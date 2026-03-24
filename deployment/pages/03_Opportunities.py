import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nav import sidebar_nav

# ============================
# إعداد الصفحة
# ============================
st.set_page_config(page_title="فجوة الأقسام التجارية", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            direction: rtl;
            text-align: right;
        }

        .stSelectbox label,
        .stMarkdown,
        .stMetric,
        .stPlotlyChart {
            text-align: right;
        }

        .block-container {
            padding-top: 2rem;
        }

        /* بطاقة القسم الأعلى */
        .top-section-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #dee2e6;
            border-radius: 16px;
            padding: 24px;
            margin: 12px 0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .top-section-card:hover {
            transform: scale(1.01);
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        }
        .top-section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #495057;
            margin-bottom: 8px;
        }
        .top-section-name {
            font-size: 1.6rem;
            font-weight: 900;
            color: #111827;
            margin-bottom: 12px;
        }
        .top-section-stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
            margin-top: 10px;
        }
        .top-stat {
            background: white;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            border: 1px solid #e5e7eb;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .top-stat:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .top-stat-label {
            font-size: 0.82rem;
            color: #6b7280;
            margin-bottom: 4px;
        }
        .top-stat-value {
            font-size: 1.15rem;
            font-weight: 800;
            color: #111827;
        }

        /* مربعات المؤشرات */
        .kpi-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin: 8px 0;
        }
        .kpi-box {
            background: #ffffff;
            border: 1.5px solid #e5e7eb;
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            height: 130px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-box:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .kpi-box-label {
            font-size: 0.9rem;
            color: #6b7280;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .kpi-box-value {
            font-size: 1.5rem;
            font-weight: 900;
            color: #111827;
        }
        .kpi-box-sub {
            font-size: 0.82rem;
            color: #9ca3af;
            margin-top: 4px;
        }

        /* خلفية خفيفة للرسمة */
        .chart-container {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px;
            margin: 8px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ─── التنقل الموحد ───
sidebar_nav()

# ============================
# مسار مجلد البيانات (نسبي)
# ============================
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ============================
# تحميل بيانات ملخص الأقسام
# ============================
@st.cache_data
def load_section_summary():
    data_path = DATA_DIR / "section_summary.csv"
    df_ = pd.read_csv(data_path)
    df_.columns = [str(c).strip() for c in df_.columns]
    return df_

df = load_section_summary()

# ============================
# تحديد الأعمدة بمرونة
# ============================
def pick_col(cols, candidates):
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

col_year = pick_col(df.columns, ["Year"])
col_section_id = pick_col(df.columns, ["Section ID", "SectionID", "Section_Id", "section_id"])
col_section = pick_col(df.columns, ["Section", "Section Name", "Section_Name"])
col_exports = pick_col(df.columns, ["Exports", "Export"])
col_imports = pick_col(df.columns, ["Imports", "Import"])
col_gap = pick_col(df.columns, ["Gap", "Deficit", "Balance"])

required = {
    "Year": col_year,
    "Section ID": col_section_id,
    "Section": col_section,
    "Exports": col_exports,
    "Imports": col_imports,
    "Gap": col_gap
}

missing = [k for k, v in required.items() if v is None]
if missing:
    st.error(f"أعمدة ناقصة أو أسماؤها مختلفة في section_summary.csv: {missing}")
    st.write("الأعمدة الموجودة:", df.columns.tolist())
    st.stop()

df = df.rename(columns={
    col_year: "Year",
    col_section_id: "Section ID",
    col_section: "Section",
    col_exports: "Exports",
    col_imports: "Imports",
    col_gap: "Gap",
}).copy()

# ============================
# تحميل أسماء الأقسام بالعربي
# ============================
@st.cache_data
def load_arabic_sections():
    candidates = [
        DATA_DIR / "sections_arabic_gastat_short.xlsx",
        DATA_DIR / "sections_arabic_gastat_short.csv",
        DATA_DIR / "sections_arabic_gastat_short1.xlsx",
        DATA_DIR / "sections_arabic_gastat_short1.csv",
    ]
    for p in candidates:
        if p.exists():
            if p.suffix == ".xlsx":
                df_ar = pd.read_excel(p)
            else:
                df_ar = pd.read_csv(p)
            df_ar.columns = [str(c).strip() for c in df_ar.columns]
            return df_ar

    st.warning(
        "⚠️ ملف السكاشن بالعربي غير موجود داخل مجلد data. "
        "ضع واحدًا من هذه الملفات: sections_arabic_gastat_short.xlsx أو sections_arabic_gastat_short1.csv"
    )
    return None

df_ar = load_arabic_sections()

def pick_col_ar(cols, candidates):
    cols_lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

if df_ar is not None:
    col_ar_id = pick_col_ar(df_ar.columns, ["Section ID", "SectionID", "Section_Id", "section_id"])
    col_ar_name = (
        pick_col_ar(df_ar.columns, ["Arabic (Short)"])
        or pick_col_ar(df_ar.columns, ["Arabic (New - GASTAT)"])
        or pick_col_ar(df_ar.columns, ["Section Arabic", "Section_AR", "Section_Arabic", "Arabic Name", "Arabic"])
        or pick_col_ar(df_ar.columns, ["Section"])
    )

    if col_ar_id is not None and col_ar_name is not None:
        df_ar = df_ar.rename(columns={
            col_ar_id: "Section ID",
            col_ar_name: "Section_Arabic"
        }).copy()

        df_ar["Section ID"] = df_ar["Section ID"].astype(str).str.strip()
        df_ar["Section_Arabic"] = df_ar["Section_Arabic"].astype(str).str.strip()

        df["Section ID"] = df["Section ID"].astype(str).str.strip()
        df = df.merge(df_ar[["Section ID", "Section_Arabic"]], on="Section ID", how="left")

        df["Section"] = df["Section_Arabic"].where(
            df["Section_Arabic"].notna() & (df["Section_Arabic"] != ""),
            df["Section"]
        )
        df.drop(columns=["Section_Arabic"], inplace=True)

# ============================
# تنظيف البيانات
# ============================
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
for c in ["Exports", "Imports", "Gap"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=["Year", "Section"]).copy()
df["Year"] = df["Year"].astype(int)

df["Section"] = df["Section"].astype(str).str.strip()
df = df[df["Section"] != ""].copy()

# ============================
# دوال التنسيق
# ============================
def format_currency_million(value, force_abs=False):
    if value is None or pd.isna(value):
        return "—"
    v = abs(value) if force_abs else value
    if abs(value) >= 1000:
        return f"{v/1000:.2f} مليار ريال"
    return f"{v:.2f} مليون ريال"

def safe_div(a, b):
    if b is None or pd.isna(b) or b == 0:
        return None
    return a / b

def fmt_pct(x):
    if x is None or pd.isna(x):
        return "—"
    return f"{x*100:.1f}%"

# ============================
# عنوان الصفحة
# ============================
st.markdown("##  فجوة الأقسام التجارية")
st.markdown("تحديد الأقسام التي تعاني من أكبر فجوة بين الواردات والصادرات، لتوجيه جهود التوطين وتقليل الاعتماد على الاستيراد.")
st.markdown("---")

# ============================
# الفلاتر
# ============================
years = sorted(df["Year"].unique().tolist())
selected_year = st.selectbox("اختر السنة", years, index=len(years) - 1)

mode = st.radio(
    "نوع العرض",
    options=["أكبر 10 أقسام عجزاً", "أكبر 10 أقسام فائضاً"],
    horizontal=True
)

df_y = df[df["Year"] == selected_year].copy()

# حساب الإجماليات
total_gap_all = df_y["Gap"].sum() if len(df_y) else 0.0
num_sections = df_y["Section"].nunique()
num_deficit = int((df_y["Gap"] > 0).sum())
num_surplus = int((df_y["Gap"] < 0).sum())

# تحديد أعلى 10 حسب نوع العرض
is_deficit_mode = mode.startswith("أكبر 10 أقسام عجز")

if is_deficit_mode:
    top10 = df_y.sort_values("Gap", ascending=False).head(10).copy()
    chart_title = f"أكبر 10 أقسام من حيث العجز التجاري — {selected_year}"
    bar_color = "#118815"
    top10_plot = top10.sort_values("Gap", ascending=True).copy()
else:
    top10 = df_y.sort_values("Gap", ascending=True).head(10).copy()
    chart_title = f"أكبر 10 أقسام من حيث الفائض التجاري — {selected_year}"
    bar_color = "#004EF7"
    top10_plot = top10.sort_values("Gap", ascending=False).copy()

# حساب نسب المساهمة
top10_total_gap = top10["Gap"].sum() if len(top10) else 0.0
if len(top10):
    top10["مساهمة_من_العشرة"] = top10["Gap"].apply(lambda x: safe_div(x, top10_total_gap))
    top10["مساهمة_من_الكل"] = top10["Gap"].apply(lambda x: safe_div(x, total_gap_all))
else:
    top10["مساهمة_من_العشرة"] = None
    top10["مساهمة_من_الكل"] = None

# ترتيب
top10_ranked = top10.copy()
top10_ranked = top10_ranked.sort_values("Gap", ascending=not is_deficit_mode)
top10_ranked["الترتيب"] = range(1, len(top10_ranked) + 1)

# ============================
# المؤشرات الرئيسية
# ============================
k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        label=f"إجمالي الفجوة ({selected_year})",
        value=format_currency_million(total_gap_all)
    )

with k2:
    st.metric(
        label="عدد الأقسام",
        value=f"{num_sections} قسم",
        delta=f"عجز: {num_deficit} | فائض: {num_surplus}",
        delta_color="off"
    )

with k3:
    if len(top10_ranked):
        top_row = top10_ranked.iloc[0]
        top_name = str(top_row["Section"])
        top_gap = float(top_row["Gap"])
        mode_label = "عجزاً" if is_deficit_mode else "فائضاً"
        st.metric(
            label=f"القسم الأعلى {mode_label} ({selected_year})",
            value=top_name,
            delta=format_currency_million(top_gap),
            delta_color="off"
        )
    else:
        st.metric(label="القسم الأعلى", value="—")

st.markdown("---")

# ============================
# الرسم البياني: أعلى 10 أقسام
# ============================
rank_map = dict(zip(top10_ranked["Section"], top10_ranked["الترتيب"]))
top10_plot["الترتيب"] = top10_plot["Section"].map(rank_map)
top10_plot["التسمية"] = top10_plot.apply(lambda r: f"{int(r['الترتيب']):02d} — {r['Section']}", axis=1)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=top10_plot["Gap"].abs() if is_deficit_mode else top10_plot["Gap"],
    y=top10_plot["التسمية"],
    orientation="h",
    marker_color=bar_color,
    customdata=top10_plot[["Imports", "Exports", "Gap"]].values,
    hovertemplate=(
        "القسم: %{y}<br>"
        "الواردات: %{customdata[0]:,.2f} مليون ريال<br>"
        "الصادرات: %{customdata[1]:,.2f} مليون ريال<br>"
        "الفجوة: %{customdata[2]:,.2f} مليون ريال"
        "<extra></extra>"
    )
))

fig.update_layout(
    title=chart_title,
    xaxis_title="حجم الفجوة (مليون ريال)",
    yaxis_title="",
    height=560,
    margin=dict(l=30, r=30, t=70, b=40),
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(249,250,251,1)",
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================
# جدول التفاصيل
# ============================
st.markdown("### تفاصيل أعلى 10 أقسام")

table_view = top10_ranked[[
    "الترتيب", "Section ID", "Section", "Imports", "Exports", "Gap",
    "مساهمة_من_العشرة", "مساهمة_من_الكل"
]].copy()

table_view.columns = [
    "الترتيب", "رمز القسم", "اسم القسم", "الواردات", "الصادرات", "الفجوة",
    "مساهمة من أعلى 10", "مساهمة من الإجمالي"
]

st.dataframe(
    table_view.style.format({
        "الواردات": "{:,.2f}",
        "الصادرات": "{:,.2f}",
        "الفجوة": "{:,.2f}",
        "مساهمة من أعلى 10": lambda x: fmt_pct(x),
        "مساهمة من الإجمالي": lambda x: fmt_pct(x),
    }),
    use_container_width=True
)

with st.expander("عرض جميع الأقسام للسنة المختارة"):
    all_view = df_y[["Section ID", "Section", "Imports", "Exports", "Gap"]].copy()
    all_view.columns = ["رمز القسم", "اسم القسم", "الواردات", "الصادرات", "الفجوة"]
    st.dataframe(all_view, use_container_width=True)
