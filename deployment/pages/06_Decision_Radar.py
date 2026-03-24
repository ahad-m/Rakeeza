import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nav import sidebar_nav


# ==========================================================
# CONFIG
# ==========================================================
st.set_page_config(
    page_title="رادار القرار",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
.chart-container {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# HELPERS
# ==========================================================
def safe_div(a, b):
    b = np.where(b == 0, np.nan, b)
    out = a / b
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


def pct(x):
    try:
        return f"{float(x) * 100:.1f}%"
    except Exception:
        return "—"


def fmt_msar(x):
    try:
        v = float(x)
        if abs(v) >= 1000:
            return f"{v / 1000:,.1f} مليار"
        return f"{v:,.0f} مليون"
    except Exception:
        return "—"


def assign_bucket(section_name: str) -> str:
    s = str(section_name).lower()
    industry = [
        "chemical", "chem", "base metal", "metal", "machinery", "mechanical", "electrical",
        "plastic", "rubber", "cement", "glass", "stone",
        "كيميائ", "لدائن", "مطاط", "معادن", "آلات", "معدات", "إسمنت", "حجر",
    ]
    food = ["food", "beverage", "tobacco", "plant", "animal",
            "أغذية", "مشروبات", "تبغ", "نبات", "حيوان", "دهون", "زيوت"]
    consumer = ["textile", "footwear", "miscellaneous", "paper", "wood", "leather", "skins",
                "منسوجات", "أحذية", "متنوعة", "ورق", "أخشاب", "جلود", "فراء"]
    strategic = ["vehicles", "aircraft", "vessels", "transport",
                 "مركبات", "طائرات", "سفن", "نقل"]

    if any(k in s for k in food):
        return "الأغذية والزراعة"
    if any(k in s for k in consumer):
        return "السلع الاستهلاكية"
    if any(k in s for k in strategic):
        return "واردات استراتيجية"
    if any(k in s for k in industry):
        return "الصناعة والتصنيع"
    return "أخرى"


BUCKET_ICON = {
    "الصناعة والتصنيع": "🏭",
    "الأغذية والزراعة": "🍏",
    "السلع الاستهلاكية": "🧺",
    "واردات استراتيجية": "🛠️",
    "أخرى": "🧩",
}


# ==========================================================
# التنقل الموحد
# ==========================================================
sidebar_nav()
st.write("")


# ==========================================================
# مسار مجلد البيانات (نسبي)
# ==========================================================
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# ==========================================================
# LOAD DATA
# ==========================================================
@st.cache_data
def load_data():
    df = pd.read_excel(DATA_DIR / "gastat_foreign_trade_cleaned.xlsx")
    rules = pd.read_excel(DATA_DIR / "Criticality,Complexity,Ease_Table.xlsx")
    return df, rules


@st.cache_data
def load_sections_ar():
    """تحميل أسماء الأقسام بالعربي من ملف CSV/XLSX."""
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


raw, rules = load_data()

required = {"Country", "Year", "Section ID", "Section", "Trade Flow", "Million SAR"}
missing = required - set(raw.columns)
if missing:
    st.error(f"الأعمدة الناقصة في الملف: {missing}")
    st.stop()

raw["Year"] = pd.to_numeric(raw["Year"], errors="coerce").astype("Int64")
raw["Million SAR"] = pd.to_numeric(raw["Million SAR"], errors="coerce").fillna(0.0)

for c in ["Criticality", "Complexity", "Ease"]:
    if c in rules.columns:
        rules[c] = pd.to_numeric(rules[c], errors="coerce")

years = sorted([int(x) for x in raw["Year"].dropna().unique().tolist()])
if not years:
    st.error("لا توجد سنوات صالحة داخل البيانات.")
    st.stop()

LATEST_YEAR = max(years)
OIL_SECTION_ID = "S05"


# ==========================================================
# ترجمة أسماء الأقسام من ملف CSV العربي
# ==========================================================
sections_ar = load_sections_ar()
section_ar_map = {}
if sections_ar is not None:
    ar_df = sections_ar[["Section", "Arabic (Short)"]].dropna().copy()
    ar_df.columns = ["Section_en", "Section_ar"]
    section_ar_map = dict(zip(ar_df["Section_en"], ar_df["Section_ar"]))


# ==========================================================
# BUILD SECTION SUMMARY
# ==========================================================
g = raw.groupby(["Year", "Section ID", "Section", "Trade Flow"], as_index=False)["Million SAR"].sum()

pvt = g.pivot_table(
    index=["Year", "Section ID", "Section"],
    columns="Trade Flow",
    values="Million SAR",
    aggfunc="sum",
    fill_value=0.0,
).reset_index()

if "Exports" not in pvt.columns:
    pvt["Exports"] = 0.0
if "Imports" not in pvt.columns:
    pvt["Imports"] = 0.0

pvt["Gap"] = pvt["Imports"] - pvt["Exports"]

df_all = pvt.merge(rules, on=["Section ID", "Section"], how="left")

for c in ["Criticality", "Complexity", "Ease"]:
    if c not in df_all.columns:
        df_all[c] = np.nan
    med = float(df_all[c].median()) if df_all[c].notna().any() else 3.0
    df_all[c] = df_all[c].fillna(med)

# Top1_share
imp = raw[raw["Trade Flow"] == "Imports"].copy()
imp_sec = imp.groupby(["Year", "Section ID", "Country"], as_index=False)["Million SAR"].sum()
imp_tot = imp_sec.groupby(["Year", "Section ID"], as_index=False)["Million SAR"].sum().rename(columns={"Million SAR": "Total"})
imp_sec = imp_sec.merge(imp_tot, on=["Year", "Section ID"], how="left")
imp_sec["Share"] = safe_div(imp_sec["Million SAR"], imp_sec["Total"])

top1 = (
    imp_sec.sort_values(["Year", "Section ID", "Share"], ascending=[True, True, False])
    .groupby(["Year", "Section ID"], as_index=False)
    .first()
)[["Year", "Section ID", "Share"]].rename(columns={"Share": "Top1_share"})

df_all = df_all.merge(top1, on=["Year", "Section ID"], how="left")
df_all["Top1_share"] = pd.to_numeric(df_all["Top1_share"], errors="coerce").fillna(0.0)
df_all["Risk"] = df_all["Top1_share"] * df_all["Criticality"]

# ترجمة أسماء الأقسام للعربي (من ملف CSV أولاً، ثم fallback)
df_all["Section_AR"] = df_all["Section"].map(section_ar_map)
if df_all["Section_AR"].isna().any():
    # fallback dictionary for any sections not in the CSV
    SECTION_AR_FALLBACK = {
        "Live Animals; Animal Products": "حيوانات حية ومنتجات حيوانية",
        "Vegetable Products": "منتجات نباتية",
        "Animal or Vegetable Fats and Oils": "دهون وزيوت حيوانية أو نباتية",
        "Prepared Foodstuffs; Beverages, Spirits and Vinegar; Tobacco": "أغذية محضرة ومشروبات وتبغ",
        "Mineral Products": "منتجات معدنية",
        "Products of the Chemical or Allied Industries": "منتجات كيميائية",
        "Plastics and Articles Thereof; Rubber and Articles Thereof": "لدائن ومطاط",
        "Raw Hides and Skins, Leather, Furskins and Articles Thereof": "جلود وفراء",
        "Wood and Articles of Wood; Wood Charcoal": "أخشاب ومصنوعاتها",
        "Pulp of Wood; Paper and Paperboard": "لب الخشب وورق",
        "Textiles and Textile Articles": "منسوجات ومصنوعاتها",
        "Footwear, Headgear, Umbrellas": "أحذية وأغطية رأس",
        "Articles of Stone, Plaster, Cement, Asbestos": "مصنوعات حجرية وإسمنتية",
        "Natural or Cultured Pearls, Precious Stones, Precious Metals": "أحجار كريمة ومعادن ثمينة",
        "Base Metals and Articles of Base Metal": "معادن عادية ومصنوعاتها",
        "Machinery and Mechanical Appliances; Electrical Equipment": "آلات ومعدات كهربائية",
        "Vehicles, Aircraft, Vessels and Associated Transport Equipment": "مركبات وطائرات وسفن",
        "Optical, Photographic, Cinematographic, Medical Instruments": "أجهزة بصرية وطبية",
        "Arms and Ammunition; Parts and Accessories Thereof": "أسلحة وذخائر",
        "Miscellaneous Manufactured Articles": "مصنوعات متنوعة",
        "Works of Art, Collectors' Pieces and Antiques": "فنون وتحف",
    }
    mask = df_all["Section_AR"].isna()
    df_all.loc[mask, "Section_AR"] = df_all.loc[mask, "Section"].map(SECTION_AR_FALLBACK)
    df_all["Section_AR"] = df_all["Section_AR"].fillna(df_all["Section"])


# ==========================================================
# PAGE
# ==========================================================
st.markdown("##  لوحة التحليل الاستراتيجي للتجارة غير النفطية")

# Focus on NON-OIL sections
df_non = df_all[df_all["Section ID"] != OIL_SECTION_ID].copy()
df_latest = df_non[df_non["Year"] == LATEST_YEAR].copy()

# حساب بيانات ندلب
lens = df_latest.copy()
lens["Bucket"] = lens["Section_AR"].apply(assign_bucket)
bucket = lens.groupby("Bucket", as_index=False).agg(
    Imports=("Imports", "sum"),
    AvgTop1=("Top1_share", "mean"),
).sort_values("Imports", ascending=False)


# ==========================================================
# بطاقات ندلب (بستايل st.metric)
# ==========================================================
st.markdown("###  حجم الواردات حسب نوع القطاع")
st.markdown(
    "تم تصنيف الأقسام التجارية إلى 5 مجموعات رئيسية. "
    "كل بطاقة توضح إجمالي واردات المجموعة، ومتوسط نسبة الاعتماد على أكبر دولة موردة فيها."
)
st.write("")

to_show = bucket.head(5).copy()
bcols = st.columns(len(to_show))
for i, (_, r) in enumerate(to_show.iterrows()):
    icon = BUCKET_ICON.get(r["Bucket"], "🧩")
    with bcols[i]:
        st.metric(
            label=f"{icon} {r['Bucket']}",
            value=fmt_msar(r["Imports"]),
            delta=f"اعتماد على مورد واحد: {pct(r['AvgTop1'])}",
            delta_color="off",
        )

st.markdown("---")


# ==========================================================
# BUMP CHART — تغير ترتيب القطاعات عبر السنوات
# ==========================================================
st.markdown("###  تغيّر ترتيب القطاعات في الصادرات غير النفطية")
st.markdown(
    "يوضح هذا الرسم كيف تغيّر ترتيب أكبر 12 قطاعاً من حيث الصادرات عبر السنوات. "
    "الترتيب 1 يعني القطاع الأعلى تصديراً. يساعدك على اكتشاف القطاعات الصاعدة والمتراجعة."
)
st.write("")

# أكبر 12 قطاع حسب متوسط الصادرات
avg_exp = df_non.groupby(["Section ID", "Section", "Section_AR"], as_index=False)["Exports"].mean()
top_sections = avg_exp.sort_values("Exports", ascending=False).head(12)[["Section ID", "Section", "Section_AR"]]

b = df_non.merge(top_sections, on=["Section ID", "Section", "Section_AR"], how="inner")
b = b[["Year", "Section_AR", "Exports"]].copy()

b["الترتيب"] = b.groupby("Year")["Exports"].rank(method="dense", ascending=False)

# ألوان متناسقة
colors = px.colors.qualitative.Set3[:12]

fig_bump = px.line(
    b.sort_values(["Year", "الترتيب"]),
    x="Year",
    y="الترتيب",
    color="Section_AR",
    markers=True,
    color_discrete_sequence=colors,
)
fig_bump.update_layout(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="#f9fafb",
    font=dict(color="#111827", family="Tajawal, Arial"),
    margin=dict(l=20, r=20, t=10, b=20),
    height=500,
    legend=dict(orientation="v", title="القطاع"),
)
fig_bump.update_yaxes(autorange="reversed", title="الترتيب", dtick=1)
fig_bump.update_xaxes(title="السنة", dtick=1, gridcolor="rgba(17,24,39,0.08)")
fig_bump.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>السنة: %{x}<br>الترتيب: %{y:.0f}<extra></extra>",
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_bump, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")


# ==========================================================
# TREEMAP — تركيب صادرات غير النفط حسب القطاع
# ==========================================================
st.markdown("###  خريطة صادرات غير النفط حسب القطاع")
st.markdown(
    "توضح هذه الخريطة الشجرية حصة كل قطاع من إجمالي الصادرات غير النفطية. "
    "كلما كان المربع أكبر، كانت حصة القطاع أعلى. مرر الماوس لمعرفة التفاصيل."
)
st.write("")

non_sec_latest = df_latest.groupby(["Section ID", "Section_AR"], as_index=False).agg(Exports=("Exports", "sum"))
non_sec_latest = non_sec_latest.sort_values("Exports", ascending=False)

top_n = 15
top15 = non_sec_latest.head(top_n).copy()
rest = non_sec_latest.iloc[top_n:].copy()
others_val = float(rest["Exports"].sum()) if len(rest) else 0.0
if others_val > 0:
    top15 = pd.concat(
        [top15, pd.DataFrame([{"Section ID": "OTH", "Section_AR": "أخرى", "Exports": others_val}])],
        ignore_index=True,
    )

total_exp = top15["Exports"].sum()
top15["الحصة"] = (top15["Exports"] / total_exp * 100).round(1)
top15["المجموعة"] = f"صادرات غير النفط — {LATEST_YEAR}"

fig_tree = px.treemap(
    top15,
    path=["المجموعة", "Section_AR"],
    values="Exports",
    color="الحصة",
    color_continuous_scale=["#dbeafe", "#3b82f6", "#1e3a5f"],
)
fig_tree.update_layout(
    template="plotly_white",
    paper_bgcolor="white",
    font=dict(color="#111827", family="Tajawal, Arial"),
    margin=dict(l=10, r=10, t=10, b=10),
    height=450,
    coloraxis_showscale=False,
)
fig_tree.update_traces(
    textinfo="label",
    textfont=dict(size=14),
    hovertemplate="<b>%{label}</b><br>الصادرات: %{value:,.0f} مليون ريال<br>الحصة: %{color:.1f}%<extra></extra>",
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_tree, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")


# ==========================================================
# WORLD MAP — انتشار صادرات غير النفط حسب الدولة
# ==========================================================
st.markdown("###  انتشار صادرات غير النفط حسب الدولة")
st.markdown(
    "توضح هذه الخريطة توزيع الصادرات السعودية غير النفطية على دول العالم. "
    "كلما كان اللون أغمق، كانت قيمة الصادرات لتلك الدولة أعلى."
)
st.write("")

base_non_exp_latest = raw[
    (raw["Year"] == LATEST_YEAR) &
    (raw["Trade Flow"] == "Exports") &
    (raw["Section ID"] != OIL_SECTION_ID)
].copy()
by_cty_latest = base_non_exp_latest.groupby("Country", as_index=False)["Million SAR"].sum().sort_values("Million SAR", ascending=False)

fig_map = px.choropleth(
    by_cty_latest,
    locations="Country",
    locationmode="country names",
    color="Million SAR",
    hover_name="Country",
    color_continuous_scale=["#ADE5AF", "#118815", "#026C05"],
    labels={"Million SAR": "مليون ريال"},
)
fig_map.update_layout(
    template="plotly_white",
    paper_bgcolor="white",
    font=dict(color="#111827", family="Tajawal, Arial"),
    margin=dict(l=20, r=20, t=10, b=20),
    height=450,
    coloraxis_colorbar=dict(title="مليون ريال"),
)
fig_map.update_geos(
    showcountries=True,
    countrycolor="rgba(17,24,39,0.18)",
    showcoastlines=True,
    coastlinecolor="rgba(17,24,39,0.12)",
    showland=True,
    landcolor="rgba(17,24,39,0.02)",
    bgcolor="white",
)
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>الصادرات: %{z:,.0f} مليون ريال<extra></extra>"
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_map, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
