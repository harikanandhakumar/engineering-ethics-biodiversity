"""Engineering Ethics in Ensuring Biodiversity Are Included in Infrastructure Decision Making."""

from pathlib import Path
import plotly.express as px
import streamlit as st

from src.data import (
    CORRIDOR_SPECIES,
    CROSSING_STRUCTURES,
    ECOSYSTEMS,
    ETHICS_DILEMMAS,
    ETHICS_QUIZ,
    INFRASTRUCTURE_PROJECTS,
    NBS_INTERVENTIONS,
)
from src.simulation import (
    generate_watershed_terrain,
    simulate_biodiversity_dashboard,
    simulate_corridor_performance,
    simulate_infrastructure_impact,
    simulate_nbs_studio,
)
from src.styles import inject_custom_css, render_hero, render_section_banner
from src.visuals import (
    build_3d_biodiversity_map,
    build_dashboard_charts,
    build_ethics_comparison_chart,
    build_impact_charts,
    build_pydeck_ecosystem_map,
    build_stressor_bars,
    render_corridor_canvas_simulation,
    render_nbs_blueprint_canvas,
)

st.set_page_config(
    page_title="Engineering Ethics & Biodiversity Simulation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

SECTIONS = [
    "1. Interactive Biodiversity Map",
    "2. Infrastructure Impact Simulator",
    "3. Ethical Decision-Making Lab",
    "4. Wildlife Corridor Designer",
    "5. Biodiversity Assessment Dashboard",
    "6. Sustainable Infrastructure Design Studio",
    "7. Engineering Ethics Challenge",
]

# Session State Initialization
if "active_section" not in st.session_state:
    st.session_state.active_section = SECTIONS[0]
if "ethics_choices" not in st.session_state:
    st.session_state.ethics_choices = {d["id"]: 0 for d in ETHICS_DILEMMAS}
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "sim_preset" not in st.session_state:
    st.session_state.sim_preset = "custom"


def _compute_stewardship_progress() -> tuple:
    """Compute user progress across the Ethics Lab and Ethics Challenge."""
    ethical_labs = sum(
        1 for d in ETHICS_DILEMMAS if st.session_state.ethics_choices.get(d["id"], 0) == 2
    )
    quiz_correct = sum(
        1
        for q in ETHICS_QUIZ
        if st.session_state.quiz_answers.get(q["id"]) == q["correct_idx"]
    )
    total_pts = ethical_labs + quiz_correct
    max_pts = len(ETHICS_DILEMMAS) + len(ETHICS_QUIZ)
    return ethical_labs, quiz_correct, int(round((total_pts / max_pts) * 100))


# Sidebar Navigation & Live Stewardship Score
with st.sidebar:
    st.markdown("## 🌿 Eco-Ethics Studio")
    st.caption("Interactive Engineering & Biodiversity Lab")
    selected_nav = st.radio(
        "Navigate Modules",
        SECTIONS,
        index=SECTIONS.index(st.session_state.active_section),
        label_visibility="collapsed",
    )
    st.session_state.active_section = selected_nav

    st.divider()
    labs_done, quiz_done, eco_pct = _compute_stewardship_progress()
    st.markdown("### 🧭 Stewardship Index")
    st.progress(eco_pct / 100.0)
    st.caption(
        f"**{eco_pct}%** Ecological Alignment  \n"
        f"• Ethics Lab Best Choices: **{labs_done}/{len(ETHICS_DILEMMAS)}**  \n"
        f"• Challenge Correct: **{quiz_done}/{len(ETHICS_QUIZ)}**"
    )
    st.divider()
    st.markdown(
        "**Core Principles**  \n"
        "• Precautionary Design  \n"
        "• Habitat Connectivity  \n"
        "• Intergenerational Equity"
    )

# Hero Header
render_hero("assets/hero_ecosystem.jpg")

# Quick Top Module Pills
pill_cols = st.columns(len(SECTIONS))
for idx, sec in enumerate(SECTIONS):
    short_label = sec.split(". ")[1].replace("Interactive ", "").replace("Sustainable ", "").replace("Engineering ", "")
    btn_type = "primary" if st.session_state.active_section == sec else "secondary"
    if pill_cols[idx].button(f"{idx + 1}. {short_label}", key=f"pill_{idx}", use_container_width=True, type=btn_type):
        st.session_state.active_section = sec
        st.rerun()

active = st.session_state.active_section

# ==============================================================================
# SECTION 1: INTERACTIVE BIODIVERSITY MAP
# ==============================================================================
if active == SECTIONS[0]:
    render_section_banner(
        "Module 01 • Spatial Ecology Explorer",
        "Interactive Biodiversity Map",
        "Inspect forest, river, wetland, coastal, and wildlife corridors in 3D. Overlay proposed infrastructure to visualize spatial impacts.",
    )

    c1, c2, c3, c4 = st.columns([1.4, 1.3, 1.2, 1.0])
    with c1:
        sel_eco = st.selectbox("Focus Ecosystem", list(ECOSYSTEMS.keys()))
    with c2:
        map_infra = st.selectbox(
            "Overlay Proposed Infrastructure",
            ["None", "Road / Highway", "Hydroelectric Dam", "High-Speed Railway", "Urban Development"],
        )
    with c3:
        map_mitigation = st.slider("Ecological Mitigation (%)", 0, 100, 65)
    with c4:
        map_mode = st.radio("Map Engine", ["3D Terrain WebGL", "3D Geospatial Map"], horizontal=False)

    show_corridors = st.checkbox("Show Primary Wildlife Migration Corridors", value=True)

    col_map, col_info = st.columns([1.65, 1.0])
    with col_map:
        terrain = generate_watershed_terrain(grid_size=44, infra_type=map_infra, mitigation_level=map_mitigation)
        if map_mode == "3D Terrain WebGL":
            fig_3d_map = build_3d_biodiversity_map(terrain, sel_eco, map_infra, show_corridors=show_corridors)
            st.plotly_chart(fig_3d_map, use_container_width=True)
            st.caption("Tip: Drag to orbit in 3D, scroll to zoom, and hover over ridges, rivers, or ecosystem pins.")
        else:
            st.pydeck_chart(build_pydeck_ecosystem_map(map_infra), use_container_width=True)
            st.caption("3D Geospatial column heights represent Species Richness; arcs trace ecological connectivity.")

    with col_info:
        eco = ECOSYSTEMS[sel_eco]
        if Path(eco["image"]).exists():
            st.image(eco["image"], use_container_width=True)

        avg_post = float(terrain["post_bio"].mean())
        avg_base = float(terrain["baseline_bio"].mean())
        delta_bio = avg_post - avg_base

        st.markdown(f"#### {sel_eco}")
        m1, m2 = st.columns(2)
        m1.metric("Species Richness", f"{eco['species_richness']}/100")
        m2.metric("Watershed Health", f"{avg_post:.1f}/100", f"{delta_bio:+.1f}" if map_infra != "None" else "Baseline")

        species_tags = "".join(f"<span class='eco-tag'>{sp}</span>" for sp in eco["key_species"])
        service_tags = "".join(f"<span class='eco-tag blue'>{sv}</span>" for sv in eco["ecosystem_services"])
        st.markdown(f"**Indicator Species:**<br>{species_tags}", unsafe_allow_html=True)
        st.markdown(f"**Ecosystem Services:**<br>{service_tags}", unsafe_allow_html=True)

        if map_infra != "None":
            st.warning(f"**{map_infra} Impact:** {eco['impacts'][map_infra]}")
        st.success(f"**Ethical Engineering Guidance:** {eco['mitigation_tip']}")

# ==============================================================================
# SECTION 2: INFRASTRUCTURE IMPACT SIMULATOR
# ==============================================================================
elif active == SECTIONS[1]:
    render_section_banner(
        "Module 02 • Environmental Engineering Modeling",
        "Infrastructure Impact Simulator",
        "Configure project type, scale, buffers, and wildlife safeguards to observe real-time biodiversity and hydrological outcomes.",
    )

    col_ctrl, col_viz = st.columns([1.0, 1.55])
    with col_ctrl:
        st.markdown("### Project Configuration")
        proj_type = st.selectbox("Infrastructure Type", list(INFRASTRUCTURE_PROJECTS.keys()))
        proj_meta = INFRASTRUCTURE_PROJECTS[proj_type]
        st.info(f"{proj_meta['icon']} **{proj_type}:** {proj_meta['summary']}")

        p1, p2 = st.columns(2)
        if p1.button("🌿 Apply Ethical Best-Practice", use_container_width=True):
            st.session_state["sim_scale"] = 55
            st.session_state["sim_buffer"] = 160
            st.session_state["sim_crossings"] = 4
            st.session_state["sim_hydro"] = True
            st.session_state["sim_shield"] = True
            st.session_state["sim_wetland"] = 95
        if p2.button("⚠️ Unmitigated Baseline", use_container_width=True):
            st.session_state["sim_scale"] = 85
            st.session_state["sim_buffer"] = 10
            st.session_state["sim_crossings"] = 0
            st.session_state["sim_hydro"] = False
            st.session_state["sim_shield"] = False
            st.session_state["sim_wetland"] = 15

        scale_pct = st.slider("Project Footprint & Intensity (%)", 20, 100, st.session_state.get("sim_scale", 65), key="sim_scale")
        eia_buffer_m = st.slider("Riparian & Forest Buffer Zone (m)", 0, 200, st.session_state.get("sim_buffer", 80), key="sim_buffer")
        green_crossings = st.slider("Vegetated Wildlife Crossings", 0, 5, st.session_state.get("sim_crossings", 2), key="sim_crossings")
        wetland_avoid = st.slider("Sensitive Wetland Avoidance (%)", 0, 100, st.session_state.get("sim_wetland", 70), key="sim_wetland")
        hydro_bypass = st.checkbox("Fish Passage & Permeable Hydro-Bypass", value=st.session_state.get("sim_hydro", True), key="sim_hydro")
        noise_shield = st.checkbox("Acoustic Berms & Wildlife-Safe Amber Lighting", value=st.session_state.get("sim_shield", True), key="sim_shield")

    metrics = simulate_infrastructure_impact(
        proj_type, scale_pct, eia_buffer_m, green_crossings, hydro_bypass, noise_shield, wetland_avoid
    )

    with col_viz:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Habitat Integrity", f"{metrics['habitat_integrity']}%")
        k2.metric("Wildlife Connectivity", f"{metrics['wildlife_connectivity']}%")
        k3.metric("Water Quality Index", f"{metrics['water_quality_index']}%")
        k4.metric("Ethical Alignment", f"{metrics['ethical_alignment']}/100")

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### Ecological Health vs. Target")
            st.plotly_chart(build_impact_charts(metrics), use_container_width=True)
        with c_right:
            st.markdown("#### Residual Stressors & Risks")
            st.plotly_chart(build_stressor_bars(metrics), use_container_width=True)

        if metrics["biodiversity_retention"] >= 78:
            st.success(f"**Outcome ({metrics['biodiversity_retention']}% Biodiversity Retention):** Strong ecological safeguards keep ecosystem functions intact.")
        elif metrics["biodiversity_retention"] >= 55:
            st.warning(f"**Outcome ({metrics['biodiversity_retention']}% Biodiversity Retention):** Moderate degradation detected. Expand buffers or wildlife crossings.")
        else:
            st.error(f"**Outcome ({metrics['biodiversity_retention']}% Biodiversity Retention):** Severe ecological harm! Realign project or adopt nature-based mitigation.")

# ==============================================================================
# SECTION 3: ETHICAL DECISION-MAKING LAB
# ==============================================================================
elif active == SECTIONS[2]:
    render_section_banner(
        "Module 03 • Applied Engineering Ethics",
        "Ethical Decision-Making Lab",
        "Weigh competing stakeholder values and test how routing, hydrology, and design decisions reshape biodiversity and intergenerational fairness.",
    )

    dilemma_titles = [d["title"] for d in ETHICS_DILEMMAS]
    sel_title = st.selectbox("Choose an Engineering Dilemma", dilemma_titles)
    dilemma = next(d for d in ETHICS_DILEMMAS if d["title"] == sel_title)

    st.markdown(f"<div class='eco-card'><b>Scenario Context:</b> {dilemma['context']}</div>", unsafe_allow_html=True)

    # Interactive Stakeholder Lens
    st.markdown("#### 🔍 Stakeholder Perspectives")
    lens = st.radio("Inspect Stakeholder Viewpoint", list(dilemma["stakeholders"].keys()), horizontal=True)
    st.info(f"**{lens} Lens:** {dilemma['stakeholders'][lens]}")

    col_dec, col_res = st.columns([1.05, 1.35])
    with col_dec:
        st.markdown("#### ⚖️ Select Your Engineering Decision")
        opt_labels = [o["label"] for o in dilemma["options"]]
        current_idx = st.session_state.ethics_choices.get(dilemma["id"], 0)
        chosen_label = st.radio("Decision Alternatives", opt_labels, index=current_idx, key=f"radio_{dilemma['id']}")
        chosen_idx = opt_labels.index(chosen_label)
        st.session_state.ethics_choices[dilemma["id"]] = chosen_idx
        chosen_opt = dilemma["options"][chosen_idx]

        m_a, m_b, m_c = st.columns(3)
        m_a.metric("Habitat Loss", f"{chosen_opt['habitat_loss_pct']}%")
        m_b.metric("Connectivity", f"{chosen_opt['connectivity_pct']}%")
        m_c.metric("CapEx Index", f"{chosen_opt['cost_index']}")

        tier = chosen_opt["ethical_tier"]
        if tier == "Ethical Best Practice":
            st.success(f"**{tier}:** {chosen_opt['consequence']}")
        elif tier == "Partial Mitigation":
            st.warning(f"**{tier}:** {chosen_opt['consequence']}")
        else:
            st.error(f"**{tier}:** {chosen_opt['consequence']}")

    with col_res:
        st.markdown("#### 📊 Ethical Framework Evaluation")
        st.plotly_chart(build_ethics_comparison_chart(dilemma["options"], chosen_idx), use_container_width=True)

# ==============================================================================
# SECTION 4: WILDLIFE CORRIDOR DESIGNER
# ==============================================================================
elif active == SECTIONS[3]:
    render_section_banner(
        "Module 04 • Habitat Reconnection Studio",
        "Wildlife Corridor Designer",
        "Design green bridges, underpasses, canopy crossings, and fishways—and watch wildlife navigate your corridor in real time.",
    )

    col_cfg, col_live = st.columns([1.0, 1.75])
    with col_cfg:
        if Path("assets/wildlife_corridor.jpg").exists():
            st.image("assets/wildlife_corridor.jpg", caption="Vegetated Wildlife Overpass Concept", use_container_width=True)

        species_name = st.selectbox("Target Wildlife Guild", list(CORRIDOR_SPECIES.keys()))
        structure_name = st.selectbox("Crossing Structure Type", list(CROSSING_STRUCTURES.keys()), index=4)
        width_m = st.slider("Corridor Width (meters)", 6, 80, 50)
        veg_pct = st.slider("Native Vegetation & Cover (%)", 0, 100, 85)
        traffic_int = st.slider("Traffic / Barrier Pressure (%)", 10, 100, 60)
        funnel_fencing = st.checkbox("Install Wildlife Funnel Fencing", value=True)

    sim_c = simulate_corridor_performance(species_name, structure_name, width_m, veg_pct, funnel_fencing, traffic_int)

    with col_live:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Permeability", f"{sim_c['permeability_pct']}%")
        k2.metric("Mortality Cut", f"{sim_c['mortality_reduction_pct']}%")
        k3.metric("20-Yr Genetic Flow", f"{sim_c['final_genetic_pct']}%")
        k4.metric("Est. Build Cost", f"${sim_c['est_cost_million']}M")

        if sim_c["species_match"]:
            st.success(f"Optimal match: **{structure_name}** directly serves **{species_name}**.")
        else:
            pref = CORRIDOR_SPECIES[species_name]["preferred"]
            st.info(f"Ecological tip: **{species_name}** performs best with **{pref}**.")

        render_corridor_canvas_simulation(
            species_name,
            structure_name,
            width_m,
            veg_pct,
            funnel_fencing,
            traffic_int,
            sim_c["permeability_pct"],
        )

        df_g = sim_c["df_genetic"]
        fig_gen = px.line(
            df_g,
            x="Year",
            y=["With Designed Corridor (%)", "Unmitigated Fragmentation (%)"],
            title="20-Year Population Genetic Diversity Retention",
            color_discrete_map={
                "With Designed Corridor (%)": "#2D6A4F",
                "Unmitigated Fragmentation (%)": "#E63946",
            },
        )
        fig_gen.update_layout(
            height=265,
            margin=dict(l=15, r=15, t=40, b=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.68)",
            yaxis=dict(range=[30, 105], title="Genetic Diversity (%)"),
            legend=dict(orientation="h", y=-0.26, title=""),
        )
        st.plotly_chart(fig_gen, use_container_width=True)

# ==============================================================================
# SECTION 5: BIODIVERSITY ASSESSMENT DASHBOARD
# ==============================================================================
elif active == SECTIONS[4]:
    render_section_banner(
        "Module 05 • Ecological KPIs & 3D Resilience Analytics",
        "Biodiversity Assessment Dashboard",
        "Adjust watershed policy levers to track habitat loss prevention, Shannon species diversity, connectivity, and 2040 restoration targets.",
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        prot_pct = st.slider("Core Habitat Protection (%)", 10, 100, 75)
    with s2:
        rest_pct = st.slider("Ecological Restoration Rate (%)", 10, 100, 68)
    with s3:
        corr_pct = st.slider("Corridor Investment (%)", 10, 100, 72)
    with s4:
        green_pct = st.slider("Green Infrastructure Adoption (%)", 10, 100, 70)

    dash = simulate_biodiversity_dashboard(prot_pct, rest_pct, corr_pct, green_pct)

    m1, m2, m3, m4 = st.columns(4)
    loss_delta = round(dash["habitat_loss_2040"] - dash["bau_habitat_loss_2040"], 1)
    m1.metric("2040 Habitat Loss", f"{dash['habitat_loss_2040']}%", f"{loss_delta:+.1f}% vs BAU", delta_color="inverse")
    m2.metric("Shannon Diversity (H')", f"{dash['shannon_2040']}", "Target >= 3.0")
    m3.metric("Ecosystem Connectivity", f"{dash['connectivity_2040']}%", "Landscape Flow")
    m4.metric("Restoration Progress", f"{dash['restoration_2040']}%", "Degraded Land Healed")

    fig_traj, fig_biome, fig_3d = build_dashboard_charts(dash)
    c_left, c_right = st.columns(2)
    with c_left:
        st.plotly_chart(fig_traj, use_container_width=True)
    with c_right:
        st.plotly_chart(fig_biome, use_container_width=True)

    st.plotly_chart(fig_3d, use_container_width=True)

# ==============================================================================
# SECTION 6: SUSTAINABLE INFRASTRUCTURE DESIGN STUDIO
# ==============================================================================
elif active == SECTIONS[5]:
    render_section_banner(
        "Module 06 • Nature-Based Solutions (NbS) Workbench",
        "Sustainable Infrastructure Design Studio",
        "Assemble living roofs, bioswales, permeable pavements, riparian buffers, and living seawalls into an integrated eco-blueprint.",
    )

    col_nbs, col_stage = st.columns([1.05, 1.55])
    with col_nbs:
        st.markdown("### Select Nature-Based Solutions")
        selected_ids = []
        for item in NBS_INTERVENTIONS:
            default_on = item["id"] in ("bioswales", "green_roofs", "riparian_restore")
            checked = st.checkbox(f"**{item['name']}** ({item['category']})", value=default_on, key=f"nbs_{item['id']}")
            st.caption(item["desc"])
            if checked:
                selected_ids.append(item["id"])

        density_factor = st.slider("Deployment Coverage Density (%)", 25, 100, 80)

    nbs_out = simulate_nbs_studio(selected_ids, density_factor)

    with col_stage:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Biodiversity Uplift", f"+{nbs_out['biodiversity_uplift']}%")
        k2.metric("Stormwater Retained", f"{nbs_out['stormwater_captured_pct']}%")
        k3.metric("Cooling Effect", f"-{nbs_out['urban_cooling_c']} °C")
        k4.metric("Carbon Sequestered", f"{int(nbs_out['annual_carbon_tons'])} t/yr")

        render_nbs_blueprint_canvas(selected_ids, density_factor)

        if nbs_out["chosen"]:
            df_nbs = px.bar(
                x=[c["name"].split(" & ")[0] for c in nbs_out["chosen"]],
                y=[c["biodiversity_gain"] for c in nbs_out["chosen"]],
                color=[c["category"] for c in nbs_out["chosen"]],
                labels={"x": "Selected Solution", "y": "Biodiversity Uplift Contribution", "color": "Domain"},
                title=f"Eco-ROI Score: {nbs_out['net_eco_roi']} (Higher = Better Ecological Gain per Cost)",
                color_discrete_sequence=["#2D6A4F", "#0077B6", "#52B788", "#BC6C25"],
            )
            df_nbs.update_layout(
                height=265,
                margin=dict(l=15, r=15, t=42, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.68)",
            )
            st.plotly_chart(df_nbs, use_container_width=True)
        else:
            st.warning("Select at least one Nature-Based Solution on the left to activate the ecological blueprint.")

# ==============================================================================
# SECTION 7: ENGINEERING ETHICS CHALLENGE
# ==============================================================================
elif active == SECTIONS[6]:
    render_section_banner(
        "Module 07 • Interactive Scenario Assessment",
        "Engineering Ethics Challenge",
        "Test your engineering judgment across 5 real-world scenarios with instant feedback on biodiversity protection, responsibility, and intergenerational equity.",
    )

    answered_count = len(st.session_state.quiz_answers)
    correct_count = sum(
        1 for q in ETHICS_QUIZ if st.session_state.quiz_answers.get(q["id"]) == q["correct_idx"]
    )

    top_a, top_b, top_c = st.columns([1.2, 1.2, 0.8])
    top_a.metric("Scenarios Completed", f"{answered_count} / {len(ETHICS_QUIZ)}")
    top_b.metric("Ethical Decisions Verified", f"{correct_count} / {len(ETHICS_QUIZ)}")
    with top_c:
        if st.button("🔄 Reset Challenge", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.rerun()

    for idx, q in enumerate(ETHICS_QUIZ, start=1):
        with st.container():
            st.markdown(
                f"<div class='eco-card'><b>Scenario {idx}:</b> {q['scenario']}<br><i>{q['question']}</i></div>",
                unsafe_allow_html=True,
            )
            prev = st.session_state.quiz_answers.get(q["id"], None)
            choice = st.radio(
                f"Select response for Scenario {idx}",
                q["choices"],
                index=prev,
                key=f"quiz_radio_{q['id']}",
                label_visibility="collapsed",
            )
            if choice is not None:
                c_idx = q["choices"].index(choice)
                st.session_state.quiz_answers[q["id"]] = c_idx
                if c_idx == q["correct_idx"]:
                    st.success(f"✅ {q['feedback_correct']}")
                    p_cols = st.columns(3)
                    for p_i, (p_name, p_val) in enumerate(q["pillars"].items()):
                        p_cols[p_i].metric(p_name, f"{p_val}/100")
                else:
                    st.error(f"⚠️ {q['feedback_wrong']}")

    if len(st.session_state.quiz_answers) == len(ETHICS_QUIZ):
        pct = int(round((correct_count / len(ETHICS_QUIZ)) * 100))
        st.divider()
        if pct >= 80:
            st.balloons()
            st.success(f"🏆 **Ecological Engineering Steward ({pct}%):** Outstanding integration of biodiversity protection, professional honesty, and intergenerational equity!")
        else:
            st.info(f"🌱 **Challenge Complete ({pct}%):** Review the highlighted feedback above and refine your choices to reach 80%+ Stewardship.")
