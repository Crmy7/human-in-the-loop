"""Thème visuel : couleurs + CSS custom injecté dans la page Streamlit."""

import streamlit as st

STYLES_CSS = """
<style>
  /* Masquer la chrome Streamlit */
  #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
  }
  [data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
  }

  /* Padding haut/bas du bloc principal */
  .block-container {
    padding-top: 3rem !important;
    padding-bottom: 5rem !important;
    max-width: 780px !important;
  }

  /* Typographie */
  h1 {
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    font-size: 2.5rem !important;
    margin-bottom: 0.5rem !important;
  }
  h2 {
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
  }
  h3 {
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    font-size: 1.15rem !important;
    margin-top: 1.5rem !important;
  }

  [data-testid="stCaption"] {
    color: #8A8A94 !important;
    font-size: 0.82rem !important;
  }

  /* Boutons */
  .stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.12s ease !important;
    border: 1px solid #2A2A32 !important;
    background: transparent !important;
    color: #E8E8EA !important;
  }
  .stButton > button:hover {
    background: #1C1C22 !important;
    border-color: #3A3A42 !important;
  }
  .stButton > button:focus:not(:active) {
    border-color: #FF5C39 !important;
    box-shadow: 0 0 0 3px rgba(255, 92, 57, 0.15) !important;
  }
  .stButton > button[kind="primary"] {
    background: #FF5C39 !important;
    border-color: #FF5C39 !important;
    color: #0A0A0B !important;
    font-weight: 600 !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #FF7555 !important;
    border-color: #FF7555 !important;
  }
  .stButton > button[kind="primary"]:disabled {
    background: #2A2A32 !important;
    border-color: #2A2A32 !important;
    color: #6A6A74 !important;
  }

  /* Segmented control actif */
  [data-testid="stSegmentedControl"] button[aria-pressed="true"],
  [data-testid="stSegmentedControl"] button[data-selected="true"] {
    background: rgba(255, 92, 57, 0.15) !important;
    border-color: #FF5C39 !important;
    color: #FF5C39 !important;
  }

  /* Conteneurs bordés = cards */
  [data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #24242A !important;
    border-radius: 12px !important;
    background: #101014 !important;
  }

  /* Expanders */
  [data-testid="stExpander"] {
    border: 1px solid #24242A !important;
    border-radius: 10px !important;
    background: #0E0E12 !important;
  }
  [data-testid="stExpander"] summary {
    font-weight: 500 !important;
  }
  [data-testid="stExpander"] summary:hover {
    color: #FF5C39 !important;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid #24242A !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    padding: 0.65rem 1rem !important;
    color: #8A8A94 !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #E8E8EA !important;
    border-bottom-color: #FF5C39 !important;
  }

  /* Chat input */
  [data-testid="stChatInput"] {
    border-radius: 12px !important;
    border: 1px solid #2A2A32 !important;
    background: #141418 !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: #FF5C39 !important;
    box-shadow: 0 0 0 3px rgba(255, 92, 57, 0.12) !important;
  }

  /* Inline code */
  code {
    background: rgba(255, 92, 57, 0.08) !important;
    color: #FF8A6B !important;
    padding: 0.12rem 0.4rem !important;
    border-radius: 4px !important;
    font-size: 0.875em !important;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace !important;
  }

  /* Blocs de code */
  [data-testid="stCode"] pre {
    border: 1px solid #24242A !important;
    border-radius: 8px !important;
    background: #0B0B0F !important;
  }

  /* Dividers */
  hr, [data-testid="stDivider"] {
    border-color: #1F1F25 !important;
    margin: 1.5rem 0 !important;
  }

  /* Alerts */
  [data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid rgba(255, 92, 57, 0.2) !important;
  }

  /* Status widget */
  [data-testid="stStatusWidget"], [data-testid="stStatus"] {
    border-radius: 10px !important;
    border: 1px solid #24242A !important;
    background: #0E0E12 !important;
  }

  /* Progress */
  [data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #FF5C39, #FF8A6B) !important;
  }

  /* Metric */
  [data-testid="stMetricValue"] {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
  }
  [data-testid="stMetricLabel"] {
    color: #8A8A94 !important;
  }

  /* Chat messages */
  [data-testid="stChatMessage"] {
    background: #101014 !important;
    border: 1px solid #1F1F25 !important;
    border-radius: 12px !important;
  }

  [data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
  }

  /* Badges inline via HTML */
  .bb-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    margin-left: 0.5rem;
    vertical-align: middle;
  }
  .bb-badge-ok {
    background: rgba(52, 211, 153, 0.12);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.25);
  }
  .bb-badge-warn {
    background: rgba(251, 191, 36, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(251, 191, 36, 0.25);
  }
  .bb-badge-stop {
    background: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
  }

  /* Hero */
  .bb-hero {
    text-align: left;
    margin-bottom: 2rem;
  }
  .bb-hero-tagline {
    color: #8A8A94;
    font-size: 0.95rem;
    margin-top: 0.25rem;
  }
  .bb-accent {
    color: #FF5C39 !important;
    font-weight: 600;
  }
</style>
"""


def injecter_styles() -> None:
    """Injecte la couche CSS custom. À appeler une fois au début de main()."""
    st.markdown(STYLES_CSS, unsafe_allow_html=True)
