"""
SciSynth — Transdisziplinäre Forschungsexploration
"""

import streamlit as st
import arxiv
import anthropic
import json
import requests
import hashlib
from pathlib import Path
from datetime import datetime

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

/* Nav radio */
[data-testid="stSidebar"] .stRadio > div {
    display: flex !important;
    gap: 4px !important;
    background: #f3f4f6 !important;
    border-radius: 8px !important;
    padding: 3px !important;
}
[data-testid="stSidebar"] .stRadio label {
    flex: 1 !important;
    text-align: center !important;
    border-radius: 6px !important;
    padding: 5px 8px !important;
    font-size: 0.82em !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    color: #6b7280 !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
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


def _quality_score(cited: int, pub_date: str, paper_type: str) -> float:
    """Composite-Score: 40% Zitationen + 60% Zitationsgeschwindigkeit × Peer-Review-Bonus."""
    year = int((pub_date or "2020")[:4])
    age  = max(2025 - year, 1)
    velocity     = cited / age
    peer_bonus   = 1.2 if paper_type == "journal-article" else 1.0
    return (0.4 * cited + 0.6 * velocity) * peer_bonus


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_openalex(oa_query: str, year_from: int, year_to: int,
                    n: int, peer_review_only: bool) -> list[dict]:
    try:
        filter_str = (
            f"has_abstract:true,"
            f"from_publication_date:{year_from}-01-01,"
            f"to_publication_date:{year_to}-12-31"
        )
        if peer_review_only:
            filter_str += ",type:journal-article"

        # Doppelte Menge abrufen, danach nach Score filtern
        resp = requests.get(
            "https://api.openalex.org/works",
            params={
                "search":   oa_query,
                "filter":   filter_str,
                "sort":     "publication_date:desc",
                "per_page": min(n * 2, 50),
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
            score     = _quality_score(cited, pub_date, ptype)
            papers.append({
                "title":   w.get("title") or "",
                "short":   abstract[:420] + "…" if len(abstract) > 420 else abstract,
                "full":    abstract,
                "authors": ", ".join(auths) + suffix if auths else "–",
                "date":    pub_date[:7],
                "url":     url,
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
def fetch_papers(disciplines: tuple[str, ...], query: str, year_from: int, year_to: int,
                 max_per: int, dynamic_queries: tuple[tuple[str, str], ...],
                 peer_review_only: bool) -> dict[str, list[dict]]:
    dq_map = dict(dynamic_queries)  # discipline → optimized query
    result: dict[str, list[dict]] = {}
    half = max(max_per // 2, 2)
    seen_globally: set[str] = set()  # dedup across all disciplines

    for discipline in disciplines:
        papers: list[dict] = []

        # arXiv (STEM)
        cats = ARXIV_CATS.get(discipline)
        if cats:
            for p in _fetch_arxiv(tuple(cats), query, year_from, year_to, half * 2):
                key = p["title"].lower()[:60]
                if key not in seen_globally:
                    papers.append(p)

        # OpenAlex — dynamische Query (bereits englisch und themenbezogen) oder statischer Fallback
        # Rohes Nutzerthema NICHT anhängen: Claude hat es bereits in die dynamische Query integriert;
        # deutschsprachiger Text würde OpenAlex-Treffer verschlechtern.
        oa_q = dq_map.get(discipline) or OPENALEX_QUERIES.get(discipline, "")
        if oa_q:
            oa_papers = _fetch_openalex(oa_q, year_from, year_to, half * 2, peer_review_only)
            seen_local = {p["title"].lower()[:60] for p in papers}
            for p in oa_papers:
                key = p["title"].lower()[:60]
                if key not in seen_globally and key not in seen_local:
                    papers.append(p)
                    seen_local.add(key)

        kept = papers[:max_per]
        if kept:
            result[discipline] = kept
            seen_globally.update(p["title"].lower()[:60] for p in kept)

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
    "interdisciplinary_tension": "<Wo könnten die Disziplinen in Konflikt geraten und wie löst man das>"
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

def generate_search_queries(disciplines: tuple[str, ...], topic: str, api_key: str) -> dict[str, str]:
    """Lässt Claude optimierte Suchbegriffe pro Disziplin generieren."""
    client    = anthropic.Anthropic(api_key=api_key)
    disc_list = "\n".join(f"- {d}" for d in disciplines)
    prompt    = f"""Generiere für jede Disziplin einen präzisen englischen Suchbegriff (4–7 Wörter) für OpenAlex.

Forschungsthema: "{topic or 'Offene transdisziplinäre Exploration'}"

Disziplinen:
{disc_list}

Regeln:
- Englisch, akademisch, spezifisch
- Berücksichtige das Forschungsthema wo sinnvoll
- Keine generischen Begriffe wie "research" oder "study"

Antworte NUR mit diesem JSON:
{{"<Disziplinname>": "<Suchbegriff>"}}"""

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=800,
        system="Du antwortest ausschließlich mit validem JSON.",
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text  = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


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
    s_css = ("background:#f0fdfa;color:#0f766e;border:1px solid #99f6e4"
             if src == "arXiv" else
             "background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe")
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

        nav = st.radio(
            "nav", ["Analyse", "Favoriten", "Verlauf"],
            horizontal=True, label_visibility="collapsed",
            index=["Analyse", "Favoriten", "Verlauf"].index(
                st.session_state.get("nav", "Analyse")
            ),
        )
        st.session_state.nav = nav
        st.markdown("---")

        if nav == "Analyse":
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
        else:
            api_key = topic = ""
            year_from = year_to = 2025
            selected = []
            max_papers = 4
            peer_review_only = False
            run = False

    # View rendern
    if nav == "Analyse":
        view_analyse(api_key, topic, selected, year_from, year_to, max_papers, peer_review_only, run)
    elif nav == "Favoriten":
        view_favorites()
    else:
        view_history()


if __name__ == "__main__":
    main()
