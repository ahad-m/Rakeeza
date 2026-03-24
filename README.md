[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/rNvrpcun)


#  رَكيزة (Rakeeza)
**حيث تُبنى القرارات على أساس**

---

## 1. Project Idea & Motivation

**Rakeeza** is an interactive data analytics dashboard designed to support strategic decision-making for industrial localization in Saudi Arabia. The project was born out of the core objectives of **Saudi Vision 2030** and the **National Industrial Development and Logistics Program (NIDLP)**, which aim to diversify the economy, reduce import dependency, and enhance local manufacturing capabilities.

The central idea is to transform raw foreign trade data into actionable insights by answering critical questions:

-   Which economic sectors have the largest **trade gaps** (Imports vs. Exports), representing the biggest opportunities for localization?
-   How **dependent** are we on single countries for critical supplies?
-   What are the **trends** in these gaps and dependencies over time?
-   Who are the **alternative suppliers** for high-dependency sectors?

By providing clear, data-driven answers through an intuitive dashboard, Rakeeza serves as a compass for investors, policymakers, and industrial planners to identify and prioritize localization efforts.

## 2. Data Collection & Source

The analysis is based on publicly available foreign trade data from the **Saudi General Authority for Statistics (GASTAT)**.

-   **Dataset:** GASTAT Foreign Trade Data (2022-2024)
-   **Scope:** The data covers import and export values (in Million SAR) between Saudi Arabia and ~199 countries across 21 main trade sections.
-   **Collection:** The raw data was downloaded as a CSV file (`gastat_foreign_trade.csv`) and serves as the single source of truth for this project.

## 3. Data Cleaning & Processing

A systematic data cleaning process was performed in the `notebooks/data_cleaning.ipynb` notebook to ensure the data was accurate, consistent, and ready for analysis. The key steps included:

| Step | Description | Outcome |
| :--- | :--- | :--- |
| **1. Handle Missing Values** | Ensured that key identifiers and values were complete. | More reliable aggregations. |
| **2. Standardize Section IDs** | Corrected inconsistent section codes (e.g., `S1` to `S01`) and mapped long text descriptions to their official 21 section codes. | A single, canonical identifier for each of the 21 trade sections. |
| **3. Standardize Trade Flow** | Unified values like "Import" and "Export" to a consistent format ("Imports", "Exports"). | Accurate pivoting and analysis. |
| **4. Convert Data Types** | Converted `Year` and `Million SAR` columns to numeric types for calculations. | Enabled mathematical operations and time-series analysis. |

The cleaned dataset was saved as `data/gastat_foreign_trade_cleaned.xlsx`, which is used by all subsequent analysis notebooks and the Streamlit dashboard.

## 4. Insights & Analysis

Insights were generated through a series of focused analysis notebooks, with each building on the last to create a comprehensive picture.

#### Key Analytical Outputs:

1.  **Section Summary (`section_summary.csv`):**
    This table aggregates the data to show total Imports, Exports, and the **Trade Gap** (Imports - Exports) for each of the 21 sections, for each year. It forms the basis for identifying high-potential sectors.

2.  **Supplier Fingerprint (`section_supplier_fingerprint_2024.csv`):**
    This crucial analysis drills down into the 2024 import data to calculate **supplier dependency**. For each section, it identifies the top supplier's market share (`top1_share`), the combined share of the top 5 suppliers, and the top 2 alternative suppliers.

3.  **Criticality Matrix (`Criticality,Complexity,Ease_Table.xlsx`):**
    A qualitative layer was added by scoring each section on its **Criticality**, **Complexity**, and **Ease of Localization**. This helps prioritize not just the biggest gaps, but the most strategic ones.

#### Core Insights:

-   **Top Opportunity:** The analysis consistently highlights sectors like **Machinery & Mechanical Appliances (S16)** and **Vehicles & Aircraft (S17)** as having the largest trade gaps, making them prime candidates for localization.
-   **High Dependency Risk:** Sectors such as **Arms & Ammunition (S19)** show over 60% dependency on a single country, posing a significant supply chain risk.
-   **Strategic View:** The dashboard combines these insights, allowing a user to see, for example, a sector with a large gap, high dependency, and high criticality, making it a top-priority focus area.
-   **Concentration Structure Insight:** The comparison between top1_share and top5_share reveals distinct dependency patterns across sectors. Some sectors exhibit single-country concentration risk, while others demonstrate clustered dependency within a limited group of suppliers, highlighting structural supply vulnerability.
-   **Shift in Trade Balance – Chemical Industry Sector** 
Why did Saudi Arabia maintain a trade surplus in the Products of Chemical Industries sector during 2022–2023, and what factors led to the weakening (or slight reversal) of that surplus in 2024?

## 5. Deployment: The Rakeeza Dashboard

To make these insights accessible and interactive, an online dashboard was developed using **Streamlit** and deployed for live access.

-   **URL:** 
-   **Technology:** Python, Streamlit, Pandas, Plotly.

The dashboard is structured into several pages, each designed to answer a specific question:

| Page | Purpose |
| :--- | :--- |
| **🏠 الرئيسية** | Introduces the project, its goals, and the analysis journey. |
| **📈 الاتجاهات** | Visualizes the overall trends of imports, exports, and the trade balance over time. |
| **📊 فجوة الأقسام** | Ranks the 21 sections by the size of their trade gap to pinpoint the largest opportunities. |
| **🧷 الاعتماد** | Analyzes and visualizes supplier concentration and dependency risks for each section. |
| **🔎 تفاصيل الموردين** | An interactive page to drill down into any section and see its top suppliers and alternatives. |
| **🧭 التحليل الاستراتيجي** | A summary dashboard that brings together key metrics for a high-level strategic overview. |

## 6. Project Structure

```
├── data/                # Raw, processed, and summary data files
├── notebooks/           # Jupyter notebooks for cleaning, EDA, and analysis
├── deployment/          # Streamlit dashboard source code
│   ├── Home.py
│   ├── pages/
│   └── assets/
├── slides     # presentation slides
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 7. Usage

1.  **Clone the repository:**
    ```bash
    git clone [repo_url]
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Streamlit Dashboard:**
    ```bash
    streamlit run deployment/Home.py
    ```

## 8. Team Members

-   Ahad Alotaibi
-   Alanoud Alqahtani 
-   Majid Alnodali
-   Abdulsalam Alahmari

## 9. Task Ownership (Assigned To)

- **Data Cleaning & EDA** — Assigned to: **Ahad,Majid,Abdulsalam**
- **Macro Trends** — Assigned to: **Majid**
- **Section Opportunities** — Assigned to: **Majid**
- **Dependency** — Assigned to: **Abdulsalam**
- **Supplier Drilldown** — Assigned to: **Alanoud,Ahad**
- **Strategic + Map** — Assigned to: **Alanoud**
- **Interface** — Assigned to: **Developed collaboratively (all team members contributed)**
