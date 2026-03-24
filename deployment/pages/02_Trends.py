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
st.set_page_config(page_title="الاتجاهات الكلية", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"]  {
            direction: rtl;
            text-align: right;
        }

        .stSelectbox label,
        .stSlider label,
        .stMarkdown,
        .stMetric,
        .stPlotlyChart {
            text-align: right;
        }

        .stMetric {
            direction: rtl;
        }

        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ─── التنقل الموحد ───
sidebar_nav()

# ----------------------------
# تحميل البيانات (مسار نسبي)
# ----------------------------
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent.parent  # جذر المشروع
    data_path = base_dir / "data" / "gastat_foreign_trade_cleaned.xlsx"
    return pd.read_excel(data_path)

df = load_data()
df.columns = [str(c).strip() for c in df.columns]

# التحقق من الأعمدة المطلوبة
required_cols = ["Year", "Trade Flow", "Million SAR"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"أعمدة ناقصة في الملف: {missing}")
    st.write("الأعمدة الموجودة:", df.columns.tolist())
    st.stop()

# توحيد قيم نوع التجارة
df["Trade Flow"] = df["Trade Flow"].astype(str).str.strip().str.lower()
df["Trade Flow"] = df["Trade Flow"].replace({
    "import": "imports",
    "imports": "imports",
    "export": "export",
    "exports": "export",
})

# ----------------------------
# تجميع البيانات حسب السنة
# ----------------------------
yearly = (
    df.groupby(["Year", "Trade Flow"], dropna=False)["Million SAR"]
      .sum()
      .reset_index()
)

pivot_df = (
    yearly.pivot(index="Year", columns="Trade Flow", values="Million SAR")
          .reset_index()
          .fillna(0)
)

if "imports" not in pivot_df.columns:
    pivot_df["imports"] = 0.0
if "export" not in pivot_df.columns:
    pivot_df["export"] = 0.0

pivot_df["imports"] = pd.to_numeric(pivot_df["imports"], errors="coerce").fillna(0.0)
pivot_df["export"] = pd.to_numeric(pivot_df["export"], errors="coerce").fillna(0.0)

# حساب المؤشرات
pivot_df["Gap"] = pivot_df["export"] - pivot_df["imports"]
pivot_df["Coverage"] = pivot_df.apply(
    lambda r: (r["export"] / r["imports"]) if r["imports"] != 0 else None, axis=1
)

pivot_df = pivot_df.sort_values("Year").reset_index(drop=True)

# حساب التغير السنوي
pivot_df["imports_yoy"] = pivot_df["imports"].pct_change() * 100
pivot_df["export_yoy"] = pivot_df["export"].pct_change() * 100
pivot_df["gap_yoy"] = pivot_df["Gap"].pct_change().replace([float("inf"), float("-inf")], pd.NA) * 100
pivot_df["coverage_yoy"] = pivot_df["Coverage"].pct_change().replace([float("inf"), float("-inf")], pd.NA) * 100

# ----------------------------
# دوال التنسيق
# ----------------------------
def format_currency_million(value_million: float) -> str:
    if value_million is None or pd.isna(value_million):
        return "—"
    if abs(value_million) >= 1000:
        return f"{abs(value_million)/1000:.2f} مليار ريال"
    return f"{abs(value_million):.2f} مليون ريال"

def format_pct(p: float) -> str:
    if p is None or pd.isna(p):
        return "—"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def format_ratio(r: float) -> str:
    if r is None or pd.isna(r):
        return "—"
    return f"{r*100:.1f}%"

# ----------------------------
# عنوان الصفحة
# ----------------------------
st.markdown("##  الاتجاهات الكلية للتجارة")
st.markdown("نظرة شاملة على حركة الواردات والصادرات والفجوة التجارية ومؤشر تغطية الصادرات للواردات عبر السنوات.")
st.markdown("---")

# ----------------------------
# اختيار السنة (بدون سلايدر نطاق السنوات)
# ----------------------------
years = sorted(pivot_df["Year"].unique().tolist())

selected_year = st.selectbox("اختر سنة لعرض المؤشرات", years, index=len(years) - 1)

# عرض جميع السنوات في الرسوم البيانية
viz_df = pivot_df.copy()

st.markdown("---")

# ----------------------------
# بيانات السنة المختارة والسنة السابقة
# ----------------------------
sel_idx = pivot_df.index[pivot_df["Year"] == selected_year][0]
sel_row = pivot_df.loc[sel_idx]

prev_row = pivot_df.loc[sel_idx - 1] if sel_idx - 1 >= 0 else None
prev_year = int(prev_row["Year"]) if prev_row is not None else None

imports_val = float(sel_row["imports"])
export_val = float(sel_row["export"])
gap_val = float(sel_row["Gap"])
coverage_val = sel_row["Coverage"]

imports_yoy = sel_row["imports_yoy"]
export_yoy = sel_row["export_yoy"]
gap_yoy = sel_row["gap_yoy"]
coverage_yoy = sel_row["coverage_yoy"]

# ----------------------------
# بطاقات المؤشرات الرئيسية
# ----------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label=f"إجمالي الواردات ({selected_year})",
        value=format_currency_million(imports_val),
        delta=f"مقارنة بـ {prev_year}: {format_pct(imports_yoy)}" if prev_year else "—",
        delta_color="off"
    )

with k2:
    st.metric(
        label=f"إجمالي الصادرات ({selected_year})",
        value=format_currency_million(export_val),
        delta=f"مقارنة بـ {prev_year}: {format_pct(export_yoy)}" if prev_year else "—",
        delta_color="off"
    )

with k3:
    st.metric(
        label=f"الفجوة التجارية ({selected_year})",
        value=format_currency_million(gap_val),
        delta=f"مقارنة بـ {prev_year}: {format_pct(gap_yoy)}" if prev_year else "—",
        delta_color="off"
    )

with k4:
    if coverage_val is None or pd.isna(coverage_val):
        st.metric(
            label=f"مؤشر التغطية ({selected_year})",
            value="—",
            delta="—",
            delta_color="off"
        )
    else:
        st.metric(
            label=f"مؤشر التغطية ({selected_year})",
            value=format_ratio(float(coverage_val)),
            delta=f"مقارنة بـ {prev_year}: {format_pct(coverage_yoy)}" if prev_year else "—",
            delta_color="off"
        )

st.markdown("---")

# ----------------------------
# الرسوم البيانية
# ----------------------------
left, right = st.columns(2)

COLOR_IMPORTS = "#004EF7"
COLOR_EXPORT = "#118815"
COLOR_GAP = "#637E9B"

with left:
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=viz_df["Year"],
        y=viz_df["imports"],
        name="الواردات",
        marker_color=COLOR_IMPORTS,
        hovertemplate="السنة: %{x}<br>الواردات: %{y:,.2f} مليون ريال<extra></extra>"
    ))
    fig_bar.add_trace(go.Bar(
        x=viz_df["Year"],
        y=viz_df["export"],
        name="الصادرات",
        marker_color=COLOR_EXPORT,
        hovertemplate="السنة: %{x}<br>الصادرات: %{y:,.2f} مليون ريال<extra></extra>"
    ))
    fig_bar.update_layout(
        barmode="group",
        title="الواردات مقابل الصادرات حسب السنة",
        xaxis_title="السنة",
        yaxis_title="القيمة (مليون ريال)",
        legend_title="",
        height=430,
        margin=dict(l=30, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    # عرض الفجوة كقيمة موجبة (حجم الفجوة)
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(
        x=viz_df["Year"],
        y=viz_df["Gap"].abs(),
        mode="lines+markers",
        name="حجم الفجوة التجارية",
        line=dict(color=COLOR_GAP),
        fill="tozeroy",
        fillcolor="rgba(76, 120, 168, 0.15)",
        hovertemplate="السنة: %{x}<br>حجم الفجوة: %{y:,.2f} مليون ريال<extra></extra>"
    ))
    fig_gap.update_layout(
        title="حجم الفجوة التجارية عبر السنوات",
        xaxis_title="السنة",
        yaxis_title="حجم الفجوة (مليون ريال )",
        height=430,
        margin=dict(l=30, r=30, t=60, b=40),
        showlegend=False
    )
    st.plotly_chart(fig_gap, use_container_width=True)

# ----------------------------
# جدول الملخص السنوي
# ----------------------------
with st.expander("عرض جدول الملخص السنوي"):
    show = pivot_df[["Year", "imports", "export", "Gap", "Coverage"]].copy()
    show.columns = ["السنة", "الواردات", "الصادرات", "الفجوة التجارية", "مؤشر التغطية"]
    show["الفجوة التجارية"] = show["الفجوة التجارية"].abs()
    st.dataframe(show, use_container_width=True)
