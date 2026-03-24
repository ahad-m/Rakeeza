import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nav import sidebar_nav

st.set_page_config(page_title="تفاصيل الموردين", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS ----------
st.markdown("""
<style>
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}

.block-container {
    direction: rtl;
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.stSelectbox label,
.stMarkdown,
.stMetric,
.stPlotlyChart {
    text-align: right;
}

/* خلفية خفيفة للرسمة */
.chart-container {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
    margin: 8px 0;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.10);
    background: rgba(0,0,0,0.02);
    font-weight: 800;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# ─── التنقل الموحد ───
sidebar_nav()

# ---------- مسار البيانات (نسبي) ----------
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ---------- تحميل البيانات ----------
@st.cache_data
def load_cleaned():
    return pd.read_excel(DATA_DIR / "gastat_foreign_trade_cleaned.xlsx")

df = load_cleaned().copy()

required = {"Country", "Year", "Section ID", "Section", "Trade Flow", "Million SAR"}
missing = required - set(df.columns)
if missing:
    st.error(f"أعمدة ناقصة في الملف: {missing}")
    st.stop()

# ---------- تحميل أسماء الأقسام بالعربي ----------
@st.cache_data
def load_sections_ar():
    candidates = [
        DATA_DIR / "sections_arabic_gastat_short1.csv",
        DATA_DIR / "sections_arabic_gastat_short.csv",
        DATA_DIR / "sections_arabic_gastat_short1.xlsx",
        DATA_DIR / "sections_arabic_gastat_short.xlsx",
    ]
    for p in candidates:
        if p.exists():
            if p.suffix == ".xlsx":
                return pd.read_excel(p)
            return pd.read_csv(p)
    return None

sections_ar = load_sections_ar()
section_ar_map = {}
if sections_ar is not None:
    ar_df = sections_ar[["Section", "Arabic (Short)"]].dropna().copy()
    ar_df.columns = ["Section_en", "Section_ar"]
    section_ar_map = dict(zip(ar_df["Section_en"], ar_df["Section_ar"]))

# ---------- عنوان الصفحة ----------
st.markdown("##  تفاصيل الموردين")
st.markdown("تحليل تفصيلي لموردي كل قسم تجاري: من هو المورد الأول؟ كم حصته؟ وما هي البدائل المتاحة؟")
st.markdown("---")

# ---------- الفلاتر ----------
years = sorted(df["Year"].dropna().unique().tolist())
sections = df[["Section ID", "Section"]].drop_duplicates().sort_values(["Section ID"])

# بناء قائمة الأقسام بالعربي
section_display = []
section_id_lookup = {}
for _, row in sections.iterrows():
    sid = str(row["Section ID"]).strip()
    sname_en = str(row["Section"]).strip()
    sname_ar = section_ar_map.get(sname_en, sname_en)
    display = f"{sname_ar}"
    section_display.append(display)
    section_id_lookup[display] = sid

c1, c2 = st.columns([1, 2])
with c1:
    year = st.selectbox("اختر السنة", years, index=len(years) - 1)
with c2:
    sel = st.selectbox("اختر القسم", section_display, index=0)
    section_id = section_id_lookup[sel]

# ---------- حساب ملخص الموردين (واردات فقط) ----------
d = df[(df["Year"] == year) & (df["Section ID"] == section_id) & (df["Trade Flow"] == "Imports")].copy()

if d.empty:
    st.warning("لا توجد واردات لهذا القسم في السنة المختارة.")
    st.stop()

sup = d.groupby(["Country"], as_index=False)["Million SAR"].sum().sort_values("Million SAR", ascending=False)
total_imports = float(sup["Million SAR"].sum()) if len(sup) else 0.0
sup["Share"] = np.where(total_imports > 0, sup["Million SAR"] / total_imports, 0.0)

# ---------- ترجمة أسماء الدول للعربي ----------
COUNTRY_AR = {
    "China": "الصين", "United States": "الولايات المتحدة", "Germany": "ألمانيا",
    "Japan": "اليابان", "South Korea": "كوريا الجنوبية", "India": "الهند",
    "France": "فرنسا", "Italy": "إيطاليا", "United Kingdom": "المملكة المتحدة",
    "Brazil": "البرازيل", "Turkey": "تركيا", "Spain": "إسبانيا",
    "Netherlands": "هولندا", "Belgium": "بلجيكا", "Switzerland": "سويسرا",
    "Australia": "أستراليا", "Canada": "كندا", "Russia": "روسيا",
    "Russian Federation": "روسيا", "Mexico": "المكسيك", "Indonesia": "إندونيسيا",
    "Thailand": "تايلاند", "Malaysia": "ماليزيا", "Singapore": "سنغافورة",
    "Vietnam": "فيتنام", "Philippines": "الفلبين", "Pakistan": "باكستان",
    "Bangladesh": "بنغلاديش", "Egypt": "مصر", "South Africa": "جنوب أفريقيا",
    "Argentina": "الأرجنتين", "Chile": "تشيلي", "Colombia": "كولومبيا",
    "Poland": "بولندا", "Sweden": "السويد", "Norway": "النرويج",
    "Denmark": "الدنمارك", "Finland": "فنلندا", "Austria": "النمسا",
    "Ireland": "أيرلندا", "Portugal": "البرتغال", "Greece": "اليونان",
    "Czech Republic": "التشيك", "Romania": "رومانيا", "Hungary": "المجر",
    "New Zealand": "نيوزيلندا", "Taiwan": "تايوان", "Israel": "إسرائيل",
    "United Arab Emirates": "الإمارات", "Kuwait": "الكويت", "Qatar": "قطر",
    "Bahrain": "البحرين", "Oman": "عُمان", "Jordan": "الأردن",
    "Lebanon": "لبنان", "Iraq": "العراق", "Iran": "إيران",
    "Sudan": "السودان", "Somalia": "الصومال", "Morocco": "المغرب",
    "Tunisia": "تونس", "Algeria": "الجزائر", "Libya": "ليبيا",
    "Nigeria": "نيجيريا", "Kenya": "كينيا", "Ethiopia": "إثيوبيا",
    "Ghana": "غانا", "Tanzania": "تنزانيا", "Ukraine": "أوكرانيا",
    "Sri Lanka": "سريلانكا", "Myanmar": "ميانمار", "Cambodia": "كمبوديا",
    "Peru": "بيرو", "Ecuador": "الإكوادور", "Venezuela": "فنزويلا",
    "Cuba": "كوبا", "Dominican Republic": "جمهورية الدومينيكان",
    "Costa Rica": "كوستاريكا", "Panama": "بنما", "Uruguay": "أوروغواي",
    "Paraguay": "باراغواي", "Bolivia": "بوليفيا",
    "Saudi Arabia": "السعودية", "Yemen": "اليمن", "Syria": "سوريا",
    "Palestine": "فلسطين", "Afghanistan": "أفغانستان", "Nepal": "نيبال",
    "Laos": "لاوس", "Mongolia": "منغوليا", "North Korea": "كوريا الشمالية",
    "Hong Kong": "هونغ كونغ", "Macao": "ماكاو",
}
sup["Country_ar"] = sup["Country"].map(COUNTRY_AR).fillna(sup["Country"])

top5 = sup.head(5).copy()
top15 = sup.head(15).copy()

top1_country = top5.iloc[0]["Country_ar"]
top1_share = float(top5.iloc[0]["Share"])
rank2 = top5.iloc[1]["Country_ar"] if len(top5) > 1 else "غير متاح"
rank3 = top5.iloc[2]["Country_ar"] if len(top5) > 2 else "غير متاح"
rank2_share = float(top5.iloc[1]["Share"]) if len(top5) > 1 else 0.0
rank3_share = float(top5.iloc[2]["Share"]) if len(top5) > 2 else 0.0

# ---------- تنسيق القيم ----------
def fmt_million(v):
    if v >= 1000:
        return f"{v/1000:,.2f} مليار ريال"
    return f"{v:,.1f} مليون ريال"

# ---------- المؤشرات الرئيسية (st.metric — نفس ستايل الصفحات السابقة) ----------
k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        label=f"إجمالي واردات القسم ({year})",
        value=fmt_million(total_imports),
    )

with k2:
    st.metric(
        label="المورد الأول",
        value=top1_country,
        delta=f"حصته: {top1_share:.1%}",
        delta_color="off",
    )

with k3:
    st.metric(
        label="أقرب بديلين",
        value=f"{rank2} ({rank2_share:.1%})",
        delta=f"{rank3} ({rank3_share:.1%})",
        delta_color="off",
    )

# ---------- تقييم مستوى الاعتماد ----------
if top1_share >= 0.50:
    msg = "⚠️ اعتماد مرتفع على مورد واحد — البدائل مهمة"
elif top1_share >= 0.30:
    msg = "🧭 اعتماد متوسط — يُنصح بمراقبة المنافسة والبدائل"
else:
    msg = "✅ توزيع جيد بين الموردين — المخاطر أقل"
st.markdown(f"<span class='badge'>{msg}</span>", unsafe_allow_html=True)

st.markdown("---")

# ---------- الرسم الأول: أكبر 5 موردين ----------
st.markdown("### أكبر 5 موردين")
st.markdown("ترتيب أكبر 5 دول موردة لهذا القسم حسب قيمة الواردات، مع حصة كل دولة من الإجمالي.")

bar_data = top5.sort_values("Million SAR", ascending=True)

fig_bar = px.bar(
    bar_data,
    x="Million SAR",
    y="Country_ar",
    orientation="h",
    color="Million SAR",
    color_continuous_scale=["#C3DFC4", "#118815"],
    labels={"Million SAR": "قيمة الواردات (مليون ريال)", "Country_ar": "الدولة"},
)
fig_bar.update_traces(
    customdata=bar_data[["Country_ar", "Million SAR", "Share"]].values,
    hovertemplate=(
        "<b style='font-size:14px'>%{customdata[0]}</b><br><br>"
        "قيمة الواردات: <b>%{customdata[1]:,.1f} مليون ريال</b><br>"
        "الحصة من الإجمالي: <b>%{customdata[2]:.1%}</b>"
        "<extra></extra>"
    ),
)
fig_bar.update_layout(
    height=400,
    paper_bgcolor="white",
    plot_bgcolor="#f9fafb",
    margin=dict(l=20, r=20, t=10, b=50),
    yaxis=dict(tickfont=dict(size=14), automargin=True),
    xaxis=dict(title="قيمة الواردات (مليون ريال)", gridcolor="#E5E7EB"),
    coloraxis_showscale=False,
    hoverlabel=dict(font_size=13, bgcolor="white"),
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")

# ---------- الرسم الثاني: توزيع أكبر 15 مورد ----------
st.markdown("### توزيع أكبر 15 مورد")
st.markdown("خريطة شجرية توضح حصة كل دولة من إجمالي واردات القسم. كلما كبر المربع، زادت حصة الدولة.")

fig_tree = px.treemap(
    top15,
    path=["Country_ar"],
    values="Million SAR",
    color="Share",
    color_continuous_scale=["#E0F2FE", "#1D4ED8"],
    labels={"Million SAR": "قيمة الواردات (مليون ريال)", "Share": "الحصة", "Country_ar": "الدولة"},
)
fig_tree.update_traces(
    textinfo="label",
    texttemplate="<b>%{label}</b>",
    textfont=dict(size=14),
    hovertemplate=(
        "<b style='font-size:14px'>%{label}</b><br><br>"
        "قيمة الواردات: <b>%{value:,.1f} مليون ريال</b><br>"
        "الحصة: <b>%{percentRoot:.1%}</b>"
        "<extra></extra>"
    ),
)
fig_tree.update_layout(
    height=500,
    paper_bgcolor="white",
    margin=dict(l=10, r=10, t=10, b=10),
    coloraxis_showscale=False,
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_tree, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------- ملاحظة ختامية ----------
st.markdown("### ملاحظة")
st.markdown(
    "إذا كانت حصة المورد الأول عالية جداً، يُنصح بالبحث عن رفع مساهمة المورد الثاني والثالث "
    "أو تنويع مصادر التوريد لتقليل المخاطر المستقبلية."
)
