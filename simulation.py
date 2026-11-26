"""Simulation & ecological modeling engine for interactive biodiversity labs."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.data import (
    CORRIDOR_SPECIES,
    CROSSING_STRUCTURES,
    ECOSYSTEMS,
    INFRASTRUCTURE_PROJECTS,
    NBS_INTERVENTIONS,
)


def generate_watershed_terrain(
    grid_size: int = 45,
    infra_type: str = "None",
    mitigation_level: int = 75,
) -> Dict[str, np.ndarray]:
    """Generate a 3D terrain & biodiversity-health grid across forest, river, wetland, and coast."""
    x = np.linspace(0, 10, grid_size)
    y = np.linspace(0, 10, grid_size)
    X, Y = np.meshgrid(x, y)

    # Meandering river centerline: x_river(y)
    river_x = 5.0 + 1.15 * np.sin(0.75 * Y - 0.6)
    dist_river = np.abs(X - river_x)

    # Elevation: high forest ridges on NW/NE, river valley in middle, coastal bay at SE (y < 2.2)
    ridge_nw = 2.6 * np.exp(-((X - 2.0) ** 2 + (Y - 7.6) ** 2) / 5.5)
    ridge_ne = 2.1 * np.exp(-((X - 8.2) ** 2 + (Y - 7.8) ** 2) / 6.0)
    valley_carve = 1.1 * np.exp(-(dist_river ** 2) / 0.45)
    coastal_slope = np.clip((Y - 1.3) / 2.2, 0.0, 1.0)
    Z = (0.35 + ridge_nw + ridge_ne - 0.55 * valley_carve) * coastal_slope
    Z = np.where(Y < 1.35, -0.18 + 0.08 * np.sin(X * 1.4), Z)

    # Baseline ecological richness (0-100)
    bio = 58.0 + 26.0 * np.exp(-((X - 2.2) ** 2 + (Y - 7.6) ** 2) / 6.0)
    bio += 22.0 * np.exp(-(dist_river ** 2) / 0.7)
    bio += 24.0 * np.exp(-((X - 6.4) ** 2 + (Y - 3.8) ** 2) / 2.6)
    bio += 25.0 * np.exp(-((X - 8.2) ** 2 + (Y - 1.8) ** 2) / 3.0)
    bio = np.clip(bio, 30, 98)

    # Infrastructure footprint impact field
    impact_mask = np.zeros_like(Z)
    mitigation_factor = 1.0 - 0.78 * (mitigation_level / 100.0)

    if infra_type == "Road / Highway":
        # East-West highway across y = 5.6
        dist_road = np.abs(Y - (5.6 + 0.35 * np.sin(0.6 * X)))
        impact_mask = 52.0 * np.exp(-(dist_road ** 2) / 0.38) * mitigation_factor
    elif infra_type == "Hydroelectric Dam":
        # Dam wall across river around y = 5.4, reservoir upstream (y > 5.4)
        dam_wall = np.exp(-((Y - 5.4) ** 2) / 0.12) * np.exp(-(dist_river ** 2) / 1.5)
        reservoir = np.where(Y > 5.4, np.exp(-(dist_river ** 2) / 2.2), 0.25 * np.exp(-(dist_river ** 2) / 0.6))
        impact_mask = (58.0 * dam_wall + 38.0 * reservoir) * mitigation_factor
    elif infra_type == "High-Speed Railway":
        # Diagonal rail corridor from (1.2, 2.0) to (8.8, 8.8)
        dist_rail = np.abs(0.89 * X - 1.0 * Y + 0.9) / np.sqrt(0.89 ** 2 + 1.0)
        impact_mask = 44.0 * np.exp(-(dist_rail ** 2) / 0.25) * mitigation_factor
    elif infra_type == "Urban Development":
        # Urban cluster around (6.8, 4.2) encroaching on wetland & river
        dist_urban = (X - 6.6) ** 2 + (Y - 4.1) ** 2
        impact_mask = 62.0 * np.exp(-dist_urban / 3.2) * mitigation_factor

    post_bio = np.clip(bio - impact_mask, 5, 99)

    return {
        "x": x,
        "y": y,
        "X": X,
        "Y": Y,
        "Z": Z,
        "river_x": 5.0 + 1.15 * np.sin(0.75 * y - 0.6),
        "baseline_bio": bio,
        "post_bio": post_bio,
        "impact_mask": impact_mask,
    }


def simulate_infrastructure_impact(
    project_type: str,
    scale_pct: int,
    eia_buffer_m: int,
    green_crossings: int,
    hydro_bypass: bool,
    noise_light_shield: bool,
    wetland_avoidance: int,
) -> Dict[str, float]:
    """Compute multidimensional biodiversity and ecosystem impacts for a proposed project."""
    proj = INFRASTRUCTURE_PROJECTS[project_type]
    scale = 0.45 + 0.75 * (scale_pct / 100.0)

    # Mitigation effectiveness (0..1)
    buffer_relief = min(0.32, (eia_buffer_m / 200.0) * 0.32)
    crossing_relief = min(0.34, green_crossings * 0.085)
    hydro_relief = 0.28 if hydro_bypass else 0.0
    shield_relief = 0.22 if noise_light_shield else 0.0
    avoid_relief = (wetland_avoidance / 100.0) * 0.30

    frag_stress = proj["fragmentation_base"] * scale * (1.0 - (crossing_relief + buffer_relief * 0.6 + avoid_relief * 0.5))
    hydro_stress = proj["hydro_impact_base"] * scale * (1.0 - (hydro_relief + buffer_relief * 0.7 + avoid_relief * 0.5))
    sensory_stress = proj["noise_light_base"] * scale * (1.0 - (shield_relief + buffer_relief * 0.5))
    mortality_risk = proj["mortality_base"] * scale * (1.0 - (crossing_relief * 1.15 + shield_relief * 0.45))

    frag_stress = float(np.clip(frag_stress, 4, 98))
    hydro_stress = float(np.clip(hydro_stress, 3, 98))
    sensory_stress = float(np.clip(sensory_stress, 4, 98))
    mortality_risk = float(np.clip(mortality_risk, 3, 98))

    habitat_integrity = float(np.clip(100.0 - (0.38 * frag_stress + 0.28 * hydro_stress + 0.16 * sensory_stress + 0.18 * mortality_risk), 6, 97))
    wildlife_connectivity = float(np.clip(100.0 - (0.65 * frag_stress + 0.35 * mortality_risk) + green_crossings * 3.5, 5, 98))
    water_quality_index = float(np.clip(100.0 - hydro_stress * 0.92, 8, 98))
    biodiversity_retention = float(np.clip(0.35 * habitat_integrity + 0.35 * wildlife_connectivity + 0.30 * water_quality_index, 8, 98))

    ethical_alignment = float(
        np.clip(
            0.40 * biodiversity_retention
            + 0.25 * (100 - mortality_risk)
            + 0.20 * (wetland_avoidance)
            + 0.15 * min(100, eia_buffer_m / 1.5),
            5,
            99,
        )
    )

    return {
        "habitat_integrity": round(habitat_integrity, 1),
        "wildlife_connectivity": round(wildlife_connectivity, 1),
        "water_quality_index": round(water_quality_index, 1),
        "biodiversity_retention": round(biodiversity_retention, 1),
        "fragmentation_stress": round(frag_stress, 1),
        "hydro_stress": round(hydro_stress, 1),
        "sensory_stress": round(sensory_stress, 1),
        "mortality_risk": round(mortality_risk, 1),
        "ethical_alignment": round(ethical_alignment, 1),
    }


def simulate_corridor_performance(
    species_name: str,
    structure_name: str,
    width_m: int,
    vegetation_pct: int,
    funnel_fencing: bool,
    traffic_intensity: int,
) -> Dict[str, object]:
    """Simulate crossing permeability, roadkill reduction, and 20-year genetic diversity."""
    sp = CORRIDOR_SPECIES[species_name]
    st_info = CROSSING_STRUCTURES[structure_name]

    base_perm = st_info["base_permeability"]
    # Synergy bonus if structure matches species ecology
    match_bonus = 0.12 if sp["preferred"].split(" ")[0].lower() in structure_name.lower() else -0.08
    if structure_name == "None (Unmitigated Barrier)":
        match_bonus = 0.0

    width_factor = min(1.12, max(0.55, (width_m / sp["min_width_m"]) ** 0.45)) if st_info["type"] != "none" else 0.4
    veg_factor = 0.72 + 0.32 * (vegetation_pct / 100.0)
    fence_bonus = sp["fence_boost"] * 0.45 if (funnel_fencing and st_info["type"] != "none") else 0.0
    traffic_drag = (traffic_intensity / 100.0) * sp["noise_sensitivity"] * (0.35 if st_info["type"] == "none" else 0.14)

    permeability = float(np.clip((base_perm + match_bonus) * width_factor * veg_factor + fence_bonus - traffic_drag, 0.04, 0.97))

    # Mortality reduction %
    if st_info["type"] == "none":
        mortality_reduction = 8.0 if funnel_fencing else 0.0
    else:
        mortality_reduction = float(np.clip((permeability * 72.0) + (24.0 if funnel_fencing else 4.0), 10.0, 96.0))

    # 20-year genetic diversity retention projection
    years = np.arange(0, 21, 2)
    decay_rate = (1.0 - permeability) * 0.055
    genetic_with_corridor = 100.0 * np.exp(-decay_rate * years)
    genetic_unmitigated = 100.0 * np.exp(-0.048 * years)

    df_genetic = pd.DataFrame(
        {
            "Year": years,
            "With Designed Corridor (%)": np.round(genetic_with_corridor, 1),
            "Unmitigated Fragmentation (%)": np.round(genetic_unmitigated, 1),
        }
    )

    return {
        "permeability_pct": round(permeability * 100, 1),
        "mortality_reduction_pct": round(mortality_reduction, 1),
        "est_cost_million": round(st_info["cost_m"] * (0.7 + 0.3 * (width_m / 40.0)), 2),
        "final_genetic_pct": round(float(genetic_with_corridor[-1]), 1),
        "df_genetic": df_genetic,
        "species_match": match_bonus > 0,
    }


def simulate_biodiversity_dashboard(
    protection_target_pct: int,
    restoration_rate_pct: int,
    corridor_investment_pct: int,
    green_infra_adoption_pct: int,
) -> Dict[str, object]:
    """Compute multi-year KPIs and trajectories for the Biodiversity Assessment Dashboard."""
    years = np.arange(2025, 2041)
    t = np.arange(len(years))

    effort = (
        0.30 * protection_target_pct
        + 0.28 * restoration_rate_pct
        + 0.22 * corridor_investment_pct
        + 0.20 * green_infra_adoption_pct
    ) / 100.0

    # Baseline (Business As Usual) trajectories
    bau_habitat_loss = np.clip(18.0 + 1.9 * t, 0, 62)
    bau_connectivity = np.clip(64.0 - 2.1 * t, 18, 100)
    bau_shannon = np.clip(2.85 - 0.065 * t, 1.2, 3.6)

    # Ethical Infrastructure trajectories
    ethical_habitat_loss = np.clip(18.0 + 0.55 * t - (1.85 * effort) * t, 2.0, 55.0)
    ethical_connectivity = np.clip(64.0 + (2.3 * effort - 0.45) * t, 20.0, 97.0)
    ethical_shannon = np.clip(2.85 + (0.048 * effort - 0.015) * t, 1.5, 3.55)
    restoration_progress = np.clip(12.0 + (5.6 * effort) * t, 12.0, 96.0)

    df_traj = pd.DataFrame(
        {
            "Year": years,
            "Ethical Connectivity": np.round(ethical_connectivity, 1),
            "Business-as-Usual Connectivity": np.round(bau_connectivity, 1),
            "Ethical Habitat Loss (%)": np.round(ethical_habitat_loss, 1),
            "Business-as-Usual Habitat Loss (%)": np.round(bau_habitat_loss, 1),
            "Restoration Progress (%)": np.round(restoration_progress, 1),
            "Shannon Diversity (H')": np.round(ethical_shannon, 2),
            "BAU Shannon Diversity (H')": np.round(bau_shannon, 2),
        }
    )

    # Ecosystem health breakdown by biome
    biome_rows = []
    for name, info in ECOSYSTEMS.items():
        base_r = info["species_richness"]
        frag = info["fragility"]
        projected = float(np.clip(base_r * (0.72 + 0.34 * effort) - frag * (1.0 - effort) * 18.0, 28, 99))
        biome_rows.append(
            {
                "Ecosystem": name.split(" & ")[0],
                "Baseline": base_r,
                "Projected 2040": round(projected, 1),
                "Carbon Score": info["carbon_density"],
            }
        )

    return {
        "habitat_loss_2040": round(float(ethical_habitat_loss[-1]), 1),
        "bau_habitat_loss_2040": round(float(bau_habitat_loss[-1]), 1),
        "shannon_2040": round(float(ethical_shannon[-1]), 2),
        "connectivity_2040": round(float(ethical_connectivity[-1]), 1),
        "restoration_2040": round(float(restoration_progress[-1]), 1),
        "df_traj": df_traj,
        "df_biomes": pd.DataFrame(biome_rows),
    }


def simulate_nbs_studio(selected_ids: List[str], density_factor: int) -> Dict[str, object]:
    """Aggregate Nature-Based Solutions metrics for the Sustainable Infrastructure Design Studio."""
    scale = 0.6 + 0.6 * (density_factor / 100.0)
    bio_gain = 0.0
    stormwater = 0.0
    cooling = 0.0
    carbon = 0.0
    cost = 0.0
    chosen = []

    for item in NBS_INTERVENTIONS:
        if item["id"] in selected_ids:
            chosen.append(item)
            bio_gain += item["biodiversity_gain"] * scale
            stormwater += item["stormwater_pct"] * scale
            cooling += item["cooling_c"] * scale
            carbon += item["carbon_t"] * scale
            cost += item["cost_index"] * (0.8 + 0.25 * (density_factor / 100.0))

    return {
        "biodiversity_uplift": round(min(98.0, bio_gain), 1),
        "stormwater_captured_pct": round(min(96.0, stormwater), 1),
        "urban_cooling_c": round(min(5.2, cooling), 2),
        "annual_carbon_tons": round(carbon, 0),
        "cost_index": round(cost, 1),
        "net_eco_roi": round((bio_gain + stormwater * 0.7) / max(10.0, cost) * 18.0, 1),
        "chosen": chosen,
    }
