"""Thème visuel : palette sobre + CSS custom. Accent bleu doux, rouge réservé aux erreurs."""

import streamlit as st

# ----------------------------------------------------------------------------
# Palette — exposée pour référence. Les couleurs sont aussi en dur dans le CSS
# pour que Streamlit les applique correctement via `unsafe_allow_html`.
# ----------------------------------------------------------------------------

COLORS = {
    # Fonds
    "bg_primary":     "#13141A",  # dark warm, pas de pur noir
    "bg_card":        "#1C1E26",
    "bg_elevated":    "#22252F",
    # Bordures
    "border_subtle":  "#2A2D36",
    "border_default": "#353943",
    # Texte
    "text_primary":   "#E4E6EB",
    "text_secondary": "#8B8F9A",
    "text_tertiary":  "#5C6068",
    # Accent (un seul, utilisé sobrement pour les primaires)
    "accent":         "#5E9EFF",
    "accent_hover":   "#7AB3FF",
    # Statuts (réservés aux badges et alertes)
    "success":        "#4ECB8F",
    "warning":        "#E8A154",
    "danger":         "#E55F6B",
}


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

  /* Padding + largeur */
  .block-container {
    padding-top: 3rem !important;
    padding-bottom: 5rem !important;
    max-width: 780px !important;
  }

  /* Typographie — sobre */
  h1 {
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    font-size: 2.1rem !important;
    margin-bottom: 0.4rem !important;
    color: #E4E6EB !important;
  }
  h2 {
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
  }
  h3 {
    font-weight: 600 !important;
    letter-spacing: -0.005em !important;
    font-size: 1.05rem !important;
    margin-top: 1.5rem !important;
    color: #E4E6EB !important;
  }

  [data-testid="stCaption"] {
    color: #8B8F9A !important;
    font-size: 0.82rem !important;
  }

  /* Boutons — neutres par défaut, primaires en bleu doux */
  .stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.12s ease !important;
    border: 1px solid #2A2D36 !important;
    background: #1C1E26 !important;
    color: #E4E6EB !important;
  }
  .stButton > button:hover {
    background: #22252F !important;
    border-color: #353943 !important;
  }
  .stButton > button:focus:not(:active) {
    border-color: #5E9EFF !important;
    box-shadow: 0 0 0 3px rgba(94, 158, 255, 0.15) !important;
    outline: none !important;
  }
  .stButton > button[kind="primary"] {
    background: #5E9EFF !important;
    border-color: #5E9EFF !important;
    color: #0D1017 !important;
    font-weight: 600 !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #7AB3FF !important;
    border-color: #7AB3FF !important;
  }
  .stButton > button[kind="primary"]:disabled {
    background: #2A2D36 !important;
    border-color: #2A2D36 !important;
    color: #5C6068 !important;
  }

  /* Segmented control — accent discret sur l'onglet actif */
  [data-testid="stSegmentedControl"] button[aria-pressed="true"],
  [data-testid="stSegmentedControl"] button[data-selected="true"] {
    background: rgba(94, 158, 255, 0.12) !important;
    border-color: rgba(94, 158, 255, 0.4) !important;
    color: #7AB3FF !important;
  }

  /* Cards bordées */
  [data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #2A2D36 !important;
    border-radius: 10px !important;
    background: #1A1C23 !important;
  }

  /* Expanders */
  [data-testid="stExpander"] {
    border: 1px solid #2A2D36 !important;
    border-radius: 10px !important;
    background: #1A1C23 !important;
  }
  [data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: #C9CCD3 !important;
  }
  [data-testid="stExpander"] summary:hover {
    color: #E4E6EB !important;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid #2A2D36 !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    padding: 0.65rem 1rem !important;
    color: #8B8F9A !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #E4E6EB !important;
    border-bottom-color: #5E9EFF !important;
  }

  /* Chat input */
  [data-testid="stChatInput"] {
    border-radius: 10px !important;
    border: 1px solid #2A2D36 !important;
    background: #1C1E26 !important;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: #5E9EFF !important;
    box-shadow: 0 0 0 3px rgba(94, 158, 255, 0.12) !important;
  }

  /* Inline code — monochrome, pas de couleur criarde */
  code {
    background: rgba(139, 143, 154, 0.15) !important;
    color: #C9CCD3 !important;
    padding: 0.12rem 0.4rem !important;
    border-radius: 4px !important;
    font-size: 0.86em !important;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace !important;
  }

  /* Blocs de code */
  [data-testid="stCode"] pre {
    border: 1px solid #2A2D36 !important;
    border-radius: 8px !important;
    background: #0F1014 !important;
  }

  /* Dividers */
  hr, [data-testid="stDivider"] {
    border-color: #22252F !important;
    margin: 1.5rem 0 !important;
  }

  /* Alerts — couleurs sémantiques strictes */
  [data-testid="stAlert"] {
    border-radius: 8px !important;
  }

  /* Status widget */
  [data-testid="stStatusWidget"], [data-testid="stStatus"] {
    border-radius: 8px !important;
    border: 1px solid #2A2D36 !important;
    background: #1A1C23 !important;
  }

  /* Progress bar — bleu doux */
  [data-testid="stProgress"] > div > div > div > div {
    background: #5E9EFF !important;
  }

  /* Metric */
  [data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
  }
  [data-testid="stMetricLabel"] {
    color: #8B8F9A !important;
  }

  [data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
  }

  /* Badges inline — couleurs sémantiques réservées aux statuts */
  .bb-badge {
    display: inline-block;
    padding: 0.12rem 0.55rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    margin-left: 0.6rem;
    vertical-align: middle;
  }
  .bb-badge-ok {
    background: rgba(78, 203, 143, 0.1);
    color: #4ECB8F;
    border: 1px solid rgba(78, 203, 143, 0.25);
  }
  .bb-badge-warn {
    background: rgba(232, 161, 84, 0.1);
    color: #E8A154;
    border: 1px solid rgba(232, 161, 84, 0.25);
  }
  .bb-badge-stop {
    background: rgba(229, 95, 107, 0.1);
    color: #E55F6B;
    border: 1px solid rgba(229, 95, 107, 0.25);
  }

  /* Hero */
  .bb-hero {
    margin-bottom: 1.8rem;
  }
  .bb-hero-tagline {
    color: #8B8F9A;
    font-size: 0.92rem;
    margin-top: 0.2rem;
  }
</style>
"""


def injecter_styles() -> None:
    """Injecte la couche CSS custom. À appeler une fois au début de main()."""
    st.markdown(STYLES_CSS, unsafe_allow_html=True)
