import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nav import sidebar_nav

# ===============================
# إعداد الصفحة
# ===============================
st.set_page_config(page_title="تحليل الاعتماد والتركيز", layout="wide")
pio.templates.default = "plotly_white"

# ===============================
# CSS
# ===============================
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

.chart-description {
    color: #4b5563;
    font-size: 0.92rem;
    line-height: 1.7;
    margin-bottom: 14px;
    padding: 0 4px;
}
</style>
""", unsafe_allow_html=True)

# ─── التنقل الموحد ───
sidebar_nav()

# ===============================
# دوال مساعدة
# ===============================
def pct(x):
    try:
        return f"{x*100:.1f}%"
    except:
        return "—"

def risk_label(v):
    if v >= 0.60:
        return "مرتفع"
    if v >= 0.35:
        return "متوسط"
    return "منخفض"

def shorten(text, max_len=50):
    s = str(text)
    return s if len(s) <= max_len else s[:max_len-1] + "…"

# ===============================
# مسار مجلد البيانات (نسبي)
# ===============================
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ===============================
# تحميل البيانات
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv(DATA_DIR / "section_supplier_fingerprint_2024.csv")

df = load_data()

# ===============================
# تحميل أسماء الأقسام بالعربي
# ===============================
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
if sections_ar is None:
    st.warning("⚠️ ملف أسماء الأقسام بالعربي غير موجود في مجلد data/")
else:
    map_df = sections_ar[["Section", "Arabic (Short)"]].dropna().copy()
    map_df.columns = ["Section_en", "Section_ar"]
    df = df.merge(map_df, left_on="Section", right_on="Section_en", how="left")
    df["Section"] = df["Section_ar"].fillna(df["Section"])
    df.drop(columns=["Section_en", "Section_ar"], inplace=True)

# ===============================
# التحقق من الأعمدة المطلوبة
# ===============================
required = {"Section", "top1_country", "top1_share", "top5_share"}
missing = required - set(df.columns)
if missing:
    st.error(f"⚠️ أعمدة ناقصة في الملف: {', '.join(missing)}")
    st.stop()

# ===============================
# عنوان الصفحة
# ===============================
st.markdown("##  تحليل الاعتماد والتركيز")
st.markdown("تحديد الأقسام الأكثر اعتماداً على دولة واحدة أو عدد محدود من الدول، لتقييم مخاطر سلاسل الإمداد وتوجيه جهود تنويع الموردين.")
st.markdown("---")

# ===============================
# اختيار السنة فقط
# ===============================
if "Year" in df.columns:
    years = sorted(df["Year"].unique())
    year = st.selectbox("اختر السنة", years, index=len(years) - 1)
    df_y = df[df["Year"] == year].copy()
else:
    year = 2024
    df_y = df.copy()

TOP_N = 10

# ===============================
# المؤشرات الرئيسية (st.metric — نفس ستايل الصفحات السابقة)
# ===============================
highest_top1 = float(df_y["top1_share"].max())
highest_top5 = float(df_y["top5_share"].max())
avg_top1 = float(df_y["top1_share"].mean())

k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        label=f"أعلى اعتماد على دولة واحدة ({year})",
        value=pct(highest_top1),
    )

with k2:
    st.metric(
        label=f"أعلى تركيز على 5 دول ({year})",
        value=pct(highest_top5),
    )

with k3:
    st.metric(
        label="متوسط الاعتماد على دولة واحدة",
        value=pct(avg_top1),
    )

st.markdown("---")

# ===============================
# الرسم الأول: تركيز أفضل 5 دول (Top5)
# ===============================
st.markdown("### تركيز الواردات على أفضل 5 دول موردة")
st.markdown("كم نسبة الواردات التي تأتي من أكبر 5 دول فقط لكل قسم؟ كلما ارتفعت النسبة، قل التنوع في مصادر التوريد.")
with st.expander("شرح مفصل عن هذا المؤشر"):
    st.markdown("""
    **ماذا يقيس هذا الرسم؟**

    نسبة الواردات التي تأتي من أكبر خمس دول موردة لكل قسم تجاري.

    **كيف نقرأه؟**
    - كل ما ارتفعت النسبة، يعني أن القطاع يعتمد على عدد محدود من الدول، ومستوى التنوع فيه منخفض.
    - مثلاً إذا قسم معين نسبته 90%، هذا يعني أن 90% من وارداته تأتي من 5 دول فقط.

    **لماذا هذا مهم؟**

    التركيز العالي لا يعني بالضرورة مشكلة، لكنه يشير إلى تنوع محدود في مصادر التوريد، مما قد يشكل مخاطرة في حال حدوث اضطرابات تجارية أو سياسية.
    هذا المؤشر يساعدنا نفهم هل هناك حاجة لتوسيع قاعدة الشركاء التجاريين.
    """)

top5_df = df_y.sort_values("top5_share", ascending=False).head(TOP_N).copy()
top5_df["Section_short"] = top5_df["Section"].apply(lambda x: shorten(x, 50))

# تجميع أسماء أفضل 5 دول إذا كانت الأعمدة موجودة
top5_country_cols = [c for c in df_y.columns if c.startswith("top") and c.endswith("_country") and c != "top1_country"]
top5_country_cols = ["top1_country"] + sorted(top5_country_cols)

if len(top5_country_cols) >= 2:
    top5_df["الدول_الخمس"] = top5_df[top5_country_cols[:5]].apply(
        lambda row: "، ".join([str(v) for v in row if pd.notna(v) and str(v).strip() != ""]), axis=1
    )
else:
    top5_df["الدول_الخمس"] = top5_df.get("top1_country", "—")

top5_plot = top5_df.sort_values("top5_share", ascending=True)

fig_top5 = go.Figure()
fig_top5.add_trace(go.Bar(
    x=top5_plot["top5_share"] * 100,
    y=top5_plot["Section_short"],
    orientation="h",
    marker=dict(
        color=top5_plot["top5_share"],
        colorscale=[[0, "#C3DFC4"], [1, "#118815"]],
        showscale=False,
    ),
    text=top5_plot["top5_share"].apply(lambda v: f"{v*100:.0f}%"),
    textposition="outside",
    textfont=dict(size=12, color="#374151"),
    customdata=top5_plot[["Section", "top5_share", "الدول_الخمس"]].values,
    hovertemplate=(
        "<b style='font-size:14px'>%{customdata[0]}</b><br><br>"
        "نسبة التركيز على أفضل 5 دول: <b>%{customdata[1]:.1%}</b><br>"
        "الدول: %{customdata[2]}"
        "<extra></extra>"
    ),
))
fig_top5.update_layout(
    height=max(480, 48 * len(top5_plot)),
    margin=dict(l=200, r=20, t=10, b=50),
    yaxis=dict(tickfont=dict(size=13), automargin=True),
    xaxis=dict(title="نسبة التركيز (%)", gridcolor="#E5E7EB"),
    plot_bgcolor="rgba(249,250,251,1)",
    paper_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(font_size=13, bgcolor="white"),
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_top5, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ===============================
# الرسم الثاني: الاعتماد على دولة واحدة (Top1)
# ===============================
st.markdown("### الاعتماد على دولة واحدة")
st.markdown("كم نسبة الواردات التي تأتي من الدولة الأولى فقط لكل قسم؟ كلما ارتفعت النسبة، زادت المخاطرة.")
with st.expander("شرح مفصل عن هذا المؤشر"):
    st.markdown("""
    **ماذا يقيس هذا الرسم؟**

    نسبة الواردات التي تأتي من الدولة الأولى (الأكبر) فقط لكل قسم تجاري.

    **كيف نقرأه؟**
    - كلما ارتفعت النسبة، زاد مستوى الاعتماد على مصدر واحد.
    - مثلاً إذا قسم الأسلحة والذخائر نسبته 60%، يعني أن أكثر من نصف وارداته تأتي من دولة واحدة فقط.

    **لماذا هذا مهم؟**

    الاعتماد العالي لا يعني وجود مشكلة حالية، لكنه يشير إلى هشاشة محتملة في سلاسل الإمداد.
    في حال حدوث أي اضطراب تجاري أو سياسي مع تلك الدولة، قد يتأثر القطاع بشكل كبير.
    لذلك هذا المؤشر يساعدنا في تحديد القطاعات التي تحتاج إلى تنويع مصادر التوريد.
    """)

top1_df = df_y.sort_values("top1_share", ascending=False).head(TOP_N).copy()
top1_df["Section_short"] = top1_df["Section"].apply(lambda x: shorten(x, 50))
top1_plot = top1_df.sort_values("top1_share", ascending=True)

fig_top1 = go.Figure()
fig_top1.add_trace(go.Bar(
    x=top1_plot["top1_share"] * 100,
    y=top1_plot["Section_short"],
    orientation="h",
    marker=dict(
        color=top1_plot["top1_share"],
        colorscale=[[0, "#B1C6F4"], [1, "#004EF7"]],
        showscale=False,
    ),
    text=top1_plot["top1_share"].apply(lambda v: f"{v*100:.0f}%"),
    textposition="outside",
    textfont=dict(size=12, color="#374151"),
    customdata=top1_plot[["Section", "top1_share", "top1_country"]].values,
    hovertemplate=(
        "<b style='font-size:14px'>%{customdata[0]}</b><br><br>"
        "نسبة الاعتماد على الدولة الأولى: <b>%{customdata[1]:.1%}</b><br>"
        "الدولة: <b>%{customdata[2]}</b>"
        "<extra></extra>"
    ),
))
fig_top1.update_layout(
    height=max(480, 48 * len(top1_plot)),
    margin=dict(l=200, r=20, t=10, b=50),
    yaxis=dict(tickfont=dict(size=13), automargin=True),
    xaxis=dict(title="نسبة الاعتماد (%)", gridcolor="#E5E7EB"),
    plot_bgcolor="rgba(249,250,251,1)",
    paper_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(font_size=13, bgcolor="white"),
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_top1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ===============================
# جدول: أعلى الأقسام اعتماداً على دولة واحدة
# ===============================
st.markdown("### أعلى الأقسام اعتماداً على دولة واحدة")

top_risk = (
    df_y
    .sort_values("top1_share", ascending=False)
    .head(TOP_N)
    .rename(columns={
        "Section": "القسم",
        "top1_country": "الدولة الأولى",
        "top1_share": "نسبة الاعتماد"
    })
    [["القسم", "الدولة الأولى", "نسبة الاعتماد"]]
)

st.dataframe(
    top_risk.style.format({"نسبة الاعتماد": "{:.0%}"}),
    use_container_width=True,
    height=350
)

st.markdown("---")

# ===============================
# جدول المخاطر الكامل مع تحميل
# ===============================
st.markdown("### جدول المخاطر الكامل")

table_mode = st.selectbox("طريقة العرض", ["الكل", "المخاطر المرتفعة فقط", "مرتفع ومتوسط"], index=0)

table_df = (
    df_y.assign(مستوى_المخاطرة=df_y["top1_share"].apply(risk_label))
    .rename(columns={
        "Section": "القسم",
        "top1_country": "الدولة الأولى",
        "top1_share": "الاعتماد على دولة واحدة",
        "top5_share": "التركيز على 5 دول",
    })
    [["القسم", "الدولة الأولى", "الاعتماد على دولة واحدة", "التركيز على 5 دول", "مستوى_المخاطرة"]]
    .sort_values("الاعتماد على دولة واحدة", ascending=False)
)

if table_mode == "المخاطر المرتفعة فقط":
    table_df = table_df[table_df["مستوى_المخاطرة"] == "مرتفع"]
elif table_mode == "مرتفع ومتوسط":
    table_df = table_df[table_df["مستوى_المخاطرة"].isin(["مرتفع", "متوسط"])]

def row_style(row):
    v = row["مستوى_المخاطرة"]
    if v == "مرتفع":
        return ["background-color: #FEF2F2"] * len(row)
    if v == "متوسط":
        return ["background-color: #FFFBEB"] * len(row)
    return ["background-color: #ECFDF5"] * len(row)

st.dataframe(
    table_df.style
    .format({"الاعتماد على دولة واحدة": "{:.0%}", "التركيز على 5 دول": "{:.0%}"})
    .apply(row_style, axis=1),
    use_container_width=True,
    height=420
)

csv = table_df.to_csv(index=False).encode("utf-8-sig")
st.download_button("تحميل الجدول (CSV)", csv, f"جدول_المخاطر_{year}.csv", "text/csv")
