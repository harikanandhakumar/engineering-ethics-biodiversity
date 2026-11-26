"""Interactive 3D Plotly visualizations, PyDeck maps, and live HTML5 Canvas simulations."""

from typing import Dict, List
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import streamlit.components.v1 as components

from src.data import ECOSYSTEMS


def build_3d_biodiversity_map(
    terrain: Dict[str, np.ndarray],
    selected_ecosystem: str,
    infra_type: str,
    show_corridors: bool = True,
) -> go.Figure:
    """Create an interactive 3D WebGL terrain & biodiversity map with ecosystem pins and infra overlay."""
    X = terrain["X"]
    Y = terrain["Y"]
    Z = terrain["Z"]
    post_bio = terrain["post_bio"]
    x_vec = terrain["x"]
    y_vec = terrain["y"]

    # Custom nature colorscale: deep blue water/stressed -> earth sand -> lush emerald forest
    colorscale = [
        [0.0, "#8B2635"],
        [0.25, "#DDA15E"],
        [0.5, "#74C69D"],
        [0.75, "#2D6A4F"],
        [1.0, "#1B4332"],
    ]

    fig = go.Figure()

    # Main 3D Terrain Surface colored by Biodiversity Health Index
    fig.add_trace(
        go.Surface(
            x=X,
            y=Y,
            z=Z,
            surfacecolor=post_bio,
            colorscale=colorscale,
            cmin=15,
            cmax=98,
            colorbar=dict(
                title=dict(text="Biodiversity<br>Index", font=dict(size=12, color="#132A1E")),
                thickness=14,
                len=0.65,
                x=1.02,
            ),
            lighting=dict(ambient=0.65, diffuse=0.8, specular=0.2, roughness=0.5),
            hovertemplate="X: %{x:.1f} km<br>Y: %{y:.1f} km<br>Elev: %{z:.2f} km<br>Biodiversity: %{surfacecolor:.1f}/100<extra></extra>",
            name="Watershed Terrain",
        )
    )

    # Meandering River Line on Surface
    rx = terrain["river_x"]
    ry = y_vec
    rz = np.interp(ry, y_vec, np.diag(Z)) * 0.0 + 0.12
    # Sample exact terrain height along river
    river_z = []
    for yi, xi in zip(ry, rx):
        ix = int(np.clip(round(xi / 10.0 * (len(x_vec) - 1)), 0, len(x_vec) - 1))
        iy = int(np.clip(round(yi / 10.0 * (len(y_vec) - 1)), 0, len(y_vec) - 1))
        river_z.append(float(Z[iy, ix]) + 0.06)

    fig.add_trace(
        go.Scatter3d(
            x=rx,
            y=ry,
            z=river_z,
            mode="lines",
            line=dict(color="#00B4D8", width=9),
            name="River Corridor",
            hoverinfo="name",
        )
    )

    # Wildlife Migration Arcs
    if show_corridors:
        t = np.linspace(0, 1, 30)
        arc_x = 2.2 + (4.6 - 2.2) * t
        arc_y = 7.6 + (7.2 - 7.6) * t
        arc_z = 2.2 + 0.55 * np.sin(np.pi * t)
        fig.add_trace(
            go.Scatter3d(
                x=arc_x,
                y=arc_y,
                z=arc_z,
                mode="lines",
                line=dict(color="#FFD166", width=6, dash="dash"),
                name="Primary Wildlife Migration Route",
            )
        )
        arc2_x = 4.6 + (6.4 - 4.6) * t
        arc2_y = 7.2 + (3.8 - 7.2) * t
        arc2_z = 1.9 - 1.1 * t + 0.5 * np.sin(np.pi * t)
        fig.add_trace(
            go.Scatter3d(
                x=arc2_x,
                y=arc2_y,
                z=arc2_z,
                mode="lines",
                line=dict(color="#FFB703", width=5, dash="dot"),
                name="Forest-to-Wetland Bio-Corridor",
            )
        )

    # Infrastructure Overlay Vector
    if infra_type == "Road / Highway":
        hx = np.linspace(0.4, 9.6, 40)
        hy = 5.6 + 0.35 * np.sin(0.6 * hx)
        hz = [
            float(Z[int(np.clip(round(yi / 10.0 * (len(y_vec) - 1)), 0, len(y_vec) - 1)),
                    int(np.clip(round(xi / 10.0 * (len(x_vec) - 1)), 0, len(x_vec) - 1))]) + 0.14
            for xi, yi in zip(hx, hy)
        ]
        fig.add_trace(
            go.Scatter3d(
                x=hx, y=hy, z=hz, mode="lines",
                line=dict(color="#E63946", width=10),
                name="Proposed Highway Alignment",
            )
        )
    elif infra_type == "Hydroelectric Dam":
        dx = np.linspace(4.2, 6.2, 15)
        dy = np.full_like(dx, 5.4)
        dz = np.full_like(dx, 1.35)
        fig.add_trace(
            go.Scatter3d(
                x=dx, y=dy, z=dz, mode="lines+markers",
                line=dict(color="#E63946", width=12),
                marker=dict(size=5, color="#FFFFFF"),
                name="Proposed Dam Barrier",
            )
        )
    elif infra_type == "High-Speed Railway":
        rx_l = np.linspace(1.2, 8.8, 35)
        ry_l = 0.89 * rx_l + 0.9
        rz_l = [
            float(Z[int(np.clip(round(yi / 10.0 * (len(y_vec) - 1)), 0, len(y_vec) - 1)),
                    int(np.clip(round(xi / 10.0 * (len(x_vec) - 1)), 0, len(x_vec) - 1))]) + 0.16
            for xi, yi in zip(rx_l, ry_l)
        ]
        fig.add_trace(
            go.Scatter3d(
                x=rx_l, y=ry_l, z=rz_l, mode="lines",
                line=dict(color="#D62828", width=8),
                name="Proposed High-Speed Rail",
            )
        )
    elif infra_type == "Urban Development":
        theta = np.linspace(0, 2 * np.pi, 30)
        ux = 6.6 + 1.35 * np.cos(theta)
        uy = 4.1 + 1.35 * np.sin(theta)
        uz = np.full_like(ux, 0.78)
        fig.add_trace(
            go.Scatter3d(
                x=ux, y=uy, z=uz, mode="lines",
                line=dict(color="#E63946", width=9),
                name="Proposed Urban Footprint",
            )
        )

    # Ecosystem Interactive Markers
    ex_x, ex_y, ex_z, ex_text, ex_sizes, ex_colors = [], [], [], [], [], []
    for name, info in ECOSYSTEMS.items():
        px, py = info["zone_xy"]
        ix = int(np.clip(round(px / 10.0 * (len(x_vec) - 1)), 0, len(x_vec) - 1))
        iy = int(np.clip(round(py / 10.0 * (len(y_vec) - 1)), 0, len(y_vec) - 1))
        pz = float(Z[iy, ix]) + 0.48
        is_sel = name == selected_ecosystem
        ex_x.append(px)
        ex_y.append(py)
        ex_z.append(pz)
        ex_text.append(f"<b>{name}</b><br>Richness: {info['species_richness']}/100")
        ex_sizes.append(16 if is_sel else 10)
        ex_colors.append("#FFD166" if is_sel else "#FFFFFF")

    fig.add_trace(
        go.Scatter3d(
            x=ex_x,
            y=ex_y,
            z=ex_z,
            mode="markers+text",
            text=[n.split(" ")[0] for n in ECOSYSTEMS.keys()],
            textposition="top center",
            textfont=dict(size=11, color="#0F291E"),
            marker=dict(
                size=ex_sizes,
                color=ex_colors,
                line=dict(width=3, color="#1B4332"),
                symbol="diamond",
            ),
            hovertext=ex_text,
            hoverinfo="text",
            name="Key Ecosystems",
        )
    )

    fig.update_layout(
        height=540,
        margin=dict(l=0, r=0, t=25, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0.0,
            bgcolor="rgba(255,255,255,0.8)",
            font=dict(size=11, color="#132A1E"),
        ),
        scene=dict(
            xaxis=dict(title="East-West (km)", backgroundcolor="#EAF4EE", gridcolor="#CBE3D3"),
            yaxis=dict(title="South-North (km)", backgroundcolor="#EAF4EE", gridcolor="#CBE3D3"),
            zaxis=dict(title="Elevation (km)", backgroundcolor="#E2EFF5", gridcolor="#C7DFEC", range=[-0.4, 3.2]),
            camera=dict(eye=dict(x=1.45, y=-1.55, z=1.05)),
            aspectratio=dict(x=1.15, y=1.15, z=0.58),
        ),
    )
    return fig


def build_pydeck_ecosystem_map(infra_type: str) -> pdk.Deck:
    """Build a 3D geospatial PyDeck column & arc map using Carto token-free tiles."""
    rows = []
    for name, info in ECOSYSTEMS.items():
        lat, lon = info["coords"]
        rows.append(
            {
                "name": name,
                "lat": lat,
                "lon": lon,
                "richness": info["species_richness"] * 38,
                "species": ", ".join(info["key_species"][:2]),
                "color": [45, 106, 79, 210] if info["key"] in ("forest", "wildlife") else [0, 119, 182, 210],
            }
        )
    df_pts = pd.DataFrame(rows)

    arcs_df = pd.DataFrame(
        [
            {
                "src_lon": ECOSYSTEMS["Old-Growth Temperate Forest"]["coords"][1],
                "src_lat": ECOSYSTEMS["Old-Growth Temperate Forest"]["coords"][0],
                "dst_lon": ECOSYSTEMS["Wildlife Migration Ridge & Meadow"]["coords"][1],
                "dst_lat": ECOSYSTEMS["Wildlife Migration Ridge & Meadow"]["coords"][0],
                "label": "Forest-Ridge Corridor",
            },
            {
                "src_lon": ECOSYSTEMS["Meandering River & Riparian Basin"]["coords"][1],
                "src_lat": ECOSYSTEMS["Meandering River & Riparian Basin"]["coords"][0],
                "dst_lon": ECOSYSTEMS["Freshwater Floodplain Wetland"]["coords"][1],
                "dst_lat": ECOSYSTEMS["Freshwater Floodplain Wetland"]["coords"][0],
                "label": "Riparian-Wetland Link",
            },
            {
                "src_lon": ECOSYSTEMS["Freshwater Floodplain Wetland"]["coords"][1],
                "src_lat": ECOSYSTEMS["Freshwater Floodplain Wetland"]["coords"][0],
                "dst_lon": ECOSYSTEMS["Coastal Mangrove & Estuary"]["coords"][1],
                "dst_lat": ECOSYSTEMS["Coastal Mangrove & Estuary"]["coords"][0],
                "label": "Estuary Flow Link",
            },
        ]
    )

    col_layer = pdk.Layer(
        "ColumnLayer",
        data=df_pts,
        get_position="[lon, lat]",
        get_elevation="richness",
        elevation_scale=1,
        radius=1600,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arcs_df,
        get_source_position="[src_lon, src_lat]",
        get_target_position="[dst_lon, dst_lat]",
        get_source_color=[255, 209, 102, 220],
        get_target_color=[82, 183, 136, 220],
        get_width=5,
    )

    layers = [col_layer, arc_layer]

    if infra_type != "None":
        infra_df = pd.DataFrame(
            [
                {
                    "name": f"Proposed {infra_type}",
                    "lat": 44.565,
                    "lon": -121.745,
                    "impact": 2900,
                }
            ]
        )
        layers.append(
            pdk.Layer(
                "ColumnLayer",
                data=infra_df,
                get_position="[lon, lat]",
                get_elevation="impact",
                radius=1900,
                get_fill_color=[230, 57, 70, 185],
                pickable=True,
            )
        )

    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=44.56, longitude=-121.75, zoom=10.6, pitch=50, bearing=-15),
        map_provider="carto",
        map_style="light",
        tooltip={"text": "{name}\nIndicator Species: {species}"},
    )


def build_impact_charts(metrics: Dict[str, float]) -> go.Figure:
    """Create dual-panel interactive Plotly radar for Ecosystem Health vs Stressors."""
    categories = [
        "Habitat Integrity",
        "Wildlife Connectivity",
        "Water Quality",
        "Biodiversity Retention",
        "Ethical Alignment",
    ]
    values = [
        metrics["habitat_integrity"],
        metrics["wildlife_connectivity"],
        metrics["water_quality_index"],
        metrics["biodiversity_retention"],
        metrics["ethical_alignment"],
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(45, 106, 79, 0.28)",
            line=dict(color="#1B4332", width=3),
            name="Simulated Project Design",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[85, 85, 85, 85, 85, 85],
            theta=categories + [categories[0]],
            line=dict(color="#0077B6", width=2, dash="dot"),
            name="Ecological Safeguard Target (85)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(255,255,255,0.7)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#CFE2D6"),
            angularaxis=dict(gridcolor="#CFE2D6"),
        ),
        height=390,
        margin=dict(l=45, r=45, t=40, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.12, x=0.1),
    )
    return fig


def build_stressor_bars(metrics: Dict[str, float]) -> go.Figure:
    """Horizontal risk stressor bars for Infrastructure Impact Simulator."""
    labels = ["Fragmentation Stress", "Hydrological Disruption", "Noise & Light Stress", "Wildlife Mortality Risk"]
    vals = [
        metrics["fragmentation_stress"],
        metrics["hydro_stress"],
        metrics["sensory_stress"],
        metrics["mortality_risk"],
    ]
    colors = ["#E63946" if v >= 65 else "#DDA15E" if v >= 38 else "#40916C" for v in vals]

    fig = go.Figure(
        go.Bar(
            x=vals,
            y=labels,
            orientation="h",
            marker=dict(color=colors, line=dict(color="#132A1E", width=1)),
            text=[f"{v:.1f}%" for v in vals],
            textposition="outside",
        )
    )
    fig.update_layout(
        xaxis=dict(range=[0, 112], title="Ecological Risk Intensity (%)", gridcolor="#DCEAE1"),
        yaxis=dict(autorange="reversed"),
        height=320,
        margin=dict(l=10, r=25, t=25, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.65)",
    )
    return fig


def build_ethics_comparison_chart(options: List[dict], selected_idx: int) -> go.Figure:
    """Compare all 3 engineering options across ethical pillars."""
    pillars = ["Biodiversity", "Precautionary Principle", "Intergenerational Equity", "Duty of Care"]
    keys = ["biodiversity", "precautionary", "intergenerational", "duty_of_care"]
    short_names = ["Option A (Harmful)", "Option B (Partial)", "Option C (Ethical)"]
    colors = ["#D62828", "#DDA15E", "#2D6A4F"]

    fig = go.Figure()
    for i, opt in enumerate(options):
        vals = [opt["scores"][k] for k in keys]
        opacity = 1.0 if i == selected_idx else 0.42
        fig.add_trace(
            go.Bar(
                name=short_names[i] + (" [Selected]" if i == selected_idx else ""),
                x=pillars,
                y=vals,
                marker=dict(color=colors[i], opacity=opacity, line=dict(width=2 if i == selected_idx else 0, color="#0F291E")),
                text=[f"{v}" for v in vals],
                textposition="outside",
            )
        )

    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 112], title="Ethical Performance Score (/100)", gridcolor="#DCEAE1"),
        height=360,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.65)",
        legend=dict(orientation="h", y=1.12, x=0.0),
    )
    return fig


def render_corridor_canvas_simulation(
    species_name: str,
    structure_name: str,
    width_m: int,
    vegetation_pct: int,
    funnel_fencing: bool,
    traffic_intensity: int,
    permeability_pct: float,
) -> None:
    """Render an interactive live HTML5 Canvas wildlife crossing simulation."""
    is_aquatic = "Fish" in species_name or "Fishway" in structure_name
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ margin:0; font-family: 'Segoe UI', sans-serif; background: transparent; }}
      .sim-wrap {{
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(45,106,79,0.22);
        background: #0F291E;
        box-shadow: 0 10px 26px rgba(15,41,30,0.16);
      }}
      .sim-hud {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 16px;
        background: linear-gradient(90deg, #123123, #0F4C6C);
        color: #ECF7F0;
        font-size: 13px;
        font-weight: 600;
      }}
      .hud-badges span {{
        background: rgba(255,255,255,0.12);
        padding: 4px 10px;
        border-radius: 999px;
        margin-left: 8px;
      }}
      canvas {{ display: block; width: 100%; height: 320px; }}
    </style>
    </head>
    <body>
    <div class="sim-wrap">
      <div class="sim-hud">
        <div>LIVE CORRIDOR AGENT SIMULATION &bull; {species_name.split('(')[0].strip()}</div>
        <div class="hud-badges">
          <span id="crossedCount">Safe Crossings: 0</span>
          <span id="blockedCount">Blocked / Risk: 0</span>
          <span>Permeability: {permeability_pct:.1f}%</span>
        </div>
      </div>
      <canvas id="simCanvas" width="900" height="320"></canvas>
    </div>

    <script>
      const canvas = document.getElementById('simCanvas');
      const ctx = canvas.getContext('2d');
      const structure = {structure_name!r};
      const isAquatic = {str(is_aquatic).lower()};
      const widthM = {width_m};
      const vegPct = {vegetation_pct};
      const hasFence = {str(funnel_fencing).lower()};
      const traffic = {traffic_intensity};
      const perm = {permeability_pct} / 100.0;

      let safeCrossed = 0;
      let blockedRisk = 0;

      const corridorHalfH = Math.max(18, Math.min(68, widthM * 0.9));
      const corridorTop = 160 - corridorHalfH;
      const corridorBot = 160 + corridorHalfH;

      const vehicles = [];
      const numVeh = Math.max(2, Math.round(traffic / 12));
      for (let i = 0; i < numVeh; i++) {{
        vehicles.push({{
          x: 410 + (i % 2) * 44,
          y: (i * 75) % 340,
          speed: (1.5 + (traffic / 35)) * (i % 2 === 0 ? 1 : -1),
          color: i % 2 === 0 ? '#E9C46A' : '#E76F51'
        }});
      }}

      const animals = [];
      for (let i = 0; i < 14; i++) {{
        animals.push({{
          x: Math.random() * 340 + 20,
          y: 25 + Math.random() * 270,
          vx: 0.9 + Math.random() * 0.9,
          vy: (Math.random() - 0.5) * 0.5,
          state: 'approaching',
          flash: 0
        }});
      }}

      function drawTree(x, y, r) {{
        ctx.fillStyle = '#1B4332';
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#40916C';
        ctx.beginPath();
        ctx.arc(x - 2, y - 2, r * 0.65, 0, Math.PI * 2);
        ctx.fill();
      }}

      function drawScene() {{
        // Left & Right habitat zones
        ctx.fillStyle = isAquatic ? '#184E77' : '#2D6A4F';
        ctx.fillRect(0, 0, 900, 320);

        // Habitat texture patches
        ctx.fillStyle = isAquatic ? 'rgba(72,202,228,0.14)' : 'rgba(149,213,178,0.16)';
        for (let i = 0; i < 18; i++) {{
          ctx.beginPath();
          ctx.arc((i * 137) % 370, (i * 89) % 300 + 10, 18, 0, Math.PI * 2);
          ctx.arc(540 + (i * 113) % 340, (i * 73) % 300 + 10, 18, 0, Math.PI * 2);
          ctx.fill();
        }}

        // Infrastructure Barrier (Road / Dam) in middle x=[390..510]
        ctx.fillStyle = isAquatic ? '#495057' : '#2B2D42';
        ctx.fillRect(390, 0, 120, 320);

        // Road lanes
        if (!isAquatic) {{
          ctx.strokeStyle = '#EDF2F4';
          ctx.setLineDash([12, 10]);
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(450, 0);
          ctx.lineTo(450, 320);
          ctx.stroke();
          ctx.setLineDash([]);
        }}

        // Vehicles / Barrier flow
        if (!isAquatic) {{
          vehicles.forEach(v => {{
            v.y += v.speed;
            if (v.y > 340) v.y = -30;
            if (v.y < -30) v.y = 340;
            // If Green Overpass, vehicles pass underneath bridge (translucent over corridor)
            ctx.globalAlpha = (structure.includes('Overpass') && v.y > corridorTop && v.y < corridorBot) ? 0.18 : 0.95;
            ctx.fillStyle = v.color;
            ctx.fillRect(v.x, v.y, 18, 28);
            ctx.globalAlpha = 1.0;
          }});
        }}

        // Exclusion fencing
        if (hasFence && !structure.includes('None')) {{
          ctx.strokeStyle = '#FFD166';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(386, 0); ctx.lineTo(386, corridorTop);
          ctx.moveTo(386, corridorBot); ctx.lineTo(386, 320);
          ctx.moveTo(514, 0); ctx.lineTo(514, corridorTop);
          ctx.moveTo(514, corridorBot); ctx.lineTo(514, 320);
          ctx.stroke();
        }}

        // Crossing Structure
        if (!structure.includes('None')) {{
          if (structure.includes('Overpass')) {{
            ctx.fillStyle = `rgba(64, 145, 108, ${{0.45 + 0.55 * (vegPct / 100)}})`;
            ctx.fillRect(378, corridorTop, 144, corridorHalfH * 2);
            ctx.strokeStyle = '#D8F3DC';
            ctx.lineWidth = 2;
            ctx.strokeRect(378, corridorTop, 144, corridorHalfH * 2);
          }} else if (structure.includes('Culvert') || structure.includes('Underpass')) {{
            ctx.fillStyle = 'rgba(0, 180, 216, 0.45)';
            ctx.fillRect(386, corridorTop, 128, corridorHalfH * 2);
            ctx.strokeStyle = '#90E0EF';
            ctx.strokeRect(386, corridorTop, 128, corridorHalfH * 2);
          }} else if (structure.includes('Canopy')) {{
            ctx.fillStyle = 'rgba(188, 108, 37, 0.78)';
            ctx.fillRect(382, 145, 136, 30);
          }} else if (structure.includes('Fishway')) {{
            ctx.fillStyle = '#00B4D8';
            ctx.fillRect(384, corridorTop, 132, corridorHalfH * 2);
            ctx.strokeStyle = '#CAF0F8';
            for (let sx = 398; sx < 508; sx += 18) {{
              ctx.beginPath(); ctx.moveTo(sx, corridorTop); ctx.lineTo(sx, corridorBot); ctx.stroke();
            }}
          }}
        }}

        // Native Trees along habitat
        for (let t = 25; t < 305; t += 46) {{
          drawTree(45 + (t % 30), t, 12);
          drawTree(845 - (t % 35), t, 12);
        }}

        // Animate Wildlife Agents
        animals.forEach(a => {{
          if (a.flash > 0) a.flash--;

          // Funneling logic toward corridor
          if (!structure.includes('None') && a.x > 290 && a.x < 392) {{
            if (a.y < corridorTop + 10) a.vy = 0.9;
            else if (a.y > corridorBot - 10) a.vy = -0.9;
            else a.vy *= 0.85;
          }}

          // Check crossing zone
          if (a.x >= 385 && a.x <= 512) {{
            const inCorridor = !structure.includes('None') && (a.y >= corridorTop && a.y <= corridorBot);
            if (!inCorridor && Math.random() > perm * 0.92) {{
              // Blocked or deterred
              a.x = 340 - Math.random() * 40;
              a.flash = 16;
              blockedRisk++;
              document.getElementById('blockedCount').innerText = 'Blocked / Risk: ' + blockedRisk;
            }}
          }}

          a.x += a.vx;
          a.y += a.vy;
          if (a.y < 16 || a.y > 304) a.vy *= -1;

          if (a.x > 885) {{
            safeCrossed++;
            document.getElementById('crossedCount').innerText = 'Safe Crossings: ' + safeCrossed;
            a.x = 12;
            a.y = 25 + Math.random() * 270;
          }}

          ctx.fillStyle = a.flash > 0 ? '#FF4D6D' : (isAquatic ? '#90E0EF' : '#FFE8D6');
          ctx.beginPath();
          ctx.arc(a.x, a.y, 5.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = '#1B4332';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }});

        requestAnimationFrame(drawScene);
      }}
      drawScene();
    </script>
    </body>
    </html>
    """
    components.html(html, height=382)


def build_dashboard_charts(dash_data: Dict[str, object]) -> tuple:
    """Build interactive multi-year trajectory, biome comparison, and 3D biodiversity niche charts."""
    df_t = dash_data["df_traj"]
    df_b = dash_data["df_biomes"]

    # 1. Trajectory Chart
    fig_traj = go.Figure()
    fig_traj.add_trace(
        go.Scatter(
            x=df_t["Year"], y=df_t["Ethical Connectivity"],
            mode="lines+markers", name="Ethical Connectivity (%)",
            line=dict(color="#2D6A4F", width=3.5),
        )
    )
    fig_traj.add_trace(
        go.Scatter(
            x=df_t["Year"], y=df_t["Business-as-Usual Connectivity"],
            mode="lines", name="BAU Connectivity (%)",
            line=dict(color="#E63946", width=2.5, dash="dash"),
        )
    )
    fig_traj.add_trace(
        go.Scatter(
            x=df_t["Year"], y=df_t["Restoration Progress (%)"],
            mode="lines+markers", name="Ecological Restoration (%)",
            line=dict(color="#0077B6", width=3),
        )
    )
    fig_traj.update_layout(
        title="Ecosystem Connectivity & Restoration Trajectory (2025–2040)",
        yaxis=dict(range=[0, 105], title="Index (%)", gridcolor="#DCEAE1"),
        xaxis=dict(title="Year"),
        height=370,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.68)",
        legend=dict(orientation="h", y=-0.22),
    )

    # 2. Biome Comparison Chart
    fig_biome = go.Figure()
    fig_biome.add_trace(
        go.Bar(
            name="Baseline Richness", x=df_b["Ecosystem"], y=df_b["Baseline"],
            marker_color="#95D5B2",
        )
    )
    fig_biome.add_trace(
        go.Bar(
            name="Projected 2040 Richness", x=df_b["Ecosystem"], y=df_b["Projected 2040"],
            marker_color="#1B4332",
        )
    )
    fig_biome.update_layout(
        title="Species Richness by Ecosystem (Baseline vs. 2040)",
        barmode="group",
        yaxis=dict(range=[0, 108], title="Richness Score (/100)", gridcolor="#DCEAE1"),
        height=370,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.68)",
        legend=dict(orientation="h", y=-0.25),
    )

    # 3. 3D Biodiversity Niche Resilience Surface
    conn_grid = np.linspace(15, 95, 25)
    rest_grid = np.linspace(10, 95, 25)
    C, R = np.meshgrid(conn_grid, rest_grid)
    shannon_surface = 1.35 + 1.15 * (C / 100.0) ** 0.75 + 0.95 * (R / 100.0) ** 0.8 + 0.25 * (C * R) / 10000.0

    fig_3d = go.Figure(
        data=[
            go.Surface(
                x=C, y=R, z=shannon_surface,
                colorscale="Viridis",
                colorbar=dict(title="Shannon H'", thickness=12),
                hovertemplate="Connectivity: %{x:.0f}%<br>Restoration: %{y:.0f}%<br>Shannon H': %{z:.2f}<extra></extra>",
            )
        ]
    )
    fig_3d.update_layout(
        title="3D Ecological Resilience Model: Connectivity × Restoration → Species Diversity (H')",
        height=430,
        margin=dict(l=0, r=0, t=42, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis_title="Connectivity (%)",
            yaxis_title="Restoration (%)",
            zaxis_title="Shannon Index (H')",
            camera=dict(eye=dict(x=1.55, y=-1.55, z=0.95)),
        ),
    )

    return fig_traj, fig_biome, fig_3d


def render_nbs_blueprint_canvas(selected_ids: List[str], density_factor: int) -> None:
    """Interactive animated HTML5 Canvas cross-section of Sustainable Infrastructure Blueprint."""
    active_js = str(selected_ids)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ margin:0; font-family: 'Segoe UI', sans-serif; }}
      .wrap {{
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(0,119,182,0.25);
        box-shadow: 0 10px 26px rgba(15,41,30,0.12);
        background: #E8F4F8;
      }}
      .bar {{
        background: linear-gradient(90deg, #1B4332, #0077B6);
        color: white;
        padding: 9px 15px;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
      }}
      canvas {{ display: block; width: 100%; height: 290px; }}
    </style>
    </head>
    <body>
    <div class="wrap">
      <div class="bar">
        <span>INTERACTIVE NATURE-BASED INFRASTRUCTURE CROSS-SECTION</span>
        <span>Active Solutions: {len(selected_ids)} / 6 &bull; Density: {density_factor}%</span>
      </div>
      <canvas id="nbsCanvas" width="900" height="290"></canvas>
    </div>
    <script>
      const canvas = document.getElementById('nbsCanvas');
      const ctx = canvas.getContext('2d');
      const active = new Set({active_js});
      const drops = Array.from({{length: 36}}, () => ({{
        x: Math.random() * 900,
        y: Math.random() * 210,
        vy: 1.8 + Math.random() * 1.4
      }}));
      const birds = Array.from({{length: 6}}, (_, i) => ({{
        x: i * 150,
        y: 35 + (i % 3) * 18,
        vx: 0.7 + (i % 2) * 0.35
      }}));

      let tick = 0;
      function frame() {{
        tick += 0.04;
        // Sky gradient (darker if dark_sky is active, cleaner blue otherwise)
        const sky = ctx.createLinearGradient(0, 0, 0, 210);
        sky.addColorStop(0, active.has('dark_sky') ? '#1D3557' : '#90E0EF');
        sky.addColorStop(1, active.has('dark_sky') ? '#457B9D' : '#CAF0F8');
        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, 900, 220);

        // Ground / Soil layer
        ctx.fillStyle = '#7F5539';
        ctx.fillRect(0, 215, 900, 75);
        ctx.fillStyle = '#52B788';
        ctx.fillRect(0, 210, 560, 8);

        // Eco-Building (x: 60..240)
        ctx.fillStyle = '#E5E5E5';
        ctx.fillRect(70, 105, 165, 105);
        ctx.fillStyle = '#457B9D';
        for (let r = 0; r < 3; r++) {{
          for (let c = 0; c < 4; c++) {{
            ctx.fillRect(88 + c * 35, 122 + r * 26, 20, 15);
          }}
        }}
        // Living Green Roof
        if (active.has('green_roofs')) {{
          ctx.fillStyle = '#2D6A4F';
          ctx.fillRect(64, 92, 177, 15);
          ctx.fillStyle = '#FFD166';
          for (let fx = 76; fx < 235; fx += 18) {{
            ctx.beginPath(); ctx.arc(fx, 90, 3.5, 0, Math.PI * 2); ctx.fill();
          }}
        }}

        // Permeable Pavement / Street (x: 265..410)
        ctx.fillStyle = active.has('permeable_pave') ? '#6C757D' : '#2B2D42';
        ctx.fillRect(265, 204, 150, 14);
        if (active.has('permeable_pave')) {{
          ctx.fillStyle = '#90E0EF';
          for (let px = 275; px < 408; px += 14) {{
            ctx.fillRect(px, 218, 4, 24);
          }}
        }}

        // Bioswale (x: 425..530)
        if (active.has('bioswales')) {{
          ctx.fillStyle = '#1B4332';
          ctx.beginPath();
          ctx.moveTo(422, 210); ctx.lineTo(445, 232); ctx.lineTo(510, 232); ctx.lineTo(532, 210);
          ctx.fill();
          ctx.fillStyle = '#74C69D';
          for (let bx = 435; bx < 520; bx += 14) {{
            ctx.fillRect(bx, 190, 4, 24);
          }}
        }}

        // Riparian Wetland & River (x: 545..760)
        ctx.fillStyle = '#0077B6';
        ctx.fillRect(560, 212, 230, 50);
        if (active.has('riparian_restore')) {{
          ctx.fillStyle = '#40916C';
          ctx.fillRect(540, 198, 40, 22);
          ctx.fillStyle = '#52B788';
          ctx.beginPath(); ctx.arc(556, 182, 18, 0, Math.PI * 2); ctx.fill();
        }}

        // Living Seawall & Oyster Reef (x: 780..900)
        ctx.fillStyle = active.has('living_seawall') ? '#4A5759' : '#ADB5BD';
        ctx.fillRect(790, 178, 110, 112);
        if (active.has('living_seawall')) {{
          ctx.fillStyle = '#2D6A4F';
          for (let sy = 190; sy < 275; sy += 20) {{
            ctx.beginPath(); ctx.arc(788, sy, 8, 0, Math.PI * 2); ctx.fill();
          }}
        }}

        // Dark-Sky Amber Streetlights
        ctx.fillStyle = '#343A40';
        ctx.fillRect(252, 145, 5, 65);
        ctx.fillStyle = active.has('dark_sky') ? '#F4A261' : '#FFFFFF';
        ctx.beginPath(); ctx.arc(255, 145, 7, 0, Math.PI * 2); ctx.fill();

        // Raindrops showing stormwater absorption
        ctx.fillStyle = 'rgba(0, 180, 216, 0.7)';
        drops.forEach(d => {{
          d.y += d.vy;
          if (d.y > 212) {{ d.y = 0; d.x = Math.random() * 900; }}
          ctx.fillRect(d.x, d.y, 2, 8);
        }});

        // Pollinators / Birds when green roofs or riparian active
        if (active.has('green_roofs') || active.has('riparian_restore')) {{
          ctx.strokeStyle = '#FFFFFF';
          ctx.lineWidth = 2;
          birds.forEach(b => {{
            b.x += b.vx;
            if (b.x > 910) b.x = -15;
            const flap = Math.sin(tick * 3 + b.x * 0.05) * 4;
            ctx.beginPath();
            ctx.moveTo(b.x - 6, b.y + flap);
            ctx.lineTo(b.x, b.y);
            ctx.lineTo(b.x + 6, b.y + flap);
            ctx.stroke();
          }});
        }}

        // Labels
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 11px Segoe UI';
        ctx.fillText('Green Roof', 112, 84);
        ctx.fillText('Permeable Zone', 292, 198);
        ctx.fillText('Bioswale', 454, 184);
        ctx.fillText('River & Riparian', 612, 240);
        ctx.fillText('Living Seawall', 804, 170);

        requestAnimationFrame(frame);
      }}
      frame();
    </script>
    </body>
    </html>
    """
    components.html(html, height=346)
