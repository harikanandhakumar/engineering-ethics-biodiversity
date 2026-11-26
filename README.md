# Engineering Ethics in Ensuring Biodiversity Are Included in Infrastructure Decision Making

An interactive, simulation-driven environmental engineering web application built with **Streamlit**, **Plotly 3D**, **PyDeck**, and **HTML5 Canvas** to explore how ethical infrastructure planning protects ecosystems, wildlife connectivity, and future generations.

## Interactive Modules

1. **Interactive Biodiversity Map** — Orbit a 3D WebGL watershed terrain or 3D geospatial PyDeck view covering old-growth forests, rivers, floodplains, coastal mangroves, and migration ridges with live infrastructure overlays.
2. **Infrastructure Impact Simulator** — Model Roads/Highways, Hydroelectric Dams, High-Speed Railways, and Urban Developments with adjustable EIA buffers, crossings, fishways, and acoustic/dark-sky shielding.
3. **Ethical Decision-Making Lab** — Inspect multi-stakeholder lenses (Ecologist, Civil Engineer, Local Community, Future Generations) and test ethical vs. harmful engineering choices.
4. **Wildlife Corridor Designer** — Run a real-time animated agent simulation of animals navigating green overpasses, underpasses, canopy bridges, and nature-like fishways alongside 20-year genetic diversity curves.
5. **Biodiversity Assessment Dashboard** — Track 2025–2040 habitat loss prevention, Shannon-Wiener diversity (`H'`), connectivity, restoration progress, and a 3D ecological resilience surface.
6. **Sustainable Infrastructure Design Studio** — Assemble Nature-Based Solutions (bioswales, living green roofs, permeable pavement, riparian restoration, living seawalls, dark-sky LEDs) on an animated engineering cross-section.
7. **Engineering Ethics Challenge** — Test applied judgment across 5 realistic scenarios with instant pillar-based feedback on Biodiversity Protection, Environmental Responsibility, and Intergenerational Equity.

## Project Structure

```text
Engineering_Ethics_Biodiversity/
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── coastal_ecosystem.jpg
│   ├── forest_wildlife.jpg
│   ├── hero_ecosystem.jpg
│   ├── wetland_river.jpg
│   └── wildlife_corridor.jpg
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── simulation.py
│   ├── styles.py
│   └── visuals.py
├── app.py
├── requirements.txt
└── README.md
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and click **New app**.
3. Select your repository, branch, and set **Main file path** to `app.py`.
4. Click **Deploy** — all assets and dependencies (`requirements.txt`, `.streamlit/config.toml`) are self-contained.
