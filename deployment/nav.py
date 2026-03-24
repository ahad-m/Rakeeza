"""
nav.py — شريط التنقل العربي الموحد لجميع الصفحات
يتم استدعاؤه من كل صفحة بسطر واحد: from nav import sidebar_nav; sidebar_nav()
"""
import streamlit as st

# ─── قائمة الصفحات ───
PAGES = [
    {"icon": " ", "label": "الرئيسية",        "file": "Home.py"},
    {"icon": " ", "label": "الاتجاهات",        "file": "pages/02_Trends.py"},
    {"icon": " ", "label": "فجوة الأقسام",     "file": "pages/03_Opportunities.py"},
    {"icon": " ", "label": "الاعتماد",          "file": "pages/04_Dependency.py"},
    {"icon": " ", "label": "تفاصيل الموردين",  "file": "pages/05_Supplier_Drilldown.py"},
    {"icon": " ", "label": "التحليل الاستراتيجي", "file": "pages/06_Decision_Radar.py"},
]


# ─── CSS الموحد ───
_GLOBAL_CSS = """
<style>
/* ====== إخفاء القائمة الإنجليزية التلقائية بالكامل ====== */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNav"] *,
nav[data-testid="stSidebarNav"],
ul[data-testid="stSidebarNavItems"],
div[data-testid="stSidebarNavSeparator"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
}

/* ====== السايدبار دائماً يمين (RTL) ====== */
section[data-testid="stSidebar"] {
    direction: rtl !important;
    text-align: right !important;
    right: 0 !important;
    left: auto !important;
}
section[data-testid="stSidebar"] > div {
    direction: rtl !important;
    text-align: right !important;
}
section[data-testid="stSidebar"] * {
    direction: rtl !important;
    text-align: right !important;
}

/* زر فتح/إغلاق السايدبار — نقله لليمين */
button[data-testid="stSidebarCollapsedControl"],
button[kind="headerNoPadding"],
[data-testid="collapsedControl"] {
    right: 0.5rem !important;
    left: auto !important;
    direction: rtl !important;
}

/* ====== تنسيق أزرار التنقل ====== */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 14px !important;
    padding: 0.80rem 0.95rem !important;
    font-weight: 950 !important;
    direction: rtl !important;
    text-align: center !important;
    font-size: 0.95rem !important;
}

/* ====== المحتوى الرئيسي RTL ====== */
.main .block-container {
    direction: rtl !important;
}
</style>
"""


def sidebar_nav():
    """يعرض شريط التنقل العربي في الشريط الجانبي مع CSS موحد."""

    # حقن CSS الموحد (إخفاء إنجليزي + تثبيت يمين)
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("###  التنقل")
        st.caption("اختر الصفحة:")

        for page in PAGES:
            btn_label = f"{page['icon']} {page['label']}"
            if st.button(btn_label, key=f"nav_{page['file']}", use_container_width=True):
                st.switch_page(page["file"])
