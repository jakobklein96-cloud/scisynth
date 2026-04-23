"""
SciSynth — Transdisziplinäre Forschungsexploration
"""

import streamlit as st
import arxiv
import anthropic
import json
import requests
import hashlib
import io
from pathlib import Path
from datetime import datetime

try:
    import pypdf
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False

st.set_page_config(
    page_title="SciSynth",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background: #ffffff; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f9fafb !important;
    border-right: 1px solid #e5e7eb !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-baseweb]),
[data-testid="stSidebar"] small { color: #374151 !important; }
[data-testid="stSidebar"] h3 {
    font-size: 0.68em !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #9ca3af !important;
    margin: 1.4rem 0 0.5rem !important;
}
[data-testid="stSidebar"] h2 {
    font-size: 1.05em !important;
    font-weight: 600 !important;
    color: #111827 !important;
    margin: 0 0 0.2rem !important;
}
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption { color: #9ca3af !important; font-size: 0.78em !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    font-size: 0.875em !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #0d9488 !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,0.08) !important;
}
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder { color: #9ca3af !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: #f0fdfa !important;
    border: 1px solid #99f6e4 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span { color: #0f766e !important; font-size: 0.8em !important; }
[data-testid="stSidebar"] hr { border-color: #e5e7eb !important; margin: 1rem 0 !important; }

/* Segmented nav control */
div[data-testid="stSidebar"] div[data-testid="stSegmentedControl"] {
    width: 100% !important;
}
div[data-testid="stSidebar"] div[data-testid="stSegmentedControl"] button {
    font-size: 0.78em !important;
    padding: 4px 6px !important;
    flex: 1 !important;
}

/* Sidebar button */
div[data-testid="stSidebar"] .stButton button {
    background: #111827 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.875em !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: background 0.15s !important;
    width: 100% !important;
}
div[data-testid="stSidebar"] .stButton button:hover { background: #1f2937 !important; }

/* ── Page header ── */
.page-header { border-bottom: 1px solid #f3f4f6; padding-bottom: 1.8rem; margin-bottom: 2rem; }
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2em; font-weight: 700; color: #111827;
    letter-spacing: -0.02em; margin: 0 0 0.35rem; line-height: 1.2;
}
.page-subtitle { font-size: 0.96em; color: #6b7280; margin: 0; line-height: 1.5; }
.page-accent {
    display: inline-block; width: 28px; height: 3px;
    background: #0d9488; border-radius: 2px; margin-bottom: 1rem;
}

/* ── Section title ── */
.section-title {
    font-size: 0.68em; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #9ca3af;
    margin: 2.5rem 0 0.9rem; padding-bottom: 0.6rem;
    border-bottom: 1px solid #f3f4f6;
}

/* ── Paper card ── */
.paper-card {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px 22px; margin: 8px 0;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.paper-card:hover { border-color: #d1fae5; box-shadow: 0 4px 16px rgba(0,0,0,0.05); }
.paper-title { font-size: 0.93em; font-weight: 600; color: #111827; line-height: 1.45; margin-bottom: 5px; }
.paper-meta { font-size: 0.77em; color: #9ca3af; margin-bottom: 9px; }
.paper-abstract { font-size: 0.85em; color: #4b5563; line-height: 1.7; }
.paper-link { display: inline-block; margin-top: 10px; font-size: 0.79em; color: #0d9488; font-weight: 500; text-decoration: none; }

/* ── Insight cards ── */
.idea-card   { background: #fafafa; border: 1px solid #e5e7eb; border-top: 3px solid #f59e0b; border-radius: 12px; padding: 20px 22px; margin: 8px 0; }
.bridge-card { background: #fafafa; border: 1px solid #e5e7eb; border-top: 3px solid #0d9488; border-radius: 12px; padding: 20px 22px; margin: 8px 0; }
.method-card { background: #fafafa; border: 1px solid #e5e7eb; border-top: 3px solid #6366f1; border-radius: 12px; padding: 20px 22px; margin: 8px 0; }
.card-title  { font-size: 0.95em; font-weight: 600; color: #111827; margin-bottom: 9px; line-height: 1.4; }
.card-body   { font-size: 0.86em; color: #4b5563; line-height: 1.75; }
.card-label  { font-size: 0.67em; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.1em; margin: 13px 0 4px; }

/* Deepen result box */
.deepen-box {
    background: #f8faff; border: 1px solid #dbeafe; border-radius: 10px;
    padding: 18px 22px; margin-top: 4px;
}
.deepen-question {
    font-size: 0.84em; color: #1e40af; padding: 5px 0;
    border-bottom: 1px solid #eff6ff; line-height: 1.5;
}

/* ── Tags ── */
.tag { display: inline-block; border-radius: 6px; padding: 3px 10px; font-size: 0.74em; font-weight: 500; margin: 3px 3px 3px 0; }
.tag-teal   { background: #f0fdfa; color: #0f766e; border: 1px solid #99f6e4; }
.tag-amber  { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.tag-indigo { background: #eef2ff; color: #3730a3; border: 1px solid #c7d2fe; }
.tag-gray   { background: #f9fafb; color: #374151; border: 1px solid #e5e7eb; }
.tag-type   { background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb; font-size: 0.68em; letter-spacing: 0.06em; text-transform: uppercase; }

/* ── Stats ── */
.stats-row  { display: flex; gap: 10px; margin-bottom: 1.8rem; }
.stat-box   { flex: 1; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; text-align: center; }
.stat-number{ font-size: 1.9em; font-weight: 700; color: #0d9488; line-height: 1; }
.stat-label { font-size: 0.72em; color: #9ca3af; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Pattern box ── */
.pattern-box { background: #f0fdfa; border: 1px solid #ccfbf1; border-radius: 10px; padding: 18px 22px; font-size: 0.9em; color: #134e4a; line-height: 1.75; }

/* ── Theme box ── */
.theme-box  { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 15px 17px; margin-bottom: 8px; }
.theme-disc { font-size: 0.78em; font-weight: 600; color: #111827; margin-bottom: 8px; padding-bottom: 7px; border-bottom: 1px solid #f3f4f6; text-transform: uppercase; letter-spacing: 0.05em; }
.theme-item { padding: 4px 0; border-bottom: 1px solid #f9fafb; color: #4b5563; font-size: 0.84em; line-height: 1.5; }

/* ── History cards ── */
.history-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 16px 20px; margin: 8px 0; cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.history-card:hover { border-color: #0d9488; box-shadow: 0 2px 10px rgba(13,148,136,0.08); }
.history-topic { font-size: 0.92em; font-weight: 600; color: #111827; margin-bottom: 5px; }
.history-meta  { font-size: 0.76em; color: #9ca3af; margin-bottom: 8px; }
.history-pattern { font-size: 0.82em; color: #4b5563; line-height: 1.6; }

/* ── Favorites ── */
.fav-card {
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px 22px; margin: 8px 0;
}
.fav-card-idea   { border-top: 3px solid #f59e0b; }
.fav-card-bridge { border-top: 3px solid #0d9488; }
.fav-card-paper  { border-top: 3px solid #6366f1; }
.fav-date { font-size: 0.73em; color: #9ca3af; margin-top: 10px; }

/* ── Welcome ── */
.welcome { text-align: center; padding: 70px 20px; }
.welcome-icon { font-size: 2em; color: #e5e7eb; margin-bottom: 14px; }
.welcome h3 { color: #374151; font-weight: 600; margin: 0 0 8px; font-size: 1.15em; }
.welcome p  { max-width: 460px; margin: 0 auto; line-height: 1.75; font-size: 0.88em; color: #9ca3af; }

#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Konstanten ─────────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-opus-4-5"
DATA_DIR       = Path("C:/Users/Jakob/SciSynth/data")
FAVORITES_FILE = DATA_DIR / "favorites.json"
HISTORY_FILE   = DATA_DIR / "history.json"

ARXIV_CATS: dict[str, list[str]] = {
    "Künstliche Intelligenz":     ["cs.AI", "cs.LG", "cs.NE"],
    "Neurowissenschaft":          ["q-bio.NC"],
    "Quantenphysik":              ["quant-ph"],
    "Biologie & Genomik":         ["q-bio.GN", "q-bio.BM"],
    "Biophysik":                  ["physics.bio-ph"],
    "Computational Biology":      ["q-bio.CB", "q-bio.MN"],
    "Epidemiologie":              ["q-bio.PE"],
    "Pharmakologie":              ["q-bio.QM"],
    "Chemie":                     ["q-bio.BM", "cond-mat.soft"],
    "Materialwissenschaft":       ["cond-mat.mtrl-sci", "cond-mat.soft"],
    "Astrophysik":                ["astro-ph.GA", "astro-ph.CO", "astro-ph.HE"],
    "Optik & Photonik":           ["physics.optics"],
    "Komplexe Systeme":           ["nlin.AO", "nlin.CD", "physics.soc-ph"],
    "Mathematik":                 ["math.ST", "math.DS", "math.CO"],
    "Informationstheorie":        ["cs.IT", "math.IT"],
    "Operations Research":        ["math.OC"],
    "Spieltheorie":               ["cs.GT", "econ.TH"],
    "Statistik & Data Science":   ["stat.ML", "stat.AP"],
    "Informatik":                 ["cs.CV", "cs.CL", "cs.HC", "cs.IR"],
    "Robotik":                    ["cs.RO", "eess.SY"],
    "Signalverarbeitung":         ["eess.SP", "eess.AS"],
    "Kryptographie & Sicherheit": ["cs.CR"],
    "Sprache & Linguistik":       ["cs.CL", "cs.HC"],
    "Kognitionswissenschaft":     ["cs.HC", "q-bio.NC"],
    "Soziologie & Netzwerke":     ["cs.SI", "physics.soc-ph"],
    "Ethik & KI-Gesellschaft":    ["cs.CY", "cs.AI"],
    "Musikwissenschaft":          ["cs.SD", "eess.AS"],
    "Kunst & Medien":             ["cs.CV", "cs.GR"],
    "Klimawissenschaft":          ["physics.ao-ph", "physics.geo-ph"],
    "Wirtschaft & Finanzen":      ["econ.GN", "econ.TH", "q-fin.GN"],
    "Medizin & Gesundheit":       ["q-bio.QM", "eess.IV"],
}

OPENALEX_QUERIES: dict[str, str] = {
    "Künstliche Intelligenz":       "artificial intelligence machine learning neural networks",
    "Neurowissenschaft":            "neuroscience brain cognition neural",
    "Quantenphysik":                "quantum physics mechanics entanglement",
    "Biologie & Genomik":           "genomics molecular biology genetics evolution",
    "Biophysik":                    "biophysics biological physics membrane",
    "Computational Biology":        "computational biology systems biology modeling",
    "Epidemiologie":                "epidemiology public health disease transmission",
    "Pharmakologie":                "pharmacology drug therapy clinical",
    "Chemie":                       "chemistry synthesis reaction molecular",
    "Materialwissenschaft":         "materials science nanotechnology polymers",
    "Astrophysik":                  "astrophysics astronomy cosmology dark matter",
    "Optik & Photonik":             "optics photonics laser quantum optics",
    "Komplexe Systeme":             "complex systems emergence nonlinear dynamics chaos",
    "Mathematik":                   "mathematics topology algebra geometry proof",
    "Informationstheorie":          "information theory entropy coding communication",
    "Operations Research":          "operations research optimization logistics",
    "Spieltheorie":                 "game theory Nash equilibrium strategy rational",
    "Statistik & Data Science":     "statistics Bayesian inference data analysis",
    "Informatik":                   "computer science software algorithms distributed",
    "Robotik":                      "robotics autonomous systems human-robot",
    "Signalverarbeitung":           "signal processing audio speech recognition",
    "Kryptographie & Sicherheit":   "cryptography cybersecurity privacy blockchain",
    "Sprache & Linguistik":         "linguistics language syntax semantics pragmatics",
    "Kognitionswissenschaft":       "cognitive science perception memory attention",
    "Psychologie":                  "psychology behavior cognition mental health emotion",
    "Soziologie & Netzwerke":       "sociology social networks inequality institutions",
    "Politikwissenschaft":          "political science democracy governance power",
    "Kommunikationswissenschaft":   "communication media rhetoric discourse framing",
    "Anthropologie":                "anthropology culture ethnography kinship ritual",
    "Geschichte":                   "history historiography memory colonialism empire",
    "Philosophie":                  "philosophy ethics metaphysics epistemology ontology",
    "Jura & Rechtswissenschaft":    "law legal jurisprudence rights justice international",
    "Genderstudies":                "gender studies feminist theory intersectionality identity",
    "Postkoloniale Studien":        "postcolonial theory subaltern decolonization race",
    "Kulturwissenschaften":         "cultural studies discourse power Foucault representation",
    "Erziehungswissenschaft":       "education pedagogy learning curriculum teaching",
    "Ethik & KI-Gesellschaft":      "AI ethics technology governance society bias",
    "Musikwissenschaft":            "musicology music cognition acoustics composition",
    "Kunst & Medien":               "art media visual culture digital aesthetics",
    "Architektur & Stadtplanung":   "architecture urban planning space design city",
    "Geographie":                   "geography spatial analysis place environment",
    "Klimawissenschaft":            "climate change atmosphere ocean carbon emissions",
    "Wirtschaft & Finanzen":        "economics finance market institutions behavioral",
    "Medizin & Gesundheit":         "medicine health clinical patient treatment",
    "Sportwissenschaft":            "sports science exercise physiology performance",
    "Religionswissenschaft":        "religion theology ritual belief secularism",
    "Internationale Beziehungen":   "international relations foreign policy diplomacy geopolitics",
}

DISCIPLINES = sorted(set(ARXIV_CATS) | set(OPENALEX_QUERIES))

# ── Persistenz ─────────────────────────────────────────────────────────────────
def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_favorites() -> list[dict]:
    if FAVORITES_FILE.exists():
        return json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    return []

def save_favorite(item: dict) -> None:
    _ensure_data_dir()
    favs = load_favorites()
    if not any(f["id"] == item["id"] for f in favs):
        favs.insert(0, {**item, "saved_at": datetime.now().strftime("%d.%m.%Y %H:%M")})
        FAVORITES_FILE.write_text(json.dumps(favs, ensure_ascii=False, indent=2), encoding="utf-8")
        st.session_state.favorites = favs

def remove_favorite(fav_id: str) -> None:
    _ensure_data_dir()
    favs = [f for f in load_favorites() if f["id"] != fav_id]
    FAVORITES_FILE.write_text(json.dumps(favs, ensure_ascii=False, indent=2), encoding="utf-8")
    st.session_state.favorites = favs

def is_favorite(fav_id: str) -> bool:
    return any(f["id"] == fav_id for f in st.session_state.get("favorites", []))

def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []

def save_to_history(topic: str, disciplines: list[str], year_from: int,
                    year_to: int, synthesis: dict) -> None:
    _ensure_data_dir()
    history = load_history()
    entry = {
        "id":          datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp":   datetime.now().strftime("%d.%m.%Y %H:%M"),
        "topic":       topic or "Offene Exploration",
        "disciplines": disciplines,
        "year_from":   year_from,
        "year_to":     year_to,
        "synthesis":   synthesis,
    }
    history.insert(0, entry)
    history = history[:30]
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    st.session_state.history = history

def _item_id(type_: str, title: str) -> str:
    return hashlib.md5(f"{type_}:{title}".encode()).hexdigest()[:12]

# ── Datenabruf ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_arxiv(cats: tuple[str, ...], query: str, year_from: int, year_to: int, n: int) -> list[dict]:
    client = arxiv.Client(num_retries=3, delay_seconds=1)
    cat_q  = " OR ".join(f"cat:{c}" for c in cats)
    date_q = f"submittedDate:[{year_from}01010000 TO {year_to}12312359]"
    base_q = f"({cat_q}) AND ({date_q})"
    # Relevanz-Sortierung wenn Nutzer ein Thema angegeben hat
    if query.strip():
        base_q  = f"({query.strip()}) AND {base_q}"
        sort_by = arxiv.SortCriterion.Relevance
    else:
        sort_by = arxiv.SortCriterion.SubmittedDate
    search = arxiv.Search(
        query=base_q, max_results=n,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending,
    )
    papers: list[dict] = []
    try:
        for r in client.results(search):
            papers.append({
                "title":   r.title,
                "short":   r.summary[:420] + "…" if len(r.summary) > 420 else r.summary,
                "full":    r.summary,
                "authors": ", ".join(a.name for a in r.authors[:3])
                           + (" et al." if len(r.authors) > 3 else ""),
                "date":    r.published.strftime("%b %Y"),
                "url":     r.entry_id,
                "cats":    r.categories[:2],
                "source":  "arXiv",
                "doi":     "",
                "score":   0.0,  # arXiv hat keine Zitationsdaten
            })
    except Exception:
        pass
    return papers


def _reconstruct_abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos: dict[int, str] = {}
    for word, positions in inv.items():
        for p in positions:
            pos[p] = word
    return " ".join(pos[k] for k in sorted(pos))


_HUMANITIES_DISCIPLINES = frozenset({
    "Geschichte", "Jura & Rechtswissenschaft", "Philosophie",
    "Politikwissenschaft", "Soziologie", "Kulturwissenschaften",
    "Postkoloniale Studien", "Genderstudies", "Literaturwissenschaft",
    "Religionswissenschaft", "Ethnologie & Anthropologie",
    "Medienwissenschaft", "Erziehungswissenschaft", "Kommunikationswissenschaft",
    "Internationale Beziehungen", "Wirtschaftswissenschaften",
    "Pädagogik", "Psychologie",
})
_STEM_DISCIPLINES = frozenset({
    "Künstliche Intelligenz", "Informatik", "Physik", "Chemie",
    "Biologie & Lebenswissenschaften", "Medizin & Gesundheit",
    "Ingenieurwissenschaften", "Mathematik", "Neurowissenschaften",
    "Quantencomputing", "Robotik", "Cybersecurity", "Klimawissenschaften",
    "Astronomie & Astrophysik",
})

def _quality_score(cited: int, pub_date: str, paper_type: str, discipline: str = "") -> float:
    """Disziplinspezifischer Composite-Score.
    Geisteswissenschaften: Klassiker (hohe Gesamtzitationen) wichtiger.
    STEM: Zitationsgeschwindigkeit (Aktualität) wichtiger.
    Sozialwissenschaften: ausgewogen."""
    year = int((pub_date or "2020")[:4])
    age  = max(2025 - year, 1)
    velocity   = cited / age
    peer_bonus = 1.2 if paper_type == "journal-article" else 1.0
    if discipline in _HUMANITIES_DISCIPLINES:
        cw, vw = 0.75, 0.25
    elif discipline in _STEM_DISCIPLINES:
        cw, vw = 0.20, 0.80
    else:
        cw, vw = 0.45, 0.55
    return (cw * cited + vw * velocity) * peer_bonus


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_openalex(oa_query: str, year_from: int, year_to: int,
                    n: int, peer_review_only: bool, discipline: str = "") -> list[dict]:
    try:
        filter_str = (
            f"has_abstract:true,"
            f"from_publication_date:{year_from}-01-01,"
            f"to_publication_date:{year_to}-12-31"
        )
        if peer_review_only:
            filter_str += ",type:journal-article"

        # Sortierung und Poolgröße disziplinabhängig:
        # Geisteswissenschaften → Zitationen (Klassiker), STEM → Datum (Aktualität)
        if discipline in _HUMANITIES_DISCIPLINES:
            oa_sort   = "cited_by_count:desc"
            pool_size = min(max(n * 4, 25), 50)
        elif discipline in _STEM_DISCIPLINES:
            oa_sort   = "publication_date:desc"
            pool_size = min(n * 2, 50)
        else:
            oa_sort   = "cited_by_count:desc"
            pool_size = min(max(n * 3, 20), 50)

        resp = requests.get(
            "https://api.openalex.org/works",
            params={
                "search":   oa_query,
                "filter":   filter_str,
                "sort":     oa_sort,
                "per_page": pool_size,
                "select":   "id,title,abstract_inverted_index,authorships,"
                            "publication_date,doi,cited_by_count,type",
                "mailto":   "scisynth@research.app",
            },
            timeout=12,
        )
        resp.raise_for_status()
        papers: list[dict] = []
        for w in resp.json().get("results", []):
            abstract = _reconstruct_abstract(w.get("abstract_inverted_index"))
            if not abstract:
                continue
            auths     = [a["author"]["display_name"] for a in (w.get("authorships") or [])[:3] if a.get("author")]
            suffix    = " et al." if len(w.get("authorships", [])) > 3 else ""
            doi       = (w.get("doi") or "").replace("https://doi.org/", "")
            url       = f"https://doi.org/{doi}" if doi else w.get("id", "")
            pub_date  = w.get("publication_date") or ""
            cited     = w.get("cited_by_count") or 0
            ptype     = w.get("type") or ""
            score     = _quality_score(cited, pub_date, ptype, discipline)
            papers.append({
                "title":   w.get("title") or "",
                "short":   abstract[:420] + "…" if len(abstract) > 420 else abstract,
                "full":    abstract,
                "authors": ", ".join(auths) + suffix if auths else "–",
                "date":    pub_date[:7],
                "url":     url,
                "doi":     doi,
                "cats":    ["OpenAlex"],
                "source":  "OpenAlex",
                "cited":   cited,
                "type":    ptype,
                "score":   score,
            })
        # Nach Composite-Score sortieren, Top-N zurückgeben
        papers.sort(key=lambda p: p["score"], reverse=True)
        return papers[:n]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_semantic_scholar(ss_query: str, year_from: int, year_to: int,
                             n: int, discipline: str = "") -> list[dict]:
    """Fetches papers from Semantic Scholar. Better monograph coverage and semantic relevance ranking."""
    try:
        if discipline in _HUMANITIES_DISCIPLINES:
            pool = min(max(n * 4, 25), 100)
        elif discipline in _STEM_DISCIPLINES:
            pool = min(n * 2, 50)
        else:
            pool = min(max(n * 3, 20), 75)

        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query":  ss_query,
                "fields": "title,abstract,authors,year,citationCount,externalIds,publicationTypes",
                "limit":  pool,
                "year":   f"{year_from}-{year_to}",
            },
            headers={"User-Agent": "SciSynth/1.0 (academic research tool)"},
            timeout=15,
        )
        resp.raise_for_status()
        papers: list[dict] = []
        for w in resp.json().get("data", []):
            title = (w.get("title") or "").strip()
            if not title:
                continue
            abstract  = w.get("abstract") or ""
            year      = str(w.get("year") or "2020")
            cited     = w.get("citationCount") or 0
            ext_ids   = w.get("externalIds") or {}
            doi       = ext_ids.get("DOI", "")
            paper_id  = w.get("paperId", "")
            url       = f"https://doi.org/{doi}" if doi else f"https://www.semanticscholar.org/paper/{paper_id}"
            auth_list = [a["name"] for a in (w.get("authors") or [])[:3] if a.get("name")]
            suffix    = " et al." if len(w.get("authors") or []) > 3 else ""
            pub_types = w.get("publicationTypes") or []
            ptype     = ("journal-article" if "JournalArticle" in pub_types
                         else "book" if "Book" in pub_types else "")
            score     = _quality_score(cited, year + "-01-01", ptype, discipline)
            papers.append({
                "title":        title,
                "short":        abstract[:420] + "…" if len(abstract) > 420 else abstract,
                "full":         abstract,
                "authors":      ", ".join(auth_list) + suffix if auth_list else "–",
                "date":         year[:4] + "-01",
                "url":          url,
                "doi":          doi,
                "cats":         ["Semantic Scholar"],
                "source":       "Semantic Scholar",
                "cited":        cited,
                "type":         ptype,
                "score":        score,
                "has_abstract": bool(abstract),
            })
        papers.sort(key=lambda p: p["score"], reverse=True)
        return papers[:n]
    except Exception:
        return []


def _is_duplicate(p: dict, seen_titles: set, seen_dois: set) -> bool:
    doi = (p.get("doi") or "").strip()
    if doi and doi in seen_dois:
        return True
    return p["title"].lower()[:60] in seen_titles


def _mark_seen(p: dict, seen_titles: set, seen_dois: set) -> None:
    doi = (p.get("doi") or "").strip()
    seen_titles.add(p["title"].lower()[:60])
    if doi:
        seen_dois.add(doi)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_papers(disciplines: tuple[str, ...], query: str, year_from: int, year_to: int,
                 max_per: int, dynamic_queries: tuple[tuple[str, str], ...],
                 peer_review_only: bool) -> dict[str, list[dict]]:
    dq_map = dict(dynamic_queries)  # discipline → optimized query
    result: dict[str, list[dict]] = {}
    half = max(max_per // 2, 2)
    seen_titles: set[str] = set()  # normalized title prefix
    seen_dois:   set[str] = set()  # DOI-based dedup (more reliable)

    for discipline in disciplines:
        papers: list[dict] = []

        # arXiv (STEM)
        cats = ARXIV_CATS.get(discipline)
        if cats:
            for p in _fetch_arxiv(tuple(cats), query, year_from, year_to, half * 2):
                if not _is_duplicate(p, seen_titles, seen_dois):
                    papers.append(p)

        # Queries aus dq_map extrahieren — "primary|||synonyms" aufteilen
        raw_q   = dq_map.get(discipline) or OPENALEX_QUERIES.get(discipline, "")
        queries = [q.strip() for q in raw_q.split("|||") if q.strip()] if raw_q else []

        def _add_from_source(new_papers: list[dict]) -> None:
            seen_local_t: set[str] = {p["title"].lower()[:60] for p in papers}
            seen_local_d: set[str] = {(p.get("doi") or "").strip() for p in papers if p.get("doi")}
            for p in new_papers:
                if not _is_duplicate(p, seen_titles, seen_dois) and \
                   not _is_duplicate(p, seen_local_t, seen_local_d):
                    papers.append(p)
                    seen_local_t.add(p["title"].lower()[:60])
                    doi = (p.get("doi") or "").strip()
                    if doi:
                        seen_local_d.add(doi)

        # OpenAlex — beide Query-Varianten ausführen
        for q in queries:
            _add_from_source(
                _fetch_openalex(q, year_from, year_to, half * 2, peer_review_only, discipline)
            )

        # Semantic Scholar — beide Query-Varianten ausführen
        for q in queries:
            _add_from_source(
                _fetch_semantic_scholar(q, year_from, year_to, half * 2, discipline)
            )

        kept = papers[:max_per]
        if kept:
            result[discipline] = kept
            for p in kept:
                _mark_seen(p, seen_titles, seen_dois)

    return result

# ── KI-Funktionen ──────────────────────────────────────────────────────────────
def synthesize(papers: dict[str, list[dict]], topic: str, api_key: str) -> dict:
    client  = anthropic.Anthropic(api_key=api_key)
    context = ""
    for disc, ps in papers.items():
        context += f"\n\n### {disc}\n"
        for i, p in enumerate(ps[:4], 1):
            context += f"\n{i}. **{p['title']}**\n{p['full'][:360]}…\n"

    prompt = f"""Du bist ein führender transdisziplinärer Wissenschaftssynthetiker. \
Analysiere die folgenden aktuellen Forschungsarbeiten und erkenne überraschende \
Verbindungen über Disziplingrenzen hinweg.

Nutzerfokus: "{topic.strip() if topic and topic.strip() else 'Offene Exploration'}"

Forschungsarbeiten:{context}

Antworte ausschließlich mit diesem JSON:
{{
    "emerging_patterns": "<2–3 prägnante Sätze>",
    "key_themes": {{ "<Disziplin>": ["<Thema1>", "<Thema2>", "<Thema3>"] }},
    "research_ideas": [
        {{
            "title": "<Titel>", "disciplines": ["<D1>", "<D2>"],
            "description": "<Beschreibung>", "novelty": "<Neuheit>",
            "methodology": "<Methodik>", "impact": "<Impact>"
        }}
    ],
    "cross_disciplinary_bridges": [
        {{
            "title": "<Titel>", "disciplines": ["<D1>", "<D2>"],
            "description": "<Beschreibung>", "potential": "<Potenzial>"
        }}
    ],
    "methodology_transfers": [
        {{
            "from_discipline": "<Von>", "to_discipline": "<Nach>",
            "method": "<Methode>", "application": "<Anwendung>", "benefit": "<Mehrwert>"
        }}
    ]
}}"""
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=5000,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def deepen_idea(idea: dict, papers: dict, api_key: str) -> dict:
    client  = anthropic.Anthropic(api_key=api_key)
    context = ""
    for disc, ps in papers.items():
        context += f"\n### {disc}: " + "; ".join(p["title"] for p in ps[:3])

    prompt = f"""Vertiefe die folgende Forschungsidee mit maximaler Detailtiefe für einen Wissenschaftler.

Idee: {json.dumps(idea, ensure_ascii=False)}

Verfügbare Paper-Kontexte:{context}

Antworte ausschließlich mit diesem JSON:
{{
    "deep_description": "<ausführliche 4–6 Satz Beschreibung>",
    "research_questions": ["<Forschungsfrage 1>", "<Forschungsfrage 2>", "<Forschungsfrage 3>"],
    "methodology_details": "<konkrete methodische Vorgehensweise, Schritt für Schritt>",
    "theoretical_foundations": "<relevante Theorien und Konzepte aus den beteiligten Disziplinen>",
    "open_challenges": ["<Herausforderung 1>", "<Herausforderung 2>"],
    "next_steps": ["<Erster konkreter Schritt>", "<Zweiter Schritt>", "<Dritter Schritt>"],
    "interdisciplinary_tension": "<Wo könnten die Disziplinen in Konflikt geraten und wie löst man das>",
    "literature_queries": [
        {{"discipline": "<Disziplin>", "query": "<präziser englischer Suchbegriff 4–8 Wörter für OpenAlex>"}},
        {{"discipline": "<Disziplin>", "query": "<präziser englischer Suchbegriff 4–8 Wörter für OpenAlex>"}},
        {{"discipline": "<Disziplin>", "query": "<präziser englischer Suchbegriff 4–8 Wörter für OpenAlex>"}}
    ],
    "counter_queries": [
        {{"discipline": "<Disziplin>", "query": "<englischer Suchbegriff für kritische/gegenteilige Perspektiven 4–8 Wörter>"}},
        {{"discipline": "<Disziplin>", "query": "<englischer Suchbegriff für Kritik oder Gegenargumente>"}}
    ]
}}"""
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=3000,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)

def synthesize_with_literature(idea: dict, lit_papers: list[dict], deepened: dict, api_key: str,
                               counter_papers: list[dict] = []) -> dict:
    """Zweiter Claude-Call: Synthetisiert die gefundene Literatur mit der Idee zu einer
    wissenschaftlich belastbaren Analyse mit Forschungslücke, These und Beitragsaussage."""
    client = anthropic.Anthropic(api_key=api_key)

    lit_context = ""
    for p in lit_papers[:8]:
        abstract = p.get("full", p.get("short", ""))[:400]
        lit_context += f"\n- **{p['title']}** ({p.get('date','')[:4]}, {p.get('authors','')})\n  {abstract}\n"

    counter_context = ""
    if counter_papers:
        counter_context = "\n\nKritische / gegenteilige Literatur:\n"
        for p in counter_papers[:4]:
            abstract = p.get("full", p.get("short", ""))[:300]
            counter_context += f"\n- **{p['title']}** ({p.get('date','')[:4]})\n  {abstract}\n"

    prompt = f"""Du bist ein erfahrener Wissenschaftler und Betreuer von Abschlussarbeiten. \
Analysiere die folgende Forschungsidee im Licht der tatsächlich gefundenen Literatur \
und erstelle eine wissenschaftlich belastbare Grundlage für eine Abschlussarbeit oder ein Forschungsprojekt.

Forschungsidee: {json.dumps(idea, ensure_ascii=False)}

Theoretische Grundlage (bereits erarbeitet): {deepened.get('theoretical_foundations', '')}

Gefundene Literatur:
{lit_context}{counter_context}

Deine Aufgabe:
1. Lies die Abstracts kritisch und ordne sie ein
2. Identifiziere die echte Forschungslücke die diese Literatur offen lässt
3. Verfeinere die These auf Basis dessen was tatsächlich existiert
4. Formuliere einen klaren wissenschaftlichen Beitrag

Wichtig: Belege jede Kernaussage in "refined_thesis" und "contribution_statement" \
mit [Autorname, Jahr] direkt im Text. Spekulativen Inhalt kennzeichne explizit mit "(spekulativ)".

Antworte ausschließlich mit diesem JSON:
{{
    "literature_map": [
        {{
            "title": "<Kurztitel des Papers>",
            "relation": "stützt|widerspricht|ergänzt|liefert Methode|Hintergrund",
            "relevance": "<1–2 Sätze: Wie genau hängt dieses Paper mit der Idee zusammen?>"
        }}
    ],
    "research_gap": "<Präzise Beschreibung der Lücke in der Literatur — was fehlt, was ist ungeklärt, was wird ignoriert?>",
    "refined_thesis": "<Die verfeinerte, literaturgestützte These in 2–3 Sätzen mit [Autorname, Jahr] Belegen>",
    "contribution_statement": "<Diese Arbeit würde X beitragen, indem sie Y und Z verbindet — konkret und akademisch formuliert, mit [Autorname, Jahr] Belegen>",
    "objections": [
        {{"objection": "<Möglicher Einwand>", "response": "<Wie man ihm begegnet>"}}
    ],
    "key_authors": ["<Autor 1>", "<Autor 2>", "<Autor 3>"],
    "positioning": "<In welcher akademischen Debatte positioniert sich diese Arbeit? Welche Schulen/Strömungen sind relevant?>",
    "counter_synthesis": "<Wie verhalten sich die Gegenargumente zur These? Was muss die Arbeit berücksichtigen?>"
}}"""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=4000,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def verify_authors_openalex(authors: list[str]) -> dict[str, bool]:
    """Prüft ob genannte Autoren in OpenAlex existieren. Gibt {name: verified} zurück."""
    verified = {}
    for name in authors[:5]:  # max 5 checks
        try:
            resp = requests.get(
                "https://api.openalex.org/authors",
                params={"search": name, "per_page": 1, "mailto": "scisynth@research.app"},
                timeout=5,
            )
            results = resp.json().get("results", [])
            verified[name] = len(results) > 0
        except Exception:
            verified[name] = True  # fail open — nicht als falsch markieren
    return verified


def generate_search_queries(disciplines: tuple[str, ...], topic: str, api_key: str) -> dict[str, str]:
    """Generiert zwei Suchanfragen pro Disziplin:
    1) primary: thematisch präzise Kernbegriffe
    2) synonyms: erweitertes Vokabular, Schulen, Strömungen, Schlüsselautoren
    Gespeichert als 'primary|||synonyms' (Cache-kompatibel)."""
    client    = anthropic.Anthropic(api_key=api_key)
    disc_list = "\n".join(f"- {d}" for d in disciplines)
    prompt    = f"""Das Forschungsthema kann in beliebiger Sprache vorliegen (häufig Deutsch).
Übersetze es zuerst gedanklich ins Englische.

Generiere für jede Disziplin ZWEI englische Suchanfragen für akademische Datenbanken:
1. "primary": Präzise Kernbegriffe des Themas (6–9 Wörter)
2. "synonyms": Alternatives Vokabular — Synonyme, verwandte Konzepte, akademische
   Schulen/Strömungen, Schlüsselautoren-Nachnamen (6–9 Wörter, terminologisch ANDERS als primary)

Beispiel für Thema "hegemony international law", Disziplin "Jura & Rechtswissenschaft":
- primary: "international law sovereignty hegemony power structures colonial"
- synonyms: "imperialism TWAIL Anghie third world postcolonial legal theory"

Forschungsthema: "{topic or 'Open transdisciplinary exploration'}"

Disziplinen:
{disc_list}

Regeln:
- Nur Englisch, akademisch spezifisch
- Keine generischen Begriffe wie "research" oder "study"
- synonyms muss terminologisch ANDERS sein als primary
- Für Geistes-/Sozialwiss.: Schulnamen (TWAIL, CLS, Frankfurt School usw.) und Autorennamen einbauen

Antworte NUR mit diesem JSON:
{{"<Disziplinname>": {{"primary": "<Primärquery>", "synonyms": "<Synonymquery>"}}}}"""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=1200,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    raw = json.loads(text)
    result = {}
    for disc, val in raw.items():
        if isinstance(val, dict):
            p = val.get("primary", "")
            s = val.get("synonyms", "")
            result[disc] = f"{p}|||{s}" if s else p
        else:
            result[disc] = str(val)
    return result


def generate_paper_abstract(paper: dict, api_key: str) -> str:
    """Generates a brief AI summary for a well-known paper that lacks an indexed abstract.
    Only suitable for highly-cited works Claude likely knows from training data."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""Erstelle eine wissenschaftliche Kurzzusammenfassung (3–4 Sätze) für folgendes Werk:

Titel: {paper['title']}
Autor(en): {paper.get('authors', '–')}
Jahr: {(paper.get('date') or '')[:4]}
Zitierungen: {paper.get('cited', 0)}
Quelle: {paper.get('source', '')}

Wichtig: Basiere die Zusammenfassung ausschließlich auf deinem Trainingswissen.
Falls du das Werk nicht kennst, antworte nur mit: "Werk nicht in Trainingsdaten bekannt."
Antworte NUR mit der Zusammenfassung, ohne Präambel oder Erklärung."""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


# ── Dokument-Upload ────────────────────────────────────────────────────────────
def extract_text(uploaded_file) -> str:
    """Extrahiert Text aus PDF oder TXT. Gibt max. 4000 Zeichen zurück."""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")[:4000]
    if name.endswith(".pdf"):
        if not _PYPDF_AVAILABLE:
            return ""
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        pages  = [p.extract_text() or "" for p in reader.pages[:20]]
        return "\n".join(pages)[:4000]
    return ""


def synthesize_from_documents(docs: list[dict], course_title: str, api_key: str) -> dict:
    """Lässt Claude Forschungsideen aus hochgeladenen Kursdokumenten generieren."""
    client  = anthropic.Anthropic(api_key=api_key)
    context = ""
    for d in docs:
        context += f"\n\n### Dokument: {d['name']}\n{d['text'][:2000]}…"

    title_hint = f'Kurstitel: "{course_title}"\n\n' if course_title.strip() else ""

    prompt = f"""{title_hint}Die folgenden Texte stammen aus Kursmaterialien. \
Analysiere die Themenspektren und entwickle daraus originelle, transdisziplinäre Forschungsideen \
für eine wissenschaftliche Abschlussarbeit oder ein Forschungsprojekt.

Kursmaterialien:{context}

Antworte ausschließlich mit diesem JSON:
{{
    "course_summary": "<2–3 Sätze: Was verbindet diese Materialien thematisch?>",
    "key_themes": ["<Thema 1>", "<Thema 2>", "<Thema 3>", "<Thema 4>", "<Thema 5>"],
    "research_ideas": [
        {{
            "title": "<Titel der Forschungsidee>",
            "disciplines": ["<Disziplin 1>", "<Disziplin 2>"],
            "description": "<2–3 Sätze Beschreibung>",
            "novelty": "<Was ist neu oder überraschend an diesem Ansatz?>",
            "methodology": "<Vorgeschlagene Methodik>",
            "thesis_angle": "<Konkreter Winkel für eine Abschlussarbeit>"
        }}
    ],
    "interdisciplinary_potential": "<Wo liegen die stärksten Brücken zwischen den Themen?>"
}}"""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=3000,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def view_upload(api_key: str) -> None:
    render_header()
    st.markdown('<div class="section-title">Kurs-Analyse</div>', unsafe_allow_html=True)

    if not api_key:
        st.warning("Bitte einen Claude API Key eingeben.")
        return

    result = st.session_state.get("upload_result")
    docs   = st.session_state.get("upload_docs", [])

    if not docs and not result:
        st.markdown("""
        <div class="welcome">
            <div class="welcome-icon">◎</div>
            <h3>Kursmaterialien hochladen</h3>
            <p>Lade PDFs oder Textdateien deiner Lehrveranstaltung hoch.<br>
            Claude analysiert die Themenspektren und entwickelt daraus Forschungsideen
            für deine Abschlussarbeit oder ein Seminarreferat.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if result:
        # Kurszusammenfassung
        st.markdown(f"""
        <div class="idea-card">
            <div style="font-size:0.72em;font-weight:600;letter-spacing:0.07em;
                        text-transform:uppercase;color:#92400e;margin-bottom:6px">Thematischer Kern</div>
            <p style="margin:0;color:#374151">{result.get('course_summary','')}</p>
        </div>""", unsafe_allow_html=True)

        # Schlüsselthemen
        themes = result.get("key_themes", [])
        if themes:
            tags = " ".join(f'<span class="tag tag-amber">{t}</span>' for t in themes)
            st.markdown(f'<div style="margin:12px 0 20px">{tags}</div>', unsafe_allow_html=True)

        # Interdisziplinäres Potential
        if result.get("interdisciplinary_potential"):
            st.markdown(f"""
            <div class="bridge-card">
                <div style="font-size:0.72em;font-weight:600;letter-spacing:0.07em;
                            text-transform:uppercase;color:#0e7490;margin-bottom:6px">Interdisziplinäres Potential</div>
                <p style="margin:0;color:#374151">{result['interdisciplinary_potential']}</p>
            </div>""", unsafe_allow_html=True)

        # Forschungsideen
        st.markdown('<div class="section-title">Forschungsideen</div>', unsafe_allow_html=True)
        for i, idea in enumerate(result.get("research_ideas", [])):
            discs = " ".join(f'<span class="tag tag-amber">{d}</span>' for d in idea.get("disciplines", []))
            st.markdown(f"""
            <div class="idea-card">
                <div style="font-size:0.72em;font-weight:600;letter-spacing:0.07em;
                            text-transform:uppercase;color:#92400e;margin-bottom:4px">Idee {i+1}</div>
                <div style="font-weight:700;font-size:1.05em;color:#111827;margin-bottom:6px">{idea['title']}</div>
                <div style="margin-bottom:8px">{discs}</div>
                <p style="margin:0 0 8px;color:#374151">{idea.get('description','')}</p>
                <div style="font-size:0.82em;color:#6b7280"><strong>Neuheit:</strong> {idea.get('novelty','')}</div>
                <div style="font-size:0.82em;color:#6b7280;margin-top:4px"><strong>Methodik:</strong> {idea.get('methodology','')}</div>
                <div style="font-size:0.82em;color:#6b7280;margin-top:4px"><strong>Abschlussarbeits-Winkel:</strong> {idea.get('thesis_angle','')}</div>
            </div>""", unsafe_allow_html=True)


# ── Render-Funktionen ──────────────────────────────────────────────────────────
def render_header() -> None:
    st.markdown("""
    <div class="page-header">
        <div class="page-accent"></div>
        <div class="page-title">SciSynth</div>
        <p class="page-subtitle">
            Entdecke verborgene Verbindungen zwischen Wissenschaftsdisziplinen —
            aktuelle Forschung, transdisziplinär synthetisiert.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_paper(paper: dict, render_idx: int = 0) -> None:
    src   = paper.get("source", "arXiv")
    if src == "arXiv":
        s_css = "background:#f0fdfa;color:#0f766e;border:1px solid #99f6e4"
    elif src == "Semantic Scholar":
        s_css = "background:#fdf4ff;color:#7e22ce;border:1px solid #e9d5ff"
    else:
        s_css = "background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe"
    cats  = " ".join(f'<span class="tag tag-gray">{c}</span>' for c in paper["cats"])
    fav_id = _item_id("paper", paper["title"])
    st.markdown(f"""
    <div class="paper-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px">
            <div class="paper-title">{paper['title']}</div>
            <span style="font-size:0.67em;font-weight:600;padding:2px 8px;border-radius:5px;
                         white-space:nowrap;letter-spacing:0.04em;{s_css}">{src}</span>
        </div>
        <div class="paper-meta">{paper['authors']} · {paper['date']}</div>
        <div class="paper-abstract">{paper['short']}</div>
        <div style="margin-top:9px">{cats}</div>
        <a href="{paper['url']}" target="_blank" class="paper-link">Paper öffnen →</a>
    </div>
    """, unsafe_allow_html=True)
    # Abstract generation for papers without abstract
    if not paper.get("short", "").strip() or not paper.get("full", "").strip():
        abs_cache_key = f"gen_abs_{fav_id}_{render_idx}"
        gen_col, _ = st.columns([3, 8])
        with gen_col:
            if abs_cache_key in st.session_state:
                generated = st.session_state[abs_cache_key]
                st.markdown(f"""
                <div style="background:#fef9c3;border-radius:6px;padding:8px 12px;
                            font-size:0.82em;color:#374151;margin:4px 0">
                    <span style="font-size:0.72em;font-weight:600;text-transform:uppercase;
                                 color:#92400e;display:block;margin-bottom:4px">
                        KI-Zusammenfassung (nicht verifiziert)
                    </span>{generated}
                </div>""", unsafe_allow_html=True)
            else:
                api_key_for_abs = st.session_state.get("current_api_key", "")
                if api_key_for_abs and st.button("Zusammenfassung generieren", key=f"gen_abs_btn_{fav_id}_{render_idx}"):
                    with st.spinner("Claude generiert Zusammenfassung…"):
                        try:
                            result_abs = generate_paper_abstract(paper, api_key_for_abs)
                            st.session_state[abs_cache_key] = result_abs
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler: {e}")

    col_space, col_fav = st.columns([10, 1])
    with col_fav:
        already = is_favorite(fav_id)
        label   = "★" if already else "☆"
        if st.button(label, key=f"fav_paper_{fav_id}_{render_idx}", help="Favorit"):
            if already:
                remove_favorite(fav_id)
            else:
                save_favorite({"id": fav_id, "type": "paper", "title": paper["title"],
                               "body": paper["short"], "disciplines": paper["cats"],
                               "url": paper["url"]})
            st.rerun()


def render_idea(idea: dict, idx: int, papers: dict, api_key: str) -> None:
    fav_id = _item_id("idea", idea["title"])
    discs  = " ".join(f'<span class="tag tag-amber">{d}</span>' for d in idea.get("disciplines", []))
    st.markdown(f"""
    <div class="idea-card">
        <div class="card-title">{idea['title']}</div>
        <div style="margin-bottom:10px">{discs}</div>
        <div class="card-body">{idea['description']}</div>
        <div class="card-label">Neuheit</div>     <div class="card-body">{idea['novelty']}</div>
        <div class="card-label">Methodik</div>    <div class="card-body">{idea['methodology']}</div>
        <div class="card-label">Impact</div>      <div class="card-body">{idea['impact']}</div>
    </div>
    """, unsafe_allow_html=True)

    col_deep, col_fav = st.columns([3, 1])
    with col_deep:
        if st.button("Idee vertiefen →", key=f"deep_{idx}"):
            st.session_state[f"deepening_{idx}"] = True
    with col_fav:
        already = is_favorite(fav_id)
        if st.button("★" if already else "☆", key=f"fav_idea_{fav_id}", help="Favorit"):
            if already:
                remove_favorite(fav_id)
            else:
                save_favorite({"id": fav_id, "type": "idea", "title": idea["title"],
                               "body": idea["description"], "disciplines": idea.get("disciplines", []),
                               "full": idea})
            st.rerun()

    if st.session_state.get(f"deepening_{idx}"):
        cache_key = f"deepened_{fav_id}"
        if cache_key not in st.session_state:
            with st.spinner("Claude vertieft die Idee…"):
                try:
                    st.session_state[cache_key] = deepen_idea(idea, papers, api_key)
                except Exception as e:
                    st.error(f"Fehler: {e}")
                    st.session_state[f"deepening_{idx}"] = False

        if result := st.session_state.get(cache_key):
            with st.expander("Tiefenanalyse", expanded=True):
                st.markdown(f'<div class="deepen-box">', unsafe_allow_html=True)
                st.markdown(f"**Ausführliche Beschreibung**\n\n{result.get('deep_description','')}")
                if qs := result.get("research_questions"):
                    st.markdown("**Forschungsfragen**")
                    for q in qs:
                        st.markdown(f'<div class="deepen-question">· {q}</div>', unsafe_allow_html=True)
                if md := result.get("methodology_details"):
                    st.markdown(f"**Methodische Vorgehensweise**\n\n{md}")
                if tf := result.get("theoretical_foundations"):
                    st.markdown(f"**Theoretische Grundlagen**\n\n{tf}")
                if oc := result.get("open_challenges"):
                    st.markdown("**Offene Herausforderungen**")
                    for c in oc:
                        st.markdown(f"- {c}")
                if ns := result.get("next_steps"):
                    st.markdown("**Nächste Schritte**")
                    for i, s in enumerate(ns, 1):
                        st.markdown(f"{i}. {s}")
                if it := result.get("interdisciplinary_tension"):
                    st.markdown(f"**Interdisziplinäre Spannungsfelder**\n\n{it}")
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Schritt 2: Weiterführende Literatur aus OpenAlex ──────────────
            lit_queries     = result.get("literature_queries", [])
            counter_queries = result.get("counter_queries", [])
            if lit_queries:
                lit_cache     = f"lit_{cache_key}"
                counter_cache = f"counter_{cache_key}"
                synth_cache   = f"litsynth_{cache_key}"

                if lit_cache not in st.session_state:
                    with st.spinner("Suche weiterführende Literatur…"):
                        found: list[dict] = []
                        seen: set[str] = set()
                        for lq in lit_queries:
                            q = lq.get("query", "").strip()
                            if not q:
                                continue
                            try:
                                for p in _fetch_openalex(q, 1900, 2025, 4, False):
                                    key = p["title"].lower()[:60]
                                    if key not in seen:
                                        seen.add(key)
                                        found.append(p)
                            except Exception:
                                pass
                        st.session_state[lit_cache] = found[:8]

                lit_papers = st.session_state.get(lit_cache, [])

                # ── Schritt 2b: Gegenliteratur aus OpenAlex ───────────────────
                if counter_queries and counter_cache not in st.session_state:
                    with st.spinner("Suche kritische Gegenliteratur…"):
                        counter_found: list[dict] = []
                        counter_seen: set[str] = set()
                        for cq in counter_queries:
                            q = cq.get("query", "").strip()
                            if not q:
                                continue
                            try:
                                for p in _fetch_openalex(q, 1900, 2025, 4, False):
                                    key = p["title"].lower()[:60]
                                    if key not in counter_seen:
                                        counter_seen.add(key)
                                        counter_found.append(p)
                            except Exception:
                                pass
                        st.session_state[counter_cache] = counter_found[:6]

                counter_papers = st.session_state.get(counter_cache, [])

                # ── Schritt 3: Literatursynthese mit zweitem Claude-Call ──────
                if lit_papers and synth_cache not in st.session_state:
                    with st.spinner("Claude synthetisiert Literatur und verfeinert die These…"):
                        try:
                            st.session_state[synth_cache] = synthesize_with_literature(
                                idea, lit_papers, result, api_key, counter_papers
                            )
                        except Exception as e:
                            st.session_state[synth_cache] = {}
                            st.error(f"Literatursynthese fehlgeschlagen: {e}")

                # ── Ausgabe: Wissenschaftliche Fundierung ─────────────────────
                synth = st.session_state.get(synth_cache, {})

                # Author verification
                auth_cache = f"authverify_{cache_key}"
                if synth and synth.get("key_authors") and auth_cache not in st.session_state:
                    st.session_state[auth_cache] = verify_authors_openalex(synth["key_authors"])

                if synth:
                    with st.expander("Wissenschaftliche Fundierung", expanded=True):
                        # Verfeinerte These
                        if rt := synth.get("refined_thesis"):
                            st.markdown(f"""
                            <div class="bridge-card">
                                <div class="card-label">Verfeinerte These</div>
                                <p style="margin:4px 0 0;color:#111827;font-size:1.0em">{rt}</p>
                            </div>""", unsafe_allow_html=True)

                        # Forschungslücke
                        if gap := synth.get("research_gap"):
                            st.markdown(f"""
                            <div class="idea-card" style="margin-top:10px">
                                <div class="card-label">Forschungslücke</div>
                                <p style="margin:4px 0 0;color:#374151">{gap}</p>
                            </div>""", unsafe_allow_html=True)

                        # Beitragsaussage
                        if cs := synth.get("contribution_statement"):
                            st.markdown(f"""
                            <div class="paper-card" style="margin-top:10px">
                                <div class="card-label">Wissenschaftlicher Beitrag</div>
                                <p style="margin:4px 0 0;color:#374151">{cs}</p>
                            </div>""", unsafe_allow_html=True)

                        # Positionierung
                        if pos := synth.get("positioning"):
                            st.markdown(f"**Akademische Positionierung**\n\n{pos}")

                        # Literaturkarte
                        if lmap := synth.get("literature_map"):
                            st.markdown("**Literaturkarte**")
                            rel_colors = {
                                "stützt":          "#d1fae5",
                                "widerspricht":    "#fee2e2",
                                "ergänzt":         "#dbeafe",
                                "liefert Methode": "#fef3c7",
                                "Hintergrund":     "#f3f4f6",
                            }
                            for lm in lmap:
                                rel   = lm.get("relation", "")
                                color = rel_colors.get(rel, "#f3f4f6")
                                st.markdown(f"""
                                <div style="background:{color};border-radius:6px;padding:8px 12px;margin-bottom:6px">
                                    <span style="font-weight:600;font-size:0.88em">{lm.get('title','')}</span>
                                    <span style="font-size:0.75em;font-weight:600;text-transform:uppercase;
                                                 margin-left:8px;color:#6b7280">{rel}</span>
                                    <div style="font-size:0.82em;color:#374151;margin-top:4px">{lm.get('relevance','')}</div>
                                </div>""", unsafe_allow_html=True)

                        # Einwände
                        if objs := synth.get("objections"):
                            st.markdown("**Mögliche Einwände & Antworten**")
                            for ob in objs:
                                st.markdown(f"""
                                <div style="border-left:3px solid #e5e7eb;padding:6px 12px;margin-bottom:6px">
                                    <div style="font-size:0.85em;font-weight:600;color:#111827">↯ {ob.get('objection','')}</div>
                                    <div style="font-size:0.82em;color:#6b7280;margin-top:3px">→ {ob.get('response','')}</div>
                                </div>""", unsafe_allow_html=True)

                        # Gegensynthese
                        if csynth := synth.get("counter_synthesis"):
                            st.markdown(f"""
                            <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;
                                        padding:10px 14px;margin-top:10px">
                                <div style="font-size:0.75em;font-weight:600;text-transform:uppercase;
                                            letter-spacing:0.08em;color:#9a3412;margin-bottom:4px">Kritische Perspektive</div>
                                <div style="font-size:0.85em;color:#374151">{csynth}</div>
                            </div>""", unsafe_allow_html=True)

                        # Schlüsselautoren (mit Verifikation)
                        if authors := synth.get("key_authors"):
                            verif = st.session_state.get(auth_cache, {})
                            tags = ""
                            for a in authors:
                                is_ok = verif.get(a, True)
                                css_class = "tag-teal" if is_ok else "tag-gray"
                                label = a if is_ok else f"{a} (nicht verifiziert)"
                                tags += f'<span class="tag {css_class}">{label}</span> '
                            st.markdown(f"**Schlüsselautoren**<br>{tags}", unsafe_allow_html=True)

                # Paper-Liste
                if lit_papers:
                    st.markdown('<div class="section-title" style="font-size:0.9em;margin-top:16px">Weiterführende Literatur</div>', unsafe_allow_html=True)
                    for pi, lp in enumerate(lit_papers):
                        render_paper(lp, render_idx=hash(cache_key + str(pi)))

                # Kritische Perspektiven
                if counter_papers:
                    st.markdown('<div class="section-title" style="font-size:0.9em;margin-top:16px">Kritische Perspektiven</div>', unsafe_allow_html=True)
                    for pi, cp in enumerate(counter_papers):
                        render_paper(cp, render_idx=hash(cache_key + "counter" + str(pi)))


def render_bridge(bridge: dict) -> None:
    fav_id = _item_id("bridge", bridge["title"])
    discs  = " ".join(f'<span class="tag tag-teal">{d}</span>' for d in bridge.get("disciplines", []))
    st.markdown(f"""
    <div class="bridge-card">
        <div class="card-title">{bridge['title']}</div>
        <div style="margin-bottom:10px">{discs}</div>
        <div class="card-body">{bridge['description']}</div>
        <div class="card-label">Potenzial</div>
        <div class="card-body">{bridge['potential']}</div>
    </div>
    """, unsafe_allow_html=True)
    _, col_fav = st.columns([10, 1])
    with col_fav:
        already = is_favorite(fav_id)
        if st.button("★" if already else "☆", key=f"fav_bridge_{fav_id}", help="Favorit"):
            if already:
                remove_favorite(fav_id)
            else:
                save_favorite({"id": fav_id, "type": "bridge", "title": bridge["title"],
                               "body": bridge["description"], "disciplines": bridge.get("disciplines", []),
                               "full": bridge})
            st.rerun()


def render_transfer(mt: dict) -> None:
    st.markdown(f"""
    <div class="method-card">
        <div class="card-title">{mt['method']}</div>
        <div style="margin-bottom:10px">
            <span class="tag tag-indigo">{mt['from_discipline']}</span>
            <span style="margin:0 6px;color:#9ca3af;font-size:0.85em">→</span>
            <span class="tag tag-teal">{mt['to_discipline']}</span>
        </div>
        <div class="card-body">{mt['application']}</div>
        <div class="card-label">Mehrwert</div>
        <div class="card-body">{mt['benefit']}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Views ──────────────────────────────────────────────────────────────────────
def view_analyse(api_key: str, topic: str, selected: list[str], year_from: int,
                 year_to: int, max_papers: int, peer_review_only: bool, run: bool) -> None:
    render_header()

    if run:
        if len(selected) < 2:
            st.warning("Bitte mindestens 2 Disziplinen wählen.")
            return
        if not api_key:
            st.warning("Bitte einen Claude API Key eingeben.")
            return
        st.session_state.analysis_params = {
            "api_key":          api_key,
            "topic":            topic,
            "selected":         selected,
            "year_from":        year_from,
            "year_to":          year_to,
            "max_papers":       max_papers,
            "peer_review_only": peer_review_only,
        }
        # Dynamische Queries bei neuer Analyse zurücksetzen
        qkey = f"dq_{'_'.join(sorted(selected))}_{topic}"
        st.session_state.pop(qkey, None)

    params = st.session_state.get("analysis_params")
    if not params:
        st.markdown("""
        <div class="welcome">
            <div class="welcome-icon">◎</div>
            <h3>Bereit zur Exploration</h3>
            <p>Wähle Disziplinen, gib optional ein Fokusthema ein und starte die Analyse.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if params:
        st.session_state["current_api_key"] = params["api_key"]

    api_key          = params["api_key"]
    topic            = params["topic"]
    selected         = params["selected"]
    year_from        = params["year_from"]
    year_to          = params["year_to"]
    max_papers       = params["max_papers"]
    peer_review_only = params["peer_review_only"]

    # Dynamische Suchbegriffe generieren (einmalig pro Analyse)
    qkey = f"dq_{'_'.join(sorted(selected))}_{topic}"
    if qkey not in st.session_state:
        with st.spinner("Optimiere Suchbegriffe für deine Disziplinen…"):
            try:
                st.session_state[qkey] = generate_search_queries(
                    tuple(selected), topic or "", api_key
                )
            except Exception:
                st.session_state[qkey] = {}

    dynamic_queries = tuple(st.session_state.get(qkey, {}).items())

    with st.spinner("Lade und bewerte Paper…"):
        papers = fetch_papers(tuple(selected), topic or "", year_from, year_to,
                              max_papers, dynamic_queries, peer_review_only)

    if not papers:
        st.error("Keine Paper gefunden. Andere Suchbegriffe oder Disziplinen versuchen.")
        return

    total = sum(len(v) for v in papers.values())
    n     = len(papers)
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Paper</div></div>
        <div class="stat-box"><div class="stat-number">{n}</div><div class="stat-label">Disziplinen</div></div>
        <div class="stat-box"><div class="stat-number">{year_from}–{year_to}</div><div class="stat-label">Zeitraum</div></div>
        <div class="stat-box"><div class="stat-number">{n*(n-1)//2}</div><div class="stat-label">Verbindungen</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Aktuelle Forschung</div>', unsafe_allow_html=True)
    tabs = st.tabs([d[:28] + "…" if len(d) > 28 else d for d in papers.keys()])
    paper_counter = 0
    for tab, (disc, disc_papers) in zip(tabs, papers.items()):
        with tab:
            for p in disc_papers:
                render_paper(p, paper_counter)
                paper_counter += 1

    st.markdown('<div class="section-title">KI-Synthese</div>', unsafe_allow_html=True)
    placeholder = st.empty()
    placeholder.info("Claude analysiert die Paper und sucht nach transdisziplinären Verbindungen…")

    cache_key = f"synthesis_{'_'.join(sorted(selected))}_{topic}_{year_from}_{year_to}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = synthesize(papers, topic or "", api_key)
            save_to_history(topic or "", selected, year_from, year_to, st.session_state[cache_key])
        except json.JSONDecodeError:
            placeholder.error("Fehler beim Parsen der Antwort. Bitte erneut versuchen.")
            return
        except anthropic.AuthenticationError:
            placeholder.error("Ungültiger API Key.")
            return
        except Exception as exc:
            placeholder.error(f"Fehler: {exc}")
            return

    placeholder.empty()
    synthesis = st.session_state[cache_key]

    if pattern := synthesis.get("emerging_patterns"):
        st.markdown('<div class="section-title">Übergreifende Muster</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="pattern-box">{pattern}</div>', unsafe_allow_html=True)

    if themes := synthesis.get("key_themes"):
        st.markdown('<div class="section-title">Kernthemen je Disziplin</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(themes), 3))
        for i, (disc, theme_list) in enumerate(themes.items()):
            with cols[i % 3]:
                items = "".join(f'<div class="theme-item">· {t}</div>' for t in theme_list)
                st.markdown(f'<div class="theme-box"><div class="theme-disc">{disc}</div>{items}</div>',
                            unsafe_allow_html=True)

    if ideas := synthesis.get("research_ideas"):
        st.markdown('<div class="section-title">Forschungsideen</div>', unsafe_allow_html=True)
        for i, idea in enumerate(ideas):
            render_idea(idea, i, papers, api_key)

    if bridges := synthesis.get("cross_disciplinary_bridges"):
        st.markdown('<div class="section-title">Transdisziplinäre Brücken</div>', unsafe_allow_html=True)
        for bridge in bridges:
            render_bridge(bridge)

    if transfers := synthesis.get("methodology_transfers"):
        st.markdown('<div class="section-title">Methoden-Transfer</div>', unsafe_allow_html=True)
        for mt in transfers:
            render_transfer(mt)


def view_favorites() -> None:
    render_header()
    st.markdown('<div class="section-title">Gespeicherte Favoriten</div>', unsafe_allow_html=True)
    favs = st.session_state.get("favorites", load_favorites())

    if not favs:
        st.markdown("""
        <div class="welcome">
            <div class="welcome-icon">☆</div>
            <h3>Keine Favoriten gespeichert</h3>
            <p>Markiere Ideen, Brücken und Paper mit ☆ um sie hier zu speichern.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    type_labels = {"idea": "Forschungsidee", "bridge": "Brücke", "paper": "Paper"}
    type_css    = {"idea": "fav-card-idea", "bridge": "fav-card-bridge", "paper": "fav-card-paper"}

    for fav in favs:
        fav_type  = fav.get("type", "idea")
        type_name = type_labels.get(fav_type, fav_type)
        css_class = type_css.get(fav_type, "")
        discs_html = " ".join(
            f'<span class="tag tag-gray">{d}</span>'
            for d in fav.get("disciplines", [])
        )
        st.markdown(f"""
        <div class="fav-card {css_class}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div class="card-title">{fav['title']}</div>
                <span class="tag tag-type">{type_name}</span>
            </div>
            <div style="margin:6px 0 10px">{discs_html}</div>
            <div class="card-body">{fav.get('body','')[:300]}{'…' if len(fav.get('body',''))>300 else ''}</div>
            <div class="fav-date">Gespeichert {fav.get('saved_at','')}</div>
        </div>
        """, unsafe_allow_html=True)

        col_link, col_del = st.columns([10, 1])
        if fav_type == "paper" and fav.get("url"):
            with col_link:
                st.markdown(f'<a href="{fav["url"]}" target="_blank" class="paper-link">Paper öffnen →</a>',
                            unsafe_allow_html=True)
        with col_del:
            if st.button("✕", key=f"del_{fav['id']}", help="Entfernen"):
                remove_favorite(fav["id"])
                st.rerun()


def view_history() -> None:
    render_header()
    st.markdown('<div class="section-title">Suchverlauf</div>', unsafe_allow_html=True)
    history = st.session_state.get("history", load_history())

    if not history:
        st.markdown("""
        <div class="welcome">
            <div class="welcome-icon">◷</div>
            <h3>Kein Verlauf vorhanden</h3>
            <p>Vergangene Analysen erscheinen hier automatisch.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    for entry in history:
        pattern_preview = entry.get("synthesis", {}).get("emerging_patterns", "")[:180]
        discs_str = " · ".join(entry.get("disciplines", [])[:4])
        if len(entry.get("disciplines", [])) > 4:
            discs_str += f" +{len(entry['disciplines'])-4}"

        st.markdown(f"""
        <div class="history-card">
            <div class="history-topic">{entry.get('topic', 'Offene Exploration')}</div>
            <div class="history-meta">
                {entry.get('timestamp','')} &nbsp;·&nbsp;
                {entry.get('year_from','')}–{entry.get('year_to','')} &nbsp;·&nbsp;
                {discs_str}
            </div>
            <div class="history-pattern">{pattern_preview}{'…' if len(pattern_preview)==180 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

        col_load, col_ideas, col_bridges = st.columns([2, 1, 1])
        with col_load:
            if st.button("Analyse laden", key=f"load_{entry['id']}"):
                st.session_state.preload = entry
                st.session_state.nav = "Analyse"
                st.rerun()
        synthesis = entry.get("synthesis", {})
        with col_ideas:
            st.caption(f"{len(synthesis.get('research_ideas',[]))} Ideen")
        with col_bridges:
            st.caption(f"{len(synthesis.get('cross_disciplinary_bridges',[]))} Brücken")

# ── Hauptapp ───────────────────────────────────────────────────────────────────
def main() -> None:
    # Session-State initialisieren
    if "favorites" not in st.session_state:
        st.session_state.favorites = load_favorites()
    if "history" not in st.session_state:
        st.session_state.history = load_history()

    # Preload aus History
    preload = st.session_state.pop("preload", None)

    with st.sidebar:
        st.markdown("## SciSynth")

        nav = st.segmented_control(
            "nav",
            options=["Analyse", "Kurs", "Favoriten", "Verlauf"],
            default=st.session_state.get("nav", "Analyse"),
            label_visibility="collapsed",
        )
        if nav:
            st.session_state.nav = nav
        else:
            nav = st.session_state.get("nav", "Analyse")
        st.markdown("---")

        if nav == "Analyse":
            _secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
            if _secret_key:
                api_key = _secret_key
            else:
                st.markdown("### API Key")
                api_key = st.text_input(
                    "api_key", type="password", placeholder="sk-ant-…",
                    label_visibility="collapsed",
                    help="Anthropic API Key — console.anthropic.com",
                )

            st.markdown("### Forschungsthema")
            default_topic = preload["topic"] if preload else ""
            topic = st.text_area(
                "topic", value=default_topic,
                placeholder="z. B. Bewusstsein und KI\noder Klimaresilienz in Städten",
                height=90, label_visibility="collapsed",
            )

            st.markdown("### Zeitraum")
            year_from, year_to = st.select_slider(
                "years", options=list(range(1900, 2026)),
                value=(preload["year_from"], preload["year_to"]) if preload else (2000, 2025),
                label_visibility="collapsed",
            )

            st.markdown("### Disziplinen")
            st.caption("2–5 Felder empfohlen · arXiv + OpenAlex (250 Mio. Werke)")
            default_discs = preload["disciplines"] if preload else ["Jura & Rechtswissenschaft", "Genderstudies", "Künstliche Intelligenz"]
            selected = st.multiselect(
                "disciplines", options=DISCIPLINES,
                default=[d for d in default_discs if d in DISCIPLINES],
                label_visibility="collapsed",
            )

            st.markdown("### Paper pro Disziplin")
            max_papers = st.slider(
                "max_papers", min_value=2, max_value=8, value=4,
                label_visibility="collapsed",
            )

            st.markdown("### Qualitätsfilter")
            peer_review_only = st.toggle(
                "Nur peer-reviewed Paper",
                value=False,
                help="Filtert auf Journal-Artikel — höhere Qualität, aber Monografien und Bücher (wichtig für Geisteswissenschaften & Jura) werden ausgeschlossen",
            )

            st.markdown("---")
            run = st.button("Analyse starten", use_container_width=True)

            fav_count  = len(st.session_state.favorites)
            hist_count = len(st.session_state.history)
            st.markdown("---")
            st.markdown(
                f"""<div style="font-size:0.75em;color:#9ca3af;line-height:2">
                <div style="font-size:0.78em;font-weight:600;letter-spacing:0.08em;
                            text-transform:uppercase;color:#d1d5db;margin-bottom:2px">Datenquellen</div>
                arXiv · OpenAlex
                <div style="font-size:0.78em;font-weight:600;letter-spacing:0.08em;
                            text-transform:uppercase;color:#d1d5db;margin:10px 0 2px">Gespeichert</div>
                {fav_count} Favoriten · {hist_count} Analysen
                </div>""",
                unsafe_allow_html=True,
            )
        elif nav == "Kurs":
            _secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
            if _secret_key:
                api_key = _secret_key
            else:
                st.markdown("### API Key")
                api_key = st.text_input(
                    "api_key_kurs", type="password", placeholder="sk-ant-…",
                    label_visibility="collapsed",
                    help="Anthropic API Key — console.anthropic.com",
                )

            st.markdown("### Kurstitel")
            course_title = st.text_input(
                "course_title", placeholder="z. B. Postkoloniale Rechtstheorie",
                label_visibility="collapsed",
            )

            st.markdown("### Dokumente hochladen")
            st.caption("PDF oder TXT · max. 20 Seiten pro Datei empfohlen")
            uploaded_files = st.file_uploader(
                "docs", type=["pdf", "txt"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )

            st.markdown("---")
            run_upload = st.button("Ideen generieren", use_container_width=True)

            if run_upload and uploaded_files:
                docs = []
                for f in uploaded_files:
                    text = extract_text(f)
                    if text.strip():
                        docs.append({"name": f.name, "text": text})
                if docs:
                    st.session_state["upload_docs"]   = docs
                    st.session_state["upload_result"] = None
                    with st.spinner("Claude analysiert deine Kursmaterialien…"):
                        try:
                            st.session_state["upload_result"] = synthesize_from_documents(
                                docs, course_title, api_key
                            )
                        except Exception as exc:
                            st.error(f"Fehler: {exc}")
                    st.rerun()
            elif run_upload:
                st.warning("Bitte mindestens eine Datei hochladen.")

            if st.button("Zurücksetzen", use_container_width=True):
                st.session_state.pop("upload_docs", None)
                st.session_state.pop("upload_result", None)
                st.rerun()

        else:
            api_key = course_title = ""

    # View rendern
    if nav == "Analyse":
        view_analyse(api_key, topic, selected, year_from, year_to, max_papers, peer_review_only, run)
    elif nav == "Kurs":
        view_upload(api_key)
    elif nav == "Favoriten":
        view_favorites()
    else:
        view_history()


if __name__ == "__main__":
    main()
