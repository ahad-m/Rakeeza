import streamlit as st
from pathlib import Path
import base64
from nav import sidebar_nav

st.set_page_config(
    page_title="رَكيزة",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

def img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")

st.markdown("""
<style>
/* Hide Streamlit default header + toolbar + menus */
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* RTL page */
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.2rem;
    direction: rtl;
    max-width: 1120px;
}
p, li { text-align: right !important; }

/* ---- Header: Logo + Name + Tagline (centered) ---- */
.brand-header {
    text-align: center;
    padding: 30px 0 20px 0;
    margin-bottom: 10px;
}
.brand-header img {
    width: 260px;
    height: auto;
    margin-bottom: 14px;
}
.brand-name {
    font-weight: 950;
    font-size: 2.8rem;
    color: #004D2E;
    margin: 0;
    line-height: 1.3;
}
.brand-tagline {
    font-size: 1.1rem;
    color: #6b7280;
    margin-top: 8px;
    font-weight: 400;
    letter-spacing: 0.3px;
}

/* ---- Section headers ---- */
.sec-title {
    font-weight: 900;
    font-size: 1.35rem;
    margin: 28px 0 6px 0;
    color: #004D2E;
    text-align: right !important;
}
.sec-sub {
    opacity: 0.65;
    margin-top: -4px;
    margin-bottom: 16px;
    font-size: 0.92rem;
    text-align: right !important;
}

/* ---- Why cards (green accent) ---- */
.why-card {
    border-radius: 16px;
    padding: 22px 20px 18px 20px;
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #bbf7d0;
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.why-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,107,63,0.10);
}
.why-card .icon {
    font-size: 2rem;
    margin-bottom: 8px;
}
.why-card .title {
    font-weight: 800;
    font-size: 1.05rem;
    margin-bottom: 6px;
    color: #004D2E;
}
.why-card .desc {
    font-size: 0.93rem;
    line-height: 1.85;
    color: #1a3d2b;
    margin: 0;
}

/* ---- Page info cards ---- */
.info-card {
    border-radius: 16px;
    padding: 22px 20px 18px 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.info-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.info-card .icon {
    font-size: 2rem;
    margin-bottom: 8px;
}
.info-card .title {
    font-weight: 800;
    font-size: 1.05rem;
    margin-bottom: 6px;
    color: #004D2E;
}
.info-card .desc {
    font-size: 0.93rem;
    line-height: 1.85;
    color: #475569;
    margin: 0;
}

/* ---- Journey ---- */
.journey-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin: 16px 0;
}
.journey-step {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 18px;
    border-radius: 999px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    font-size: 0.88rem;
    font-weight: 700;
    color: #004D2E;
    transition: all 0.15s ease;
}
.journey-step:hover {
    background: #dcfce7;
    border-color: #86efac;
}
.journey-arrow {
    font-size: 1.1rem;
    color: #94a3b8;
}

/* ---- Footer ---- */
.footer-note {
    text-align: center !important;
    opacity: 0.55;
    font-size: 0.82rem;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── التنقل الموحد ───
sidebar_nav()

# ================ HEADER: Logo + Name + Tagline ================
logo_html = ""
if LOGO_PATH.exists():
    b64 = img_to_base64(LOGO_PATH)
    logo_html = f'<img src="data:image/png;base64,{b64}" />'
else:
    logo_html = '<div style="height:40px;"></div>'

st.markdown(f"""
<div class="brand-header">
    {logo_html}
    <div class="brand-tagline">حيث تُبنى القرارات على أساس البيانات</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ================ لماذا هذا المشروع مهم؟ ================
st.markdown('<div class="sec-title">لماذا هذا المشروع مهم؟</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
with c1:
    st.markdown("""
    <div class="why-card">
        <div class="icon">🇸🇦</div>
        <div class="title">ارتباطه برؤية 2030</div>
        <div class="desc">
            يساعد على تنويع الاقتصاد بعيداً عن النفط من خلال تحويل بيانات التجارة الخارجية
            إلى أولويات واضحة لفرص التوطين وتقليل الاعتماد على الاستيراد.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="why-card">
        <div class="icon">🏭</div>
        <div class="title">ارتباطه ببرنامج ندلب (NIDLP)</div>
        <div class="desc">
            يدعم مسار تطوير الصناعة والخدمات اللوجستية عبر تحديد القطاعات ذات الفجوة الأعلى
            بين الواردات والصادرات، ورصد مخاطر سلاسل الإمداد.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ================ ماذا ستجد داخل اللوحة؟ ================
st.markdown('<div class="sec-title">ماذا ستجد داخل اللوحة؟</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">كل صفحة تجيب على سؤال محدد — اضغط على أي صفحة من القائمة الجانبية للانتقال.</div>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3, gap="medium")
with p1:
    st.markdown("""
    <div class="info-card">
        <div class="icon">📈</div>
        <div class="title">الاتجاهات</div>
        <div class="desc">كيف تتغير الصادرات والواردات عبر السنوات؟ هل الفجوة تتحسن أم تتفاقم؟</div>
    </div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="info-card">
        <div class="icon">📊</div>
        <div class="title">فجوة الأقسام</div>
        <div class="desc">ما الأقسام التجارية التي لديها أكبر فجوة بين الواردات والصادرات؟ وأين تبدأ فرص التوطين؟</div>
    </div>
    """, unsafe_allow_html=True)
with p3:
    st.markdown("""
    <div class="info-card">
        <div class="icon">🧷</div>
        <div class="title">الاعتماد والتركيز</div>
        <div class="desc">هل نعتمد على دولة واحدة في الاستيراد؟ ما الأقسام الأكثر خطورة من ناحية سلاسل الإمداد؟</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

p4, p5, p6 = st.columns(3, gap="medium")
with p4:
    st.markdown("""
    <div class="info-card">
        <div class="icon">🔎</div>
        <div class="title">تفاصيل الموردين</div>
        <div class="desc">من هم أكبر الموردين لكل قسم؟ ما حصة المورد الأول؟ وما البدائل المتاحة؟</div>
    </div>
    """, unsafe_allow_html=True)
with p5:
    st.markdown("""
    <div class="info-card">
        <div class="icon">🧭</div>
        <div class="title">التحليل الاستراتيجي</div>
        <div class="desc">نظرة شاملة تجمع أهم المؤشرات: توزيع الواردات، ترتيب القطاعات، وخريطة الصادرات العالمية.</div>
    </div>
    """, unsafe_allow_html=True)
with p6:
    st.markdown("""
    <div class="info-card" style="background: #f0fdf4; border-color: #bbf7d0;">
        <div class="icon">📋</div>
        <div class="title">ملخص سريع</div>
        <div class="desc">5 صفحات تحليلية مبنية على بيانات الهيئة العامة للإحصاء — من الاتجاه العام إلى التفاصيل الدقيقة.</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ================ مسار الاستخدام ================
st.markdown('<div class="sec-title" style="text-align:center !important;">مسار الاستخدام</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub" style="text-align:center !important;">ابدأ من الرئيسية وتنقل بالترتيب للحصول على الصورة الكاملة.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="journey-bar">
    <span class="journey-step"> الرئيسية</span>
    <span class="journey-arrow">←</span>
    <span class="journey-step"> الاتجاهات</span>
    <span class="journey-arrow">←</span>
    <span class="journey-step"> فجوة الأقسام</span>
    <span class="journey-arrow">←</span>
    <span class="journey-step"> الاعتماد</span>
    <span class="journey-arrow">←</span>
    <span class="journey-step"> تفاصيل الموردين</span>
    <span class="journey-arrow">←</span>
    <span class="journey-step"> التحليل الاستراتيجي</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================ مصدر البيانات ================
st.markdown("""
<div class="footer-note">
    المصدر: الهيئة العامة للإحصاء (GASTAT) — بيانات التجارة الخارجية.
    تم تنظيف البيانات وتوحيد الأقسام لأغراض التحليل.
</div>
""", unsafe_allow_html=True)
