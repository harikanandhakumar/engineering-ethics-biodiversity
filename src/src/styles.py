"""Custom nature-themed CSS, animations, and UI helper components."""

import base64
from pathlib import Path
import streamlit as st


def img_to_base64(path: str) -> str:
    """Convert a local image file to a base64 data URI string."""
    p = Path(path)
    if not p.exists():
        return ""
    suffix = p.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
    data = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:image/{mime};base64,{data}"


def inject_custom_css() -> None:
    """Inject modern environmental engineering styling and animations."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --forest-deep: #0F291E;
            --forest-mid: #1B4332;
            --forest-accent: #2D6A4F;
            --emerald-glow: #40916C;
            --sage-soft: #95D5B2;
            --river-deep: #023E8A;
            --river-blue: #0077B6;
            --river-cyan: #48CAE4;
            --earth-warm: #BC6C25;
            --earth-sand: #DDA15E;
            --earth-cream: #F7F9F5;
            --card-bg: rgba(255, 255, 255, 0.88);
            --border-soft: rgba(45, 106, 79, 0.16);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #132A1E;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(149, 213, 178, 0.24) 0%, transparent 38%),
                radial-gradient(circle at 88% 15%, rgba(72, 202, 228, 0.16) 0%, transparent 35%),
                radial-gradient(circle at 75% 88%, rgba(221, 161, 94, 0.14) 0%, transparent 40%),
                linear-gradient(180deg, #F2F7F3 0%, #EAF3ED 100%);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0E261C 0%, #163A2A 55%, #11343D 100%);
            border-right: 1px solid rgba(149, 213, 178, 0.2);
        }
        section[data-testid="stSidebar"] * {
            color: #ECF7F0 !important;
        }
        section[data-testid="stSidebar"] .stRadio label {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(149, 213, 178, 0.14);
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
            transition: all 0.22s ease;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(82, 183, 136, 0.18);
            border-color: rgba(149, 213, 178, 0.45);
            transform: translateX(3px);
        }

        /* Hero Banner */
        .hero-container {
            position: relative;
            border-radius: 22px;
            overflow: hidden;
            padding: 2.1rem 2.3rem;
            margin-bottom: 1.35rem;
            color: #FFFFFF;
            box-shadow: 0 18px 45px rgba(15, 41, 30, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.22);
            background-size: cover;
            background-position: center;
        }
        .hero-overlay {
            position: relative;
            z-index: 2;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(15, 41, 30, 0.68);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(149, 213, 178, 0.45);
            color: #B7E4C7;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #52B788;
            box-shadow: 0 0 0 0 rgba(82, 183, 136, 0.8);
            animation: ecoPulse 2s infinite;
        }
        @keyframes ecoPulse {
            0% { box-shadow: 0 0 0 0 rgba(82, 183, 136, 0.8); }
            70% { box-shadow: 0 0 0 10px rgba(82, 183, 136, 0); }
            100% { box-shadow: 0 0 0 0 rgba(82, 183, 136, 0); }
        }
        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(1.55rem, 2.6vw, 2.35rem);
            font-weight: 800;
            line-height: 1.15;
            margin: 0 0 0.55rem 0;
            color: #FFFFFF;
            text-shadow: 0 2px 14px rgba(0, 0, 0, 0.45);
        }
        .hero-sub {
            font-size: 0.98rem;
            line-height: 1.5;
            color: #E7F5EC;
            max-width: 780px;
            margin: 0;
            text-shadow: 0 1px 8px rgba(0, 0, 0, 0.5);
        }

        /* Section Header Banner */
        .section-banner {
            background: linear-gradient(125deg, #123123 0%, #1D4E3B 55%, #0F4C6C 100%);
            border-radius: 18px;
            padding: 1.25rem 1.6rem;
            color: #FFFFFF;
            margin-bottom: 1.1rem;
            box-shadow: 0 10px 28px rgba(18, 49, 35, 0.14);
            border: 1px solid rgba(149, 213, 178, 0.25);
            position: relative;
            overflow: hidden;
        }
        .section-banner::after {
            content: "";
            position: absolute;
            right: -40px;
            top: -40px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(72, 202, 228, 0.22) 0%, transparent 70%);
            pointer-events: none;
        }
        .section-kicker {
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #95D5B2;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .section-heading {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.48rem;
            font-weight: 700;
            margin: 0 0 0.25rem 0;
            color: #FFFFFF;
        }
        .section-desc {
            font-size: 0.92rem;
            color: #DDF2E5;
            margin: 0;
        }

        /* Glass Eco Cards */
        .eco-card {
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.15rem 1.25rem;
            border: 1px solid var(--border-soft);
            box-shadow: 0 8px 24px rgba(20, 43, 30, 0.06);
            transition: transform 0.22s ease, box-shadow 0.22s ease;
            margin-bottom: 0.85rem;
        }
        .eco-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 30px rgba(20, 43, 30, 0.10);
        }

        /* Metric Pills */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.8rem;
            margin: 0.6rem 0 1rem 0;
        }
        .kpi-box {
            background: rgba(255, 255, 255, 0.92);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            border-left: 4px solid #2D6A4F;
            box-shadow: 0 5px 16px rgba(15, 41, 30, 0.06);
        }
        .kpi-box.blue { border-left-color: #0077B6; }
        .kpi-box.earth { border-left-color: #BC6C25; }
        .kpi-box.alert { border-left-color: #C1121F; }
        .kpi-label {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #4A6B58;
            margin-bottom: 0.2rem;
        }
        .kpi-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.45rem;
            font-weight: 800;
            color: #132A1E;
        }
        .kpi-sub {
            font-size: 0.78rem;
            color: #52796F;
            margin-top: 0.1rem;
        }

        /* Tag Badges */
        .eco-tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 5px;
            background: #D8F3DC;
            color: #1B4332;
            border: 1px solid rgba(45, 106, 79, 0.2);
        }
        .eco-tag.blue {
            background: #CAF0F8;
            color: #023E8A;
            border-color: rgba(0, 119, 182, 0.2);
        }
        .eco-tag.earth {
            background: #FAEDCD;
            color: #7F4F24;
            border-color: rgba(188, 108, 37, 0.25);
        }
        .eco-tag.warn {
            background: #FFE5E5;
            color: #9B2226;
            border-color: rgba(193, 18, 31, 0.25);
        }

        /* Streamlit native elements polish */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(45, 106, 79, 0.16);
            padding: 0.85rem 1rem;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(15, 41, 30, 0.05);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255, 255, 255, 0.6);
            padding: 6px;
            border-radius: 14px;
            border: 1px solid rgba(45, 106, 79, 0.12);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background: #2D6A4F !important;
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
            border: none;
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(image_path: str) -> None:
    """Render the animated hero header with nature backdrop."""
    b64 = img_to_base64(image_path)
    bg_css = (
        f"background-image: linear-gradient(110deg, rgba(11, 34, 24, 0.86) 0%, rgba(18, 57, 41, 0.72) 52%, rgba(9, 58, 82, 0.68) 100%), url('{b64}');"
        if b64
        else "background: linear-gradient(120deg, #0E2A1E 0%, #1B4332 55%, #005F73 100%);"
    )
    st.markdown(
        f"""
        <div class="hero-container" style="{bg_css}">
            <div class="hero-overlay">
                <div class="hero-badge">
                    <span class="pulse-dot"></span>
                    Interactive Environmental Engineering Simulation Lab
                </div>
                <h1 class="hero-title">Engineering Ethics in Ensuring Biodiversity Are Included in Infrastructure Decision Making</h1>
                <p class="hero-sub">
                    Simulate real-world ecosystems, test roads, dams, railways &amp; urban blueprints, design wildlife corridors,
                    and evaluate ethical trade-offs for thriving human &amp; ecological futures.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_banner(kicker: str, title: str, subtitle: str) -> None:
    """Render a crisp visual header for each interactive module."""
    st.markdown(
        f"""
        <div class="section-banner">
            <div class="section-kicker">{kicker}</div>
            <div class="section-heading">{title}</div>
            <p class="section-desc">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
