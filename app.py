"""
app.py – Sawt Taleb | صوت الطالب
Platform for Algerian university students to report conditions and advocate for change.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
import io
import hashlib
import uuid
from datetime import datetime, timedelta
import random

import database as db

# ─────────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Sawt Taleb | صوت الطالب",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SESSION STATE BOOTSTRAP
# ─────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "page" not in st.session_state:
    st.session_state["page"] = "🏠 Accueil"
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
if "submit_success" not in st.session_state:
    st.session_state["submit_success"] = None
if "view_report_id" not in st.session_state:
    st.session_state["view_report_id"] = None

SESSION_HASH = hashlib.sha256(st.session_state["session_id"].encode()).hexdigest()[:32]

# ─────────────────────────────────────────────
# DB INIT
# ─────────────────────────────────────────────
db.init_db()

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SEVERITY_COLORS = {1: "#22c55e", 2: "#84cc16", 3: "#f59e0b", 4: "#f97316", 5: "#ef4444"}
SEVERITY_LABELS = {1: "Très faible 🟢", 2: "Faible 🟡", 3: "Modéré 🟠", 4: "Grave 🔴", 5: "Critique 🚨"}
STATUS_COLORS   = db.STATUS_COLORS
CATEGORY_ICONS  = {cat.split(" ")[0]: cat for cat in db.CATEGORIES.keys()}

PAGES = ["home", "submit", "browse", "dashboard", "union", "about"]

# Simple translations dictionary (key -> {lang: text})
TRANSLATIONS = {
    # Navigation
    "nav.home": {"fr": "🏠 Accueil", "en": "🏠 Home", "ar": "🏠 الرئيسية"},
    "nav.submit": {"fr": "📝 Soumettre un Signalement", "en": "📝 Submit Report", "ar": "📝 تقديم بلاغ"},
    "nav.browse": {"fr": "🔍 Explorer les Signalements", "en": "🔍 Explore Reports", "ar": "🔍 استعرض البلاغات"},
    "nav.dashboard": {"fr": "📊 Tableau de Bord", "en": "📊 Dashboard", "ar": "📊 لوحة القيادة"},
    "nav.union": {"fr": "🏛️ Portail Union Étudiante", "en": "🏛️ Student Union Portal", "ar": "🏛️ بوابة اتحاد الطلبة"},
    "nav.about": {"fr": "ℹ️ À Propos & Aide", "en": "ℹ️ About & Help", "ar": "ℹ️ حول ومساعدة"},

    # Hero
    "hero.title": {
        "fr": "Sawt Taleb",
        "en": "Sawt Taleb",
        "ar": "صوت الطالب",
    },
    "hero.subtitle": {
        "fr": "La plateforme des étudiants algériens pour signaler les conditions universitaires inacceptables, partager des preuves visuelles et pousser pour le changement.",
        "en": "A platform for Algerian students to report unacceptable university and dorm conditions, share photographic evidence, and push for change.",
        "ar": "منصة لطلبة الجزائر للإبلاغ عن ظروف الجامعة والسكن غير المقبولة، ومشاركة الأدلة المرئية والدفع نحو التغيير.",
    },
    "announce": {
        "fr": "📢 Nouveau : Les syndicats étudiants peuvent désormais accéder au Portail Union Étudiante pour exporter des rapports et générer des lettres d'advocacy officielles.",
        "en": "📢 New: Student unions can now access the Student Union Portal to export reports and generate official advocacy letters.",
        "ar": "📢 جديد: يمكن لاتحادات الطلبة الآن الوصول إلى بوابة اتحاد الطلبة لتصدير التقارير وإنشاء رسائل مناصرة رسمية.",
    },

    # Metrics
    "metric.total": {"fr": "Signalements total", "en": "Total reports", "ar": "إجمالي البلاغات"},
    "metric.pending": {"fr": "En attente", "en": "Pending", "ar": "قيد الانتظار"},
    "metric.resolved": {"fr": "Résolus", "en": "Resolved", "ar": "محلول"},
    "metric.universities": {"fr": "Universités couvertes", "en": "Universities covered", "ar": "الجامعات المشمولة"},
    "metric.avg_severity": {"fr": "Gravité moyenne", "en": "Average severity", "ar": "شدة متوسطة"},

    # Sections
    "overview.title": {"fr": "📈 Aperçu de la plateforme", "en": "📈 Platform overview", "ar": "📈 نظرة عامة"},
    "wilaya.title": {"fr": "🗺️ Signalements par Wilaya", "en": "🗺️ Reports by Wilaya", "ar": "🗺️ البلاغات بحسب الولاية"},
    "recent.title": {"fr": "🕒 Derniers signalements", "en": "🕒 Recent reports", "ar": "🕒 البلاغات الأخيرة"},
    "how.title": {"fr": "⚙️ Comment ça marche", "en": "⚙️ How it works", "ar": "⚙️ كيف تعمل المنصة"},

    # How it works steps
    "how.step1.title": {"fr": "Signalez", "en": "Report", "ar": "أبلِغ"},
    "how.step1.desc": {"fr": "Décrivez le problème rencontré dans votre université ou résidence.", "en": "Describe the problem you encountered at your university or dorm.", "ar": "صف المشكلة التي تواجهها في جامعتك أو سكنك."},
    "how.step2.title": {"fr": "Documentez", "en": "Document", "ar": "وثق"},
    "how.step2.desc": {"fr": "Ajoutez des photos pour appuyer votre signalement.", "en": "Add photos to support your report.", "ar": "أضف صورًا لدعم بلاغك."},
    "how.step3.title": {"fr": "Soutenez", "en": "Support", "ar": "ادعم"},
    "how.step3.desc": {"fr": "Votez pour les signalements qui vous concernent aussi.", "en": "Upvote reports that affect you too.", "ar": "صوّت للبلاغات التي تؤثر عليك أيضًا."},
    "how.step4.title": {"fr": "Impactez", "en": "Impact", "ar": "أثر"},
    "how.step4.desc": {"fr": "Les unions étudiantes utilisent les données pour agir.", "en": "Student unions use the data to take action.", "ar": "تستخدم اتحادات الطلبة البيانات لاتخاذ إجراءات."},

    # Submit page
    "submit.title": {"fr": "📝 Soumettre un Signalement", "en": "📝 Submit a Report", "ar": "📝 تقديم بلاغ"},
    "submit.subtitle": {"fr": "Votre voix compte. Décrivez le problème en détail pour maximiser l'impact.", "en": "Your voice matters. Describe the issue in detail to maximize impact.", "ar": "صوتك مهم. صِف المشكلة بتفصيل لزيادة أثر البلاغ."},
    "submit.success": {"fr": "✅ Signalement #{id} soumis avec succès ! Merci pour votre contribution.", "en": "✅ Report #{id} submitted successfully! Thank you for your contribution.", "ar": "✅ تم تقديم البلاغ رقم #{id} بنجاح! شكرًا لمساهمتك."},
    "submit.another": {"fr": "Soumettre un autre signalement", "en": "Submit another report", "ar": "تقديم بلاغ آخر"},

    # Browse
    "browse.title": {"fr": "🔍 Explorer les Signalements", "en": "🔍 Explore Reports", "ar": "🔍 استعرض البلاغات"},
    "browse.filters": {"fr": "🔧 Filtres", "en": "🔧 Filters", "ar": "🔧 مرشحات"},
    "browse.search.placeholder": {"fr": "Mots-clés…", "en": "Keywords…", "ar": "الكلمات المفتاحية…"},
    "browse.found": {"fr": "{n} signalement(s) trouvé(s)", "en": "{n} report(s) found", "ar": "{n} بلاغ(ات) تم العثور عليها"},

    # Dashboard
    "dashboard.title": {"fr": "📊 Tableau de Bord par Université", "en": "📊 Dashboard by University", "ar": "📊 لوحة لكل جامعة"},

    # Union portal
    "union.title": {"fr": "🏛️ Portail Union Étudiante", "en": "🏛️ Student Union Portal", "ar": "🏛️ بوابة اتحاد الطلبة"},

    # About
    "about.title": {"fr": "ℹ️ À Propos de Sawt Taleb", "en": "ℹ️ About Sawt Taleb", "ar": "ℹ️ حول صوت الطالب"},
}


def t(key, **kwargs):
    """Return translated string for current session language."""
    lang = st.session_state.get("lang", "en")
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get("en") or entry.get("fr") or key
    try:
        return text.format(**kwargs)
    except Exception:
        return text


# Add a few common label translations
TRANSLATIONS.update({
    "label.month": {"fr": "Mois", "en": "Month", "ar": "الشهر"},
    "label.reports": {"fr": "Signalements", "en": "Reports", "ar": "بلاغات"},
    "category.breakdown": {"fr": "Répartition par catégorie", "en": "Category breakdown", "ar": "التوزيع حسب الفئة"},
    "how.title": {"fr": "⚙️ Comment ça marche", "en": "⚙️ How it works", "ar": "⚙️ كيف تعمل المنصة"},
})

TRANSLATIONS.update({
    "submit.visible": {
        "fr": "🔍 Votre signalement est maintenant visible dans la section \"Explorer les Signalements\" et sera examiné par les équipes concernées.",
        "en": "🔍 Your report is now visible in the \"Explore Reports\" section and will be reviewed by the relevant teams.",
        "ar": "🔍 تم الآن نشر بلاغك في قسم \"استعرض البلاغات\" وسيراجعه الفريق المعني.",
    }
})

TRANSLATIONS.update({
    "submit.button": {"fr": "🚀 Soumettre le Signalement", "en": "🚀 Submit Report", "ar": "🚀 إرسال البلاغ"},
})

TRANSLATIONS.update({
    "browse.no_results": {
        "fr": "Aucun signalement ne correspond à vos critères. Essayez d'élargir les filtres.",
        "en": "No reports match your filters. Try broadening your search.",
        "ar": "لا يوجد بلاغ يطابق معاييرك. حاول توسيع المرشحات.",
    }
})

TRANSLATIONS.update({
    "dashboard.select_info": {
        "fr": "Sélectionnez une université pour analyser ses signalements en détail.",
        "en": "Select a university to analyze its reports in detail.",
        "ar": "اختر جامعة لتحليل بلاغاتها بالتفصيل.",
    }
})

TRANSLATIONS.update({
    "union.subtitle": {
        "fr": "Outils d'analyse et d'advocacy pour les syndicats et unions d'étudiants algériens.",
        "en": "Analytics and advocacy tools for student unions and associations.",
        "ar": "أدوات التحليل والمناصرة لاتحادات وجمعيات الطلبة.",
    },
    "union.stats_title": {"fr": "📊 Statistiques nationales", "en": "📊 National statistics", "ar": "📊 إحصاءات وطنية"},
})

TRANSLATIONS.update({
    "about.subtitle": {
        "fr": "Une plateforme indépendante, par et pour les étudiants algériens.",
        "en": "An independent platform by and for Algerian students.",
        "ar": "منصة مستقلة من أجل ومن قِبل طلبة الجزائر.",
    }
})

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    /* RTL support */
    .rtl { direction: rtl; text-align: right; }
    .rtl .hero { direction: rtl; }
    .rtl .hero p { text-align: right; }
    .rtl .report-desc, .rtl .report-meta, .rtl .comment-bubble { text-align: right; }

    /* ── Hide default Streamlit branding ── */
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064e3b 0%, #065f46 60%, #047857 100%);
    }
    [data-testid="stSidebar"] * { color: #ecfdf5 !important; }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem; padding: 6px 0; cursor: pointer;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

    /* ── Hero banner ── */
    .hero {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #059669 100%);
        border-radius: 16px; padding: 40px 48px; color: white; margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(6,78,59,0.3);
    }
    .hero h1 { font-size: 2.6rem; font-weight: 700; margin: 0 0 6px; }
    .hero .arabic { font-size: 1.8rem; opacity: 0.85; direction: rtl; }
    .hero p { font-size: 1.05rem; opacity: 0.9; margin-top: 12px; max-width: 640px; }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 150px;
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-top: 4px solid #059669;
        text-align: center;
    }
    .metric-card .value { font-size: 2.2rem; font-weight: 700; color: #064e3b; }
    .metric-card .label { font-size: 0.82rem; color: #6b7280; margin-top: 4px; font-weight: 500; }
    .metric-card.red   { border-top-color: #ef4444; }
    .metric-card.amber { border-top-color: #f59e0b; }
    .metric-card.blue  { border-top-color: #3b82f6; }

    /* ── Report cards ── */
    .report-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        border-left: 5px solid #059669;
        margin-bottom: 16px;
        transition: box-shadow 0.2s;
    }
    .report-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
    .report-card.sev-1 { border-left-color: #22c55e; }
    .report-card.sev-2 { border-left-color: #84cc16; }
    .report-card.sev-3 { border-left-color: #f59e0b; }
    .report-card.sev-4 { border-left-color: #f97316; }
    .report-card.sev-5 { border-left-color: #ef4444; }

    .report-title { font-size: 1.05rem; font-weight: 600; color: #1f2937; margin-bottom: 6px; }
    .report-meta  { font-size: 0.78rem; color: #6b7280; margin-bottom: 8px; }
    .report-desc  { font-size: 0.88rem; color: #374151; line-height: 1.5; }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .badge-category { background: #eff6ff; color: #1d4ed8; }
    .badge-location { background: #f0fdf4; color: #15803d; }
    .badge-status-Signalé                  { background: #fef2f2; color: #dc2626; }
    .badge-status-en_cours_examen          { background: #fefce8; color: #ca8a04; }
    .badge-status-en_cours_resolution      { background: #eff6ff; color: #2563eb; }
    .badge-status-Résolu                   { background: #f0fdf4; color: #16a34a; }
    .badge-status-Rejeté                   { background: #f9fafb; color: #6b7280; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.35rem; font-weight: 700; color: #064e3b;
        border-bottom: 3px solid #059669;
        padding-bottom: 8px; margin: 28px 0 18px;
    }

    /* ── Severity selector ── */
    .sev-pill {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 99px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 4px;
    }

    /* ── Priority table ── */
    .priority-item {
        background: white;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }
    .priority-rank {
        font-size: 1.4rem;
        font-weight: 700;
        color: #9ca3af;
        width: 32px;
        text-align: center;
    }

    /* ── Comment box ── */
    .comment-bubble {
        background: #f9fafb;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-left: 3px solid #d1d5db;
    }
    .comment-author { font-weight: 600; font-size: 0.82rem; color: #374151; }
    .comment-time   { font-size: 0.75rem; color: #9ca3af; }
    .comment-text   { margin-top: 6px; font-size: 0.88rem; color: #4b5563; }

    /* ── Announcement bar ── */
    .announce {
        background: linear-gradient(90deg, #fef9c3, #fef3c7);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: #78350f;
    }

    /* ── Steps ── */
    .step-box {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }
    .step-num {
        background: #059669;
        color: white;
        width: 36px; height: 36px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1rem;
        margin: 0 auto 12px;
    }

    /* ── Info box ── */
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 16px 20px;
        color: #1e40af;
        font-size: 0.9rem;
    }
    .warn-box {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 10px;
        padding: 16px 20px;
        color: #9a3412;
        font-size: 0.9rem;
    }

    /* ── Footer ── */
    .app-footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.78rem;
        margin-top: 48px;
        padding-top: 24px;
        border-top: 1px solid #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def status_badge(status):
    key = status.replace(" ", "_").replace("'", "")
    color = STATUS_COLORS.get(status, "#6b7280")
    return f'<span class="badge" style="background:{color}22;color:{color}">{status}</span>'


def severity_badge(sev):
    color = SEVERITY_COLORS.get(sev, "#6b7280")
    label = SEVERITY_LABELS.get(sev, str(sev))
    return f'<span class="badge" style="background:{color}22;color:{color}">{label}</span>'


def img_to_b64(uploaded_file):
    """Convert uploaded file to base64 string."""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((1200, 1200), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def display_image(b64_str, caption="", width=None):
    html = f'<img src="data:image/jpeg;base64,{b64_str}" style="border-radius:8px;max-width:100%;{f"width:{width}px;" if width else ""}" alt="{caption}"/>'
    if caption:
        html += f'<p style="font-size:0.78rem;color:#6b7280;margin-top:4px;text-align:center">{caption}</p>'
    st.markdown(html, unsafe_allow_html=True)


def format_date(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - dt
        if delta.days == 0:
            if delta.seconds < 3600:
                return f"il y a {delta.seconds // 60} min"
            return f"il y a {delta.seconds // 3600}h"
        if delta.days == 1:
            return "hier"
        if delta.days < 7:
            return f"il y a {delta.days} jours"
        if delta.days < 30:
            return f"il y a {delta.days // 7} sem."
        return dt.strftime("%d %b %Y")
    except Exception:
        return dt_str


def render_report_card(report, show_detail_btn=True):
    """Render a report as an HTML card with a Streamlit expander for details."""
    sev   = report["severity"]
    color = SEVERITY_COLORS.get(sev, "#6b7280")
    label = SEVERITY_LABELS.get(sev, str(sev))
    desc_preview = report["description"][:200] + ("…" if len(report["description"]) > 200 else "")

    html = f"""
    <div class="report-card sev-{sev}">
      <div class="report-title">#{report['id']} — {report['title']}</div>
      <div class="report-meta">
        🏫 {report['university_name']} &nbsp;|&nbsp;
        📍 {report['location_type']} &nbsp;|&nbsp;
        🕒 {format_date(report['created_at'])}
      </div>
      <div style="margin-bottom:8px">
        <span class="badge badge-category">{report['category']}</span>
        <span class="badge badge-location">{report.get('subcategory','')}</span>
        {status_badge(report['status'])}
        <span class="badge" style="background:{color}22;color:{color}">{label}</span>
      </div>
      <div class="report-desc">{desc_preview}</div>
      <div style="margin-top:10px;font-size:0.82rem;color:#6b7280">
        👍 {report['upvotes']} soutiens
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: ACCUEIL
# ─────────────────────────────────────────────
def show_home():
    st.markdown(f"""
    <div class="hero">
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="announce">{t("announce")}</div>', unsafe_allow_html=True)

    # ── Stats ──
    stats = db.get_platform_stats()
    col1, col2, col3, col4, col5 = st.columns(5)
    cards = [
        (col1, stats["total"],        t("metric.total"),    ""),
        (col2, stats["pending"],      t("metric.pending"),  "red"),
        (col3, stats["resolved"],     t("metric.resolved"), ""),
        (col4, stats["universities"], t("metric.universities"), "blue"),
        (col5, f"{stats['avg_severity']:.1f}/5", t("metric.avg_severity"), "amber"),
    ]
    for col, val, lbl, cls in cards:
        with col:
            st.markdown(
                f'<div class="metric-card {cls}"><div class="value">{val}</div><div class="label">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(f'<div class="section-header">{t("overview.title")}</div>', unsafe_allow_html=True)

    # ── Charts row ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Timeline chart
        timeline = db.get_timeline_data(days=180)
        if timeline:
            df_time = pd.DataFrame(timeline)
            fig = px.area(
                df_time, x="month", y="count",
                labels={"month": t('label.month'), "count": t('label.reports')},
                title=t('overview.title'),
                color_discrete_sequence=["#059669"],
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"), margin=dict(t=40, b=20, l=20, r=20),
                title_font_size=14,
            )
            fig.update_traces(fillcolor="rgba(5,150,105,0.15)", line_color="#059669")
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Category donut
        cats = db.get_category_breakdown()
        if cats:
            df_cat = pd.DataFrame(cats)
            df_cat["label"] = df_cat["category"].str.split(" ").str[0]
            fig2 = px.pie(
                df_cat, values="count", names="category",
                title=t('category.breakdown'),
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig2.update_layout(
                font=dict(family="Inter"), margin=dict(t=40, b=0, l=0, r=0),
                legend=dict(font=dict(size=10)), title_font_size=14,
                showlegend=True,
            )
            fig2.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(fig2, use_container_width=True)

    # ── Wilaya bar chart ──
    st.markdown(f'<div class="section-header">{t("wilaya.title")}</div>', unsafe_allow_html=True)
    wilayas = db.get_wilaya_breakdown()
    if wilayas:
        df_w = pd.DataFrame(wilayas).head(15)
        fig3 = px.bar(
            df_w, x="count", y="wilaya", orientation="h",
            labels={"count": "Signalements", "wilaya": "Wilaya"},
            color="count",
            color_continuous_scale=[[0, "#bbf7d0"], [0.5, "#059669"], [1, "#064e3b"]],
        )
        fig3.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter"), margin=dict(t=20, b=20, l=20, r=20),
            coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
            height=420,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Recent reports ──
    st.markdown(f'<div class="section-header">{t("recent.title")}</div>', unsafe_allow_html=True)
    recent = db.get_reports(sort_by="newest", limit=6)
    if recent:
        cols = st.columns(2)
        for i, r in enumerate(recent):
            with cols[i % 2]:
                render_report_card(r)
    else:
        st.info("Aucun signalement pour le moment. Soyez le premier à signaler !")

    # ── How it works ──
    st.markdown(f'<div class="section-header">{t("how.title")}</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    steps = [
        ("1", "📝", t("how.step1.title"), t("how.step1.desc")),
        ("2", "📸", t("how.step2.title"), t("how.step2.desc")),
        ("3", "👍", t("how.step3.title"), t("how.step3.desc")),
        ("4", "📊", t("how.step4.title"), t("how.step4.desc")),
    ]
    for col, (num, icon, title, desc) in zip([s1, s2, s3, s4], steps):
        with col:
            st.markdown(
                f'<div class="step-box"><div class="step-num">{num}</div>'
                f'<div style="font-size:2rem">{icon}</div>'
                f'<strong style="color:#064e3b">{title}</strong>'
                f'<p style="font-size:0.84rem;color:#6b7280;margin-top:8px">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    _footer()


# ─────────────────────────────────────────────
# PAGE: SUBMIT REPORT
# ─────────────────────────────────────────────
def show_submit_report():
    st.markdown(f'<div class="hero" style="padding:28px 40px"><h1 style="font-size:1.8rem">{t("submit.title")}</h1><p style="margin-top:8px">{t("submit.subtitle")}</p></div>', unsafe_allow_html=True)

    # Success message
    if st.session_state.get("submit_success"):
        rid = st.session_state["submit_success"]
        st.success(t("submit.success", id=rid))
        st.markdown(f'<div class="info-box">{t("submit.visible")}</div>', unsafe_allow_html=True)
        if st.button(t("submit.another")):
            st.session_state["submit_success"] = None
            st.rerun()
        return

    universities = db.get_universities()
    uni_map = {u["name"]: u["id"] for u in universities}
    wilayas = sorted(set(u["wilaya"] for u in universities))

    with st.form("report_form", clear_on_submit=False):
        st.markdown("### 🏫 Étape 1 – Identification de l'établissement")
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_wilaya = st.selectbox("Wilaya *", ["(Toutes)"] + wilayas)
        with col2:
            filtered_unis = [u["name"] for u in universities
                             if selected_wilaya == "(Toutes)" or u["wilaya"] == selected_wilaya]
            selected_uni_name = st.selectbox("Université / École *", filtered_unis)

        location_type = st.selectbox("Lieu concerné *", db.LOCATION_TYPES)

        st.divider()
        st.markdown("### 🗂️ Étape 2 – Classification du problème")
        col3, col4 = st.columns(2)
        with col3:
            selected_category = st.selectbox("Catégorie principale *", list(db.CATEGORIES.keys()))
        with col4:
            subcats = db.CATEGORIES.get(selected_category, ["Autre"])
            selected_subcat = st.selectbox("Sous-catégorie *", subcats)

        st.markdown("**Niveau de gravité** *")
        severity = st.slider(
            "Gravité (1 = très faible, 5 = critique)", 1, 5, 3,
            help="1: Inconfort mineur | 3: Problème sérieux | 5: Urgence/danger",
        )
        sev_color = SEVERITY_COLORS[severity]
        sev_label = SEVERITY_LABELS[severity]
        st.markdown(
            f'<div style="background:{sev_color}22;border-left:4px solid {sev_color};'
            f'border-radius:8px;padding:10px 16px;color:{sev_color};font-weight:600">'
            f'Gravité sélectionnée : {sev_label}</div>',
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("### ✍️ Étape 3 – Description du problème")
        title = st.text_input(
            "Titre du signalement *",
            placeholder="Ex: Fuite de toiture dans l'Amphi B depuis 2 semaines",
            max_chars=120,
        )
        description = st.text_area(
            "Description détaillée *",
            placeholder=(
                "Décrivez le problème en détail :\n"
                "– Depuis quand existe-t-il ?\n"
                "– Combien d'étudiants sont affectés ?\n"
                "– L'administration a-t-elle été informée ?\n"
                "– Quelles conséquences cela entraîne-t-il ?"
            ),
            height=200,
            max_chars=2000,
        )
        st.caption(f"{'('+str(len(description))+'/2000 caractères)' if description else '0/2000 caractères'}")

        st.divider()
        st.markdown("### 📸 Étape 4 – Preuves photographiques (optionnel)")
        st.markdown(
            '<div class="info-box">📷 Ajoutez jusqu\'à <strong>5 photos</strong> pour appuyer votre signalement. '
            'Les images seront redimensionnées automatiquement (max 10 Mo par fichier).</div>',
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "Télécharger des photos",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            if len(uploaded_files) > 5:
                st.warning("⚠️ Maximum 5 photos. Seules les 5 premières seront prises en compte.")
                uploaded_files = uploaded_files[:5]
            preview_cols = st.columns(len(uploaded_files))
            for i, f in enumerate(uploaded_files):
                with preview_cols[i]:
                    st.image(f, use_container_width=True, caption=f"Photo {i+1}")

        captions = []
        if uploaded_files:
            st.markdown("**Légendes des photos (optionnel)**")
            for i, f in enumerate(uploaded_files[:5]):
                cap = st.text_input(f"Légende photo {i+1}", placeholder="Description courte…", key=f"cap_{i}")
                captions.append(cap)

        st.divider()
        st.markdown("### 👤 Étape 5 – Vos coordonnées (optionnel)")
        is_anon = st.checkbox("Soumettre de manière anonyme", value=True)
        reporter_name  = ""
        reporter_email = ""
        if not is_anon:
            col5, col6 = st.columns(2)
            with col5:
                reporter_name = st.text_input("Prénom et Nom", max_chars=80)
            with col6:
                reporter_email = st.text_input("Email universitaire", placeholder="prenom.nom@univ-xx.dz")
            st.markdown(
                '<div class="warn-box">🔒 Vos coordonnées ne seront <strong>jamais partagées publiquement</strong>. '
                'Elles servent uniquement à vous contacter si nécessaire.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="info-box">🕵️ Mode anonyme activé – votre identité sera complètement protégée.</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("### ✅ Étape 6 – Confirmation")
        agree = st.checkbox(
            "Je certifie que ces informations sont exactes et de bonne foi. "
            "Je comprends que les faux signalements nuisent à la crédibilité de la plateforme."
        )

        submitted = st.form_submit_button(
            t("submit.button"),
            use_container_width=True,
            type="primary",
        )

    if submitted:
        errors = []
        if not selected_uni_name:
            errors.append("Université requise.")
        if not title or len(title.strip()) < 10:
            errors.append("Titre trop court (minimum 10 caractères).")
        if not description or len(description.strip()) < 30:
            errors.append("Description trop courte (minimum 30 caractères).")
        if not agree:
            errors.append("Vous devez cocher la case de confirmation.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            uni_id = uni_map[selected_uni_name]
            report_id = db.add_report(
                university_id=uni_id,
                location_type=location_type,
                category=selected_category,
                subcategory=selected_subcat,
                severity=severity,
                title=title.strip(),
                description=description.strip(),
                reporter_name=reporter_name if not is_anon else None,
                reporter_email=reporter_email if not is_anon else None,
                is_anonymous=is_anon,
            )
            # Save images
            if uploaded_files:
                imgs = []
                for i, f in enumerate(uploaded_files[:5]):
                    b64 = img_to_b64(f)
                    if b64:
                        imgs.append((b64, captions[i] if i < len(captions) else ""))
                if imgs:
                    db.add_images(report_id, imgs)

            st.session_state["submit_success"] = report_id
            st.rerun()

    _footer()


# ─────────────────────────────────────────────
# PAGE: BROWSE REPORTS
# ─────────────────────────────────────────────
def show_browse_reports():
    st.markdown(f"## {t('browse.title')}")

    universities = db.get_universities()
    uni_options  = {"(Toutes les universités)": None}
    for u in universities:
        uni_options[u["name"]] = u["id"]

    # ── Sidebar filters ──
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {t('browse.filters')}")
        search_q    = st.text_input("🔎 ", placeholder=t('browse.search.placeholder'))
        sel_uni     = st.selectbox("Université", list(uni_options.keys()), key="browse_uni")
        sel_cat     = st.selectbox("Catégorie", ["(Toutes)"] + list(db.CATEGORIES.keys()), key="browse_cat")
        sel_loc     = st.selectbox("Lieu", ["(Tous)"] + db.LOCATION_TYPES, key="browse_loc")
        sev_range   = st.slider("Gravité", 1, 5, (1, 5), key="browse_sev")
        sel_status  = st.selectbox("Statut", ["(Tous)"] + db.STATUS_OPTIONS, key="browse_status")
        sort_by     = st.selectbox("Trier par", {
            "newest":     "Plus récents",
            "most_voted": "Plus soutenus",
            "severity":   "Plus graves",
            "oldest":     "Plus anciens",
        }.keys(), format_func=lambda k: {"newest":"Plus récents","most_voted":"Plus soutenus","severity":"Plus graves","oldest":"Plus anciens"}[k])
        st.markdown("---")

    uid     = uni_options.get(sel_uni)
    cat     = None if sel_cat == "(Toutes)" else sel_cat
    loc     = None if sel_loc == "(Tous)" else sel_loc
    status  = None if sel_status == "(Tous)" else sel_status
    q       = search_q.strip() if search_q else None

    reports = db.get_reports(
        university_id=uid,
        category=cat,
        location_type=loc,
        min_severity=sev_range[0],
        max_severity=sev_range[1],
        status=status,
        search_query=q,
        sort_by=sort_by,
    )

    st.markdown(f"**{t('browse.found', n=len(reports))}**")

    if not reports:
        st.info(t('browse.no_results'))
        return

    # ── Report list with detail expander ──
    for r in reports:
        sev   = r["severity"]
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        label = SEVERITY_LABELS.get(sev, str(sev))

        with st.expander(
            f"**#{r['id']}** — {r['title']}  |  {r['university_name']}  |  {label}",
            expanded=False,
        ):
            col_info, col_actions = st.columns([3, 1])

            with col_info:
                st.markdown(f"""
                <div style="margin-bottom:10px">
                  <span class="badge badge-category">{r['category']}</span>
                  <span class="badge badge-location">{r.get('subcategory','')}</span>
                  {status_badge(r['status'])}
                  {severity_badge(r['severity'])}
                </div>
                <p style="font-size:0.82rem;color:#6b7280">
                  📍 {r['location_type']} &nbsp;|&nbsp; 🏫 {r['university_name']} ({r['wilaya']})
                  &nbsp;|&nbsp; 🕒 {format_date(r['created_at'])}
                </p>
                <p style="margin-top:12px;line-height:1.7">{r['description']}</p>
                """, unsafe_allow_html=True)

                # Images
                images = db.get_images_for_report(r["id"])
                if images:
                    st.markdown("**📸 Photos :**")
                    img_cols = st.columns(min(len(images), 3))
                    for j, img in enumerate(images[:3]):
                        with img_cols[j]:
                            display_image(img["image_data"], img.get("caption", ""))

            with col_actions:
                already = db.has_upvoted(r["id"], SESSION_HASH)
                btn_label = f"{'❤️' if already else '🤍'} Soutenir ({r['upvotes']})"
                if st.button(btn_label, key=f"upvote_{r['id']}"):
                    new_count = db.toggle_upvote(r["id"], SESSION_HASH)
                    st.rerun()

                # Status update (admin-like for demo)
                st.markdown("**Mettre à jour le statut :**")
                new_status = st.selectbox(
                    "Statut", db.STATUS_OPTIONS,
                    index=db.STATUS_OPTIONS.index(r["status"]) if r["status"] in db.STATUS_OPTIONS else 0,
                    key=f"status_{r['id']}",
                )
                if st.button("Enregistrer", key=f"save_status_{r['id']}"):
                    db.update_report_status(r["id"], new_status)
                    st.success("Statut mis à jour !")
                    st.rerun()

            # Comments
            st.markdown("---")
            st.markdown("**💬 Commentaires**")
            comments = db.get_comments(r["id"])
            if comments:
                for c in comments:
                    st.markdown(
                        f'<div class="comment-bubble">'
                        f'<span class="comment-author">👤 {c["commenter_name"]}</span>'
                        f'<span class="comment-time"> · {format_date(c["created_at"])}</span>'
                        f'<div class="comment-text">{c["comment_text"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Aucun commentaire. Soyez le premier à réagir.")

            with st.form(f"comment_form_{r['id']}"):
                c_name = st.text_input("Votre nom (optionnel)", value="Anonyme", key=f"cname_{r['id']}")
                c_text = st.text_area("Votre commentaire", height=80, key=f"ctext_{r['id']}")
                if st.form_submit_button("Publier le commentaire"):
                    if c_text.strip():
                        db.add_comment(r["id"], c_text.strip(), c_name or "Anonyme")
                        st.success("Commentaire publié !")
                        st.rerun()
                    else:
                        st.warning("Le commentaire ne peut pas être vide.")

    _footer()


# ─────────────────────────────────────────────
# PAGE: TABLEAU DE BORD
# ─────────────────────────────────────────────
def show_dashboard():
    st.markdown(f"## {t('dashboard.title')}")
    st.markdown(t('dashboard.select_info'))

    universities = db.get_universities()
    uni_names    = [u["name"] for u in universities]
    selected_name = st.selectbox("🏫 Choisir une université", uni_names, key="dash_uni")
    selected_uni  = next(u for u in universities if u["name"] == selected_name)
    uid = selected_uni["id"]

    stats = db.get_university_stats(uid)

    if stats["total"] == 0:
        st.info(f"Aucun signalement enregistré pour {selected_name} pour le moment.")
        return

    # ── Metrics ──
    st.markdown(f"### 📋 Vue d'ensemble — {selected_uni.get('short_name', selected_name)}")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    metrics = [
        (m1, stats["total"],       "Signalements total", ""),
        (m2, stats["open"],        "Non résolus",         "red"),
        (m3, stats["resolved"],    "Résolus",             ""),
        (m4, f"{stats['avg_severity']:.1f}/5", "Gravité moy.", "amber"),
        (m5, f"{stats['resolution_rate']}%", "Taux résolution", "blue"),
        (m6, stats["top_category"].split(" ")[0] if stats["top_category"] != "N/A" else "—",
         "Catégorie principale", ""),
    ]
    for col, val, lbl, cls in metrics:
        with col:
            st.markdown(
                f'<div class="metric-card {cls}"><div class="value" style="font-size:1.6rem">{val}</div>'
                f'<div class="label">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Row 1: Timeline + Category ──
    col_a, col_b = st.columns(2)

    with col_a:
        timeline = db.get_timeline_data(university_id=uid, days=365)
        if timeline:
            df_t = pd.DataFrame(timeline)
            fig = px.bar(
                df_t, x="month", y="count",
                labels={"month": "Mois", "count": "Signalements"},
                title="📅 Évolution mensuelle des signalements",
                color_discrete_sequence=["#059669"],
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"), margin=dict(t=40, b=20, l=10, r=10),
                title_font_size=13,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        cats = db.get_category_breakdown(university_id=uid)
        if cats:
            df_c = pd.DataFrame(cats)
            df_c["emoji"] = df_c["category"].str.split(" ").str[0]
            df_c["name"]  = df_c["category"].str.split(" ", n=1).str[1]
            fig2 = px.pie(
                df_c, values="count", names="category",
                title="🗂️ Répartition par catégorie",
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            fig2.update_layout(
                font=dict(family="Inter"), margin=dict(t=40, b=0, l=0, r=0),
                title_font_size=13, showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Severity + Status + Location ──
    col_c, col_d, col_e = st.columns(3)

    with col_c:
        sevs = db.get_severity_breakdown(university_id=uid)
        if sevs:
            df_s = pd.DataFrame(sevs)
            df_s["label"] = df_s["severity"].map(SEVERITY_LABELS)
            df_s["color"] = df_s["severity"].map(SEVERITY_COLORS)
            fig3 = px.bar(
                df_s, x="label", y="count",
                title="⚠️ Distribution par gravité",
                color="label",
                color_discrete_map={v: SEVERITY_COLORS[k] for k, v in SEVERITY_LABELS.items()},
            )
            fig3.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"), margin=dict(t=40, b=20, l=10, r=10),
                title_font_size=13, showlegend=False,
                xaxis_title="", yaxis_title="Signalements",
            )
            st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        statuses = db.get_status_breakdown(university_id=uid)
        if statuses:
            df_st = pd.DataFrame(statuses)
            status_color_list = [STATUS_COLORS.get(s, "#9ca3af") for s in df_st["status"]]
            fig4 = px.pie(
                df_st, values="count", names="status",
                title="📌 Statut des signalements",
                color="status",
                color_discrete_map=STATUS_COLORS,
            )
            fig4.update_traces(textposition="inside", textinfo="percent+label")
            fig4.update_layout(
                font=dict(family="Inter"), margin=dict(t=40, b=0, l=0, r=0),
                title_font_size=13, showlegend=False,
            )
            st.plotly_chart(fig4, use_container_width=True)

    with col_e:
        locs = db.get_location_breakdown(university_id=uid)
        if locs:
            df_l = pd.DataFrame(locs).head(8)
            fig5 = px.bar(
                df_l, x="count", y="location_type", orientation="h",
                title="📍 Lieux les plus signalés",
                color="count",
                color_continuous_scale=[[0, "#bbf7d0"], [1, "#064e3b"]],
            )
            fig5.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"), margin=dict(t=40, b=20, l=10, r=10),
                title_font_size=13, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"), xaxis_title="", yaxis_title="",
            )
            st.plotly_chart(fig5, use_container_width=True)

    # ── Latest reports for this university ──
    st.markdown(f'<div class="section-header">🕒 Derniers signalements – {selected_uni.get("short_name","")}</div>', unsafe_allow_html=True)
    latest = db.get_reports(university_id=uid, sort_by="newest", limit=6)
    if latest:
        col1, col2 = st.columns(2)
        for i, r in enumerate(latest):
            with col1 if i % 2 == 0 else col2:
                render_report_card(r)

    # ── Export ──
    st.markdown("---")
    all_reports = db.get_reports(university_id=uid)
    if all_reports:
        df_export = pd.DataFrame(all_reports)[
            ["id", "created_at", "category", "subcategory", "location_type",
             "severity", "status", "title", "description", "upvotes"]
        ]
        csv = df_export.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ Exporter les signalements (CSV)",
            data=csv.encode("utf-8-sig"),
            file_name=f"signalements_{selected_uni['short_name']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    _footer()


# ─────────────────────────────────────────────
# PAGE: PORTAIL UNION ÉTUDIANTE
# ─────────────────────────────────────────────
def show_union_portal():
    st.markdown(f"""
    <div class="hero">
      <h1 style="font-size:1.9rem">{t('union.title')}</h1>
      <p>{t('union.subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Platform stats ──
    stats = db.get_platform_stats()
    st.markdown("### " + t('union.stats_title'))
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, cls in [
        (c1, stats["total"],    "Signalements au total",  ""),
        (c2, stats["pending"],  "En attente de réponse",  "red"),
        (c3, stats["resolved"], "Résolus",                ""),
        (c4, stats["universities"], "Universités touchées", "blue"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card {cls}"><div class="value">{val}</div><div class="label">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Classement des universités",
        "🔥 Problèmes prioritaires",
        "📈 Comparaison nationale",
        "📄 Export & Advocacy",
    ])

    # ── Tab 1: University Ranking ──
    with tab1:
        st.markdown("### 🏆 Classement par nombre de signalements")
        st.caption("Les universités avec le plus de signalements actifs ont le plus besoin d'attention.")

        ranking = db.get_university_ranking()
        if ranking:
            df_rank = pd.DataFrame(ranking)
            df_rank["resolution_rate"] = (df_rank["resolved"] / df_rank["total"] * 100).round(1)
            df_rank["avg_severity"]    = df_rank["avg_severity"].round(2)
            df_rank = df_rank.fillna(0)

            # Visual table
            st.dataframe(
                df_rank[["name", "wilaya", "total", "open_count", "resolved",
                          "avg_severity", "resolution_rate"]].rename(columns={
                    "name":            "Université",
                    "wilaya":          "Wilaya",
                    "total":           "Total",
                    "open_count":      "Ouverts",
                    "resolved":        "Résolus",
                    "avg_severity":    "Gravité moy.",
                    "resolution_rate": "Taux résolution (%)",
                }),
                use_container_width=True,
                height=420,
            )

            # Bar chart of top 10
            df_top10 = df_rank.head(10)
            fig = px.bar(
                df_top10, x="total", y="name", orientation="h",
                color="avg_severity",
                color_continuous_scale=[[0,"#22c55e"],[0.5,"#f59e0b"],[1,"#ef4444"]],
                labels={"total": "Signalements", "name": "", "avg_severity": "Gravité moy."},
                title="Top 10 – Universités les plus signalées",
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter"), margin=dict(t=40, b=20, l=20, r=20),
                yaxis=dict(autorange="reversed"), height=420, title_font_size=14,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 2: Priority Issues ──
    with tab2:
        st.markdown("### 🔥 Problèmes prioritaires non résolus")
        st.caption("Classés par score de priorité = upvotes × 2 + gravité × 10")

        priorities = db.get_top_priority_issues(limit=15)
        for i, r in enumerate(priorities):
            sev_c = SEVERITY_COLORS.get(r["severity"], "#6b7280")
            score = r["upvotes"] * 2 + r["severity"] * 10
            st.markdown(
                f'<div class="priority-item">'
                f'  <div class="priority-rank">#{i+1}</div>'
                f'  <div style="flex:1">'
                f'    <div style="font-weight:600;color:#1f2937">{r["title"]}</div>'
                f'    <div style="font-size:0.8rem;color:#6b7280;margin-top:4px">'
                f'      🏫 {r["university_name"]} &nbsp;|&nbsp; {r["category"]}'
                f'      &nbsp;|&nbsp; {severity_badge(r["severity"])} &nbsp;|&nbsp; 👍 {r["upvotes"]}'
                f'    </div>'
                f'  </div>'
                f'  <div style="font-size:0.85rem;font-weight:700;color:{sev_c}">Score&nbsp;{score}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Tab 3: National Comparison ──
    with tab3:
        st.markdown("### 📈 Analyse comparative nationale")

        cats_data = db.get_category_breakdown()
        wilaya_data = db.get_wilaya_breakdown()

        col_l, col_r = st.columns(2)

        with col_l:
            if cats_data:
                df_c = pd.DataFrame(cats_data)
                fig = px.bar(
                    df_c, x="count", y="category", orientation="h",
                    title="Signalements par catégorie (national)",
                    color="count",
                    color_continuous_scale=[[0,"#bbf7d0"],[1,"#064e3b"]],
                )
                fig.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter"), margin=dict(t=40,b=20,l=10,r=10),
                    yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                    title_font_size=13, xaxis_title="", yaxis_title="",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_r:
            if wilaya_data:
                df_w = pd.DataFrame(wilaya_data).head(15)
                fig2 = px.bar(
                    df_w, x="wilaya", y="count",
                    title="Signalements par Wilaya",
                    color="count",
                    color_continuous_scale=[[0,"#bbf7d0"],[1,"#064e3b"]],
                )
                fig2.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Inter"), margin=dict(t=40,b=60,l=10,r=10),
                    coloraxis_showscale=False, title_font_size=13,
                    xaxis_tickangle=-45, xaxis_title="", yaxis_title="",
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Severity national
        sev_data = db.get_severity_breakdown()
        if sev_data:
            df_sv = pd.DataFrame(sev_data)
            df_sv["label"] = df_sv["severity"].map(SEVERITY_LABELS)
            fig3 = px.funnel(
                df_sv, x="count", y="label",
                title="Entonnoir de gravité (national)",
                color="label",
                color_discrete_map={v: SEVERITY_COLORS[k] for k, v in SEVERITY_LABELS.items()},
            )
            fig3.update_layout(
                font=dict(family="Inter"), margin=dict(t=40,b=20,l=10,r=10),
                title_font_size=13, showlegend=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Tab 4: Export & Advocacy ──
    with tab4:
        st.markdown("### 📄 Export des données & Outils d'Advocacy")

        # Full export
        all_reports = db.get_reports()
        if all_reports:
            df_all = pd.DataFrame(all_reports)
            cols_export = ["id", "created_at", "university_name", "wilaya",
                           "location_type", "category", "subcategory",
                           "severity", "status", "title", "description", "upvotes"]
            df_export = df_all[[c for c in cols_export if c in df_all.columns]]
            csv_all = df_export.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇️ Exporter TOUS les signalements (CSV)",
                data=csv_all.encode("utf-8-sig"),
                file_name=f"sawt_taleb_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("### ✉️ Générateur de Lettre d'Advocacy")
        st.caption("Générez une lettre officielle à destination du ministère ou de la direction universitaire.")

        universities = db.get_universities()
        uni_names    = [u["name"] for u in universities]
        col_a, col_b = st.columns(2)
        with col_a:
            letter_uni  = st.selectbox("Université concernée", uni_names, key="letter_uni")
            letter_dest = st.selectbox("Destinataire", [
                "Le Recteur / Président de l'Université",
                "Le Directeur des Œuvres Universitaires (DOU)",
                "Le Ministre de l'Enseignement Supérieur",
                "Le Wali (Gouverneur) de la Wilaya",
                "Le Directeur du CROUS",
            ])
        with col_b:
            union_name  = st.text_input("Nom du syndicat / union", placeholder="Ex: UGEL, UNEA, Bureau Syndical de …")
            rep_name    = st.text_input("Nom du représentant", placeholder="Ex: Mohamed Ammari")

        if st.button("📝 Générer la lettre", use_container_width=True):
            if not union_name or not rep_name:
                st.warning("Veuillez renseigner le nom de votre syndicat et votre nom.")
            else:
                uni_stats = db.get_university_stats(
                    next(u["id"] for u in universities if u["name"] == letter_uni)
                )
                top_issues = db.get_top_priority_issues(limit=5)
                uni_issues = [r for r in top_issues if r["university_name"] == letter_uni]

                letter = f"""
LETTRE OUVERTE D'ADVOCACY ÉTUDIANT
====================================
{datetime.now().strftime("%d %B %Y")}

De : {union_name}
Représenté par : {rep_name}
À : {letter_dest}
Objet : Conditions inacceptables à {letter_uni} — Demande d'intervention urgente

Monsieur / Madame,

Nous, membres de {union_name}, représentant les étudiants de {letter_uni},
portons à votre attention des problèmes graves et persistants affectant les conditions
d'études et de vie de nos étudiants.

CHIFFRES CLÉS (Source : Plateforme Sawt Taleb) :
- Nombre total de signalements : {uni_stats['total']}
- Signalements non résolus : {uni_stats['open']}
- Taux de résolution actuel : {uni_stats['resolution_rate']}%
- Gravité moyenne : {uni_stats['avg_severity']}/5
- Problème le plus signalé : {uni_stats['top_category']}

PROBLÈMES LES PLUS URGENTS :
"""
                for i, issue in enumerate(uni_issues[:3], 1):
                    letter += f"\n{i}. {issue['title']}\n   Gravité : {SEVERITY_LABELS[issue['severity']]} | Soutiens : {issue['upvotes']}\n"

                letter += f"""

Nous demandons formellement et urgemment :
1. Un plan d'action concret avec des délais précis pour chaque problème signalé.
2. Une réponse officielle à ce courrier dans un délai de 15 jours ouvrables.
3. Une réunion de concertation avec les représentants étudiants.
4. Un rapport mensuel public sur l'avancement des résolutions.

Les étudiants de {letter_uni} méritent des conditions dignes pour leurs études.
Nous restons à votre disposition pour toute discussion constructive.

Dans l'attente d'une réponse favorable,

{rep_name}
Au nom de {union_name}
Date : {datetime.now().strftime("%d/%m/%Y")}
"""
                st.text_area("📄 Lettre générée (copiez et personnalisez)", letter, height=500)
                st.download_button(
                    "⬇️ Télécharger la lettre (.txt)",
                    data=letter.encode("utf-8"),
                    file_name=f"lettre_advocacy_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                )

    _footer()


# ─────────────────────────────────────────────
# PAGE: À PROPOS & AIDE
# ─────────────────────────────────────────────
def show_about():
    st.markdown(f"""
    <div class="hero">
      <h1 style="font-size:1.9rem">{t('about.title')}</h1>
      <p>{t('about.subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Notre Mission")
        st.markdown("""
        **Sawt Taleb** (صوت الطالب — "La Voix de l'Étudiant") est une plateforme citoyenne
        permettant aux étudiants algériens de :

        - **Signaler** les problèmes d'infrastructure, d'hygiène, d'alimentation et d'hébergement
        - **Documenter** avec des preuves photographiques
        - **Mobiliser** en soutenant les signalements d'autres étudiants
        - **Impacter** en fournissant des données aux unions étudiantes pour l'advocacy

        Notre objectif est simple : **transformer la frustration en action collective**.
        """)

        st.markdown("### 🔒 Confidentialité & Sécurité")
        st.markdown("""
        - Les signalements anonymes sont **totalement protégés**
        - Aucune donnée personnelle n'est partagée avec des tiers
        - Les photos uploadées ne contiennent pas de métadonnées EXIF
        - La plateforme ne nécessite aucune inscription
        """)

    with col2:
        st.markdown("### 📖 Comment utiliser la plateforme")
        st.markdown("""
        **1. Soumettre un signalement**
        Rendez-vous sur "📝 Soumettre un Signalement" et remplissez le formulaire en 6 étapes.
        Plus votre description est détaillée, plus elle sera efficace.

        **2. Explorer les signalements**
        Utilisez "🔍 Explorer" pour voir tous les signalements. Vous pouvez filtrer par
        université, catégorie, gravité et bien plus.

        **3. Soutenir un signalement**
        Cliquez sur 🤍 "Soutenir" sur tout signalement qui vous concerne aussi.
        Plus un signalement est soutenu, plus il est prioritaire.

        **4. Tableau de bord**
        Le "📊 Tableau de Bord" offre des analyses visuelles par université.

        **5. Portail Union**
        Les syndicats accèdent au "🏛️ Portail Union" pour exporter les données
        et générer des lettres officielles d'advocacy.
        """)

    st.markdown("---")
    st.markdown("### ❓ Questions Fréquentes")

    faqs = [
        ("Mes signalements sont-ils vraiment anonymes ?",
         "Oui. Si vous cochez 'Anonyme', aucune information d'identification n'est stockée. "
         "Votre adresse IP n'est pas enregistrée non plus."),
        ("Qui peut voir mes signalements ?",
         "Tous les signalements approuvés sont visibles publiquement. Si vous signaler quelque chose "
         "de sensible, choisissez l'option anonyme."),
        ("Qui gère les réponses aux signalements ?",
         "La plateforme est un outil de documentation. Les réponses aux problèmes dépendent des "
         "administrations universitaires et des autorités compétentes."),
        ("Comment savoir si mon problème a été résolu ?",
         "Le statut de chaque signalement est mis à jour dans l'application. Vous pouvez le suivre "
         "en notant le numéro de votre signalement (affiché après soumission)."),
        ("Puis-je signaler au nom d'autres étudiants ?",
         "Oui. Vous pouvez soumettre un signalement collectif en mentionnant le nombre d'étudiants "
         "affectés dans la description."),
        ("La plateforme est-elle officielle ?",
         "Non. Sawt Taleb est une initiative étudiante indépendante. Elle n'est pas affiliée "
         "au Ministère de l'Enseignement Supérieur."),
    ]

    for question, answer in faqs:
        with st.expander(f"❓ {question}"):
            st.markdown(answer)

    st.markdown("---")
    st.markdown("### 📞 Contact & Signalement d'Abus")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        **📧 Contact général**
        contact@sawttaleb.dz
        *(adresse fictive pour la démo)*
        """)
    with col_b:
        st.markdown("""
        **🐛 Signaler un bug**
        Utilisez le formulaire de signalement
        avec la catégorie "Administration".
        """)
    with col_c:
        st.markdown("""
        **🤝 Contribuer**
        La plateforme est open source.
        Rejoignez-nous sur GitHub !
        """)

    # Stats finale
    st.markdown("---")
    stats = db.get_platform_stats()
    st.markdown(
        f'<div style="text-align:center;padding:24px;background:linear-gradient(135deg,#064e3b,#059669);'
        f'border-radius:12px;color:white">'
        f'<h3 style="margin:0 0 16px">Ensemble, nous avons déjà accompli</h3>'
        f'<span style="font-size:2.5rem;font-weight:700">{stats["total"]}</span> signalements &nbsp;·&nbsp; '
        f'<span style="font-size:2.5rem;font-weight:700">{stats["resolved"]}</span> résolus &nbsp;·&nbsp; '
        f'<span style="font-size:2.5rem;font-weight:700">{stats["universities"]}</span> universités<br>'
        f'<p style="margin-top:12px;opacity:0.85">Chaque signalement est une voix. Ensemble, nous changeons les choses.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _footer()


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
def _footer():
    st.markdown(
        '<div class="app-footer">'
        '© 2025 Sawt Taleb | صوت الطالب — Plateforme étudiante algérienne indépendante<br>'
        'Données stockées localement · Aucune affiliation gouvernementale'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px">'
            '<span style="font-size:3rem">🎓</span>'
            '<div style="font-size:1.4rem;font-weight:700;margin-top:4px">Sawt Taleb</div>'
            '<div style="font-size:1.1rem;opacity:0.8;font-family:serif">صوت الطالب</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Language selector
        lang_map = {"English": "en", "Français": "fr", "العربية": "ar"}
        labels = list(lang_map.keys())
        current_label = next((lbl for lbl, code in lang_map.items() if code == st.session_state.get("lang", "en")), labels[0])
        selected_label = st.selectbox("Langue / Language / اللغة", labels, index=labels.index(current_label), key="lang_select")
        selected_code = lang_map[selected_label]
        if st.session_state.get("lang") != selected_code:
            st.session_state["lang"] = selected_code
            st.experimental_rerun()

        st.markdown("---")

        selected = st.radio(
            "Navigation",
            PAGES,
            key="nav_radio",
            format_func=lambda k: t(f"nav.{k}"),
            label_visibility="collapsed",
        )

        st.markdown("---")
        stats = db.get_platform_stats()
        st.markdown(
            f'<div style="font-size:0.8rem;opacity:0.7;text-align:center">'
            f'📊 {stats["total"]} signalements<br>'
            f'🏫 {stats["universities"]} universités<br>'
            f'✅ {stats["resolved"]} résolus'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            '<div style="font-size:0.72rem;opacity:0.6;text-align:center">'
            'v1.0 · Plateforme Étudiante<br>Algérie 🇩🇿'
            '</div>',
            unsafe_allow_html=True,
        )

    return selected


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    inject_css()
    selected_page = build_sidebar()
    page_map = {
        "home": show_home,
        "submit": show_submit_report,
        "browse": show_browse_reports,
        "dashboard": show_dashboard,
        "union": show_union_portal,
        "about": show_about,
    }

    lang = st.session_state.get("lang", "fr")
    if lang == "ar":
        st.markdown('<div class="rtl">', unsafe_allow_html=True)

    fn = page_map.get(selected_page, show_home)
    fn()

    if lang == "ar":
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
