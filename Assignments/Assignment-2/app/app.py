"""
Project Cost Estimation Tool
==============================
Module: IOT591U Enhanced Reflective Practice
Purpose: Demonstrates application of PM estimation principles (K15, S5, S6)
Methods: Function Point Analysis (FPA), COCOMO, Three-Point/PERT Estimation

Tech: Python Dash + Deployed via Render
"""

import dash
from dash import dcc, html, callback, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import json

# ============================================================
# APP INITIALISATION
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
    ],
    suppress_callback_exceptions=True,
    title="Project Cost Estimation Tool"
)
server = app.server  # Required for Render deployment

# ============================================================
# CONSTANTS - PM THEORY DATA
# ============================================================

# FPA Weight Table (Albrecht, 1979)
FPA_WEIGHTS = {
    "External Inputs (EI)": {"Simple": 3, "Average": 4, "Complex": 6},
    "External Outputs (EO)": {"Simple": 4, "Average": 5, "Complex": 7},
    "External Inquiries (EQ)": {"Simple": 3, "Average": 4, "Complex": 6},
    "Internal Logical Files (ILF)": {"Simple": 7, "Average": 10, "Complex": 15},
    "External Interface Files (EIF)": {"Simple": 5, "Average": 7, "Complex": 10},
}

# 14 General System Characteristics
GSC_NAMES = [
    "Data Communications", "Distributed Data Processing", "Performance",
    "Heavily Used Configuration", "Transaction Rate", "Online Data Entry",
    "End-User Efficiency", "Online Update", "Complex Processing",
    "Reusability", "Installation Ease", "Operational Ease",
    "Multiple Sites", "Facilitate Change"
]

# COCOMO Coefficients (Boehm, 1981)
COCOMO_PARAMS = {
    "Organic": {"a": 2.4, "b": 1.05, "c": 2.5, "d": 0.38},
    "Semi-detached": {"a": 3.0, "b": 1.12, "c": 2.5, "d": 0.35},
    "Embedded": {"a": 3.6, "b": 1.20, "c": 2.5, "d": 0.32},
}

# FP to LOC conversion ratios (Avg LOC per FP)
# Sources: QSM SLOC/FP Table + Capers Jones (1996) for Python
FP_TO_LOC = {
    "Python (Capers Jones)": 53,
    "Java": 53,
    "JavaScript": 47,
    "C#": 54,
    "C++": 50,
    "C": 97,
    ".NET": 57,
    "SQL": 21,
    "HTML": 34,
    "COBOL": 61,
    "J2EE": 46,
    "Visual Basic": 42,
    "PL/SQL": 37,
    "Oracle": 37,
    "Perl": 24,
}

# ============================================================
# LAYOUT
# ============================================================

# Navigation tabs
tabs = dbc.Tabs(
    id="main-tabs",
    active_tab="fpa",
    children=[
        dbc.Tab(label="1. FPA - Size", tab_id="fpa"),
        dbc.Tab(label="2. COCOMO - Effort", tab_id="cocomo"),
        dbc.Tab(label="3. PERT - Uncertainty", tab_id="pert"),
        dbc.Tab(label="4. Cost", tab_id="cost"),
        dbc.Tab(label="5. Summary", tab_id="summary"),
    ]
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            /* ============ MINT TEAL DESIGN SYSTEM ============ */
            :root {
                --bg-main: #f8fafc;
                --bg-card: #ffffff;
                --primary: #0f766e;
                --accent: #10b981;
                --text-dark: #1f2937;
                --text-muted: #6b7280;
                --border: #e5e7eb;
                --alert-info: #e0f2fe;
                --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
                --shadow-md: 0 4px 6px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.03);
                --radius: 12px;
            }

            * { font-family: 'EB Garamond', serif !important; }
            body { background-color: var(--bg-main) !important; color: var(--text-dark) !important; }
            .container-fluid { background-color: var(--bg-main) !important; }

            /* Typography */
            h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; font-weight: 700; color: var(--text-dark) !important; }
            h2 { font-size: 2.2rem !important; letter-spacing: -0.02em !important; }
            h4 { font-size: 1.5rem !important; }
            h5 { font-size: 1.1rem !important; text-transform: none !important; }
            p, li, label, small { color: #4b5563 !important; }
            .text-muted { color: var(--text-muted) !important; }
            strong, b { color: var(--text-dark) !important; }
            a { color: var(--primary) !important; text-decoration: none !important; }
            a:hover { color: #065f46 !important; text-decoration: underline !important; }

            /* Cards - white panels with soft shadow */
            .card { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: var(--shadow-sm) !important; border-top: 3px solid var(--primary) !important; }
            .card-body h3 { font-size: 1.5rem; font-weight: 800 !important; color: var(--primary) !important; }
            .card-body h6 { color: var(--text-muted) !important; font-weight: 500 !important; font-size: 0.82rem !important; }

            /* Tabs - wizard navigation with active indicator */
            .nav-tabs { border-bottom: 2px solid var(--border) !important; background-color: var(--bg-card) !important; border-radius: 10px 10px 0 0 !important; padding: 6px 8px !important; }
            .nav-link { font-size: 0.88rem; color: #9ca3af !important; border: none !important; padding: 10px 20px !important; border-radius: 8px !important; transition: all 0.2s !important; }
            .nav-link.active { color: #ffffff !important; background-color: var(--primary) !important; font-weight: 600 !important; box-shadow: 0 2px 8px rgba(15,118,110,0.25) !important; }
            .nav-link:hover:not(.active) { color: var(--primary) !important; background-color: #f0fdfa !important; }

            /* Tables - borderless modern style */
            .table { color: var(--text-dark) !important; background-color: var(--bg-card) !important; border-color: var(--border) !important; border-collapse: separate !important; border-spacing: 0 !important; }
            .table thead th { background-color: #f0fdfa !important; color: var(--primary) !important; border-bottom: 2px solid var(--border) !important; font-weight: 600 !important; font-size: 0.85rem !important; text-transform: uppercase !important; letter-spacing: 0.03em !important; }
            .table td { border-color: var(--border) !important; color: #374151 !important; background-color: var(--bg-card) !important; padding: 10px 12px !important; }
            .table-striped tbody tr:nth-of-type(odd) td { background-color: var(--bg-card) !important; }
            .table-striped tbody tr:nth-of-type(even) td { background-color: var(--bg-card) !important; }
            .table-striped > tbody > tr:nth-of-type(odd) > * { --bs-table-striped-bg: var(--bg-card) !important; background-color: var(--bg-card) !important; }
            .table-bordered { border-color: var(--border) !important; }
            .table-bordered td, .table-bordered th { border-left: none !important; border-right: none !important; }
            .table-dark, .table-dark td, .table-dark th { --bs-table-bg: var(--bg-card) !important; --bs-table-striped-bg: var(--bg-card) !important; background-color: var(--bg-card) !important; color: var(--text-dark) !important; border-color: var(--border) !important; }
            .table-dark thead th { background-color: #f0fdfa !important; color: var(--primary) !important; }
            .table-dark.table-striped > tbody > tr:nth-of-type(odd) > * { --bs-table-striped-bg: var(--bg-card) !important; background-color: var(--bg-card) !important; }
            .table > :not(caption) > * > * { background-color: var(--bg-card) !important; }

            /* Inputs & Dropdowns */
            .form-control, input[type="number"] { background-color: var(--bg-card) !important; border: 1.5px solid var(--border) !important; color: var(--text-dark) !important; border-radius: 8px !important; padding: 8px 12px !important; }
            .form-control:focus, input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.12) !important; }

            /* Buttons - teal primary with depth */
            .btn-primary { background-color: var(--primary) !important; border-color: var(--primary) !important; border-radius: 8px !important; padding: 12px 32px !important; font-weight: 600 !important; font-size: 0.95rem !important; color: #ffffff !important; box-shadow: 0 2px 4px rgba(15,118,110,0.2) !important; }
            .btn-primary:hover { background-color: #065f46 !important; box-shadow: 0 4px 12px rgba(15,118,110,0.3) !important; }
            .btn-secondary { background-color: var(--bg-main) !important; border: 1.5px solid var(--border) !important; color: #374151 !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.85rem !important; }
            .btn-secondary:hover { background-color: #f0fdfa !important; color: var(--primary) !important; border-color: var(--accent) !important; }

            /* Alerts */
            .alert-success { background-color: #ecfdf5 !important; border: none !important; border-left: 4px solid var(--accent) !important; color: #065f46 !important; border-radius: 8px !important; }
            .alert-info { background-color: var(--alert-info) !important; border: none !important; border-left: 4px solid #0ea5e9 !important; color: #0c4a6e !important; border-radius: 8px !important; padding: 14px 18px !important; }
            .alert-warning { background-color: #fffbeb !important; border: none !important; border-left: 4px solid #f59e0b !important; color: #92400e !important; border-radius: 8px !important; }

            /* Accordion */
            .accordion-button { background-color: var(--bg-main) !important; color: var(--text-dark) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; font-weight: 500 !important; }
            .accordion-button:not(.collapsed) { background-color: #f0fdfa !important; color: var(--primary) !important; font-weight: 600 !important; }
            .accordion-body { background-color: var(--bg-card) !important; color: #4b5563 !important; border-radius: 0 0 8px 8px !important; }
            .accordion-item { border-color: var(--border) !important; border-radius: 8px !important; margin-bottom: 6px !important; overflow: hidden !important; }

            /* Sliders */
            .rc-slider-track { background-color: var(--accent) !important; height: 6px !important; }
            .rc-slider-handle { border-color: var(--accent) !important; background-color: var(--bg-card) !important; width: 18px !important; height: 18px !important; margin-top: -6px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important; }
            .rc-slider-rail { background-color: #e5e7eb !important; height: 6px !important; }
            .rc-slider-mark-text { color: var(--text-muted) !important; font-size: 0.75rem !important; }

            /* Dropdown (Dash specific) */
            .Select-control { background-color: var(--bg-card) !important; border: 1.5px solid var(--border) !important; border-radius: 8px !important; }
            .Select-menu-outer { background-color: var(--bg-card) !important; border-color: var(--border) !important; border-radius: 8px !important; box-shadow: var(--shadow-md) !important; }
            .Select-option { background-color: var(--bg-card) !important; color: var(--text-dark) !important; }
            .Select-option.is-focused { background-color: #f0fdfa !important; color: var(--primary) !important; }
            .Select-value-label { color: var(--text-dark) !important; }
            .Select-placeholder { color: #9ca3af !important; }
            .Select-value { color: var(--text-dark) !important; }
            .Select-input input { color: var(--text-dark) !important; }
            .Select-arrow-zone { color: var(--text-muted) !important; }
            .dash-dropdown .Select-control { background-color: var(--bg-card) !important; border: 1.5px solid var(--border) !important; }
            .dash-dropdown .Select-value-label { color: var(--text-dark) !important; }
            .dash-dropdown .Select-menu-outer { background-color: var(--bg-card) !important; }
            .dash-dropdown .VirtualizedSelectOption { background-color: var(--bg-card) !important; color: var(--text-dark) !important; }
            .dash-dropdown .VirtualizedSelectFocusedOption { background-color: #f0fdfa !important; color: var(--primary) !important; }
            div[class*="Select"] { background-color: transparent !important; }
            .Select.is-focused > .Select-control { background-color: var(--bg-card) !important; border-color: var(--accent) !important; }
            .Select.has-value.Select--single > .Select-control { background-color: var(--bg-card) !important; }
            .Select.has-value.is-pseudo-focused.Select--single > .Select-control { background-color: var(--bg-card) !important; }

            /* Horizontal rules */
            hr { border-color: var(--border) !important; opacity: 0.5 !important; }

            /* Footer */
            .text-center.text-muted.small { color: #9ca3af !important; }

            /* UL/LI styling */
            ul { padding-left: 1.2rem !important; }
            li { margin-bottom: 0.4rem !important; }

            /* Accordion body tables */
            .accordion-body .table { background-color: var(--bg-card) !important; }
            .accordion-body .table td { background-color: var(--bg-card) !important; color: #374151 !important; font-weight: 500 !important; }
            .accordion-body .table thead th { background-color: #f0fdfa !important; color: var(--primary) !important; }

            /* Card tables - results */
            .card .table td { background-color: var(--bg-card) !important; color: var(--text-dark) !important; }
            .card .table td strong, .card .table td b { color: var(--primary) !important; font-weight: 700 !important; }
            .card .table thead th { background-color: #f0fdfa !important; color: var(--primary) !important; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Project Cost Estimation Tool", className="mt-3"),
            html.P(
                "Applying FPA, COCOMO, and PERT estimation methods to support informed project planning decisions.",
                className="text-muted"
            ),
            html.Hr()
        ])
    ]),

    # Tabs
    dbc.Row([dbc.Col(tabs)]),

    # Tab Content
    dbc.Row([dbc.Col(html.Div(id="tab-content"), className="mt-3")]),

    # Hidden stores for passing data between tabs
    dcc.Store(id="fpa-store", storage_type="session"),
    dcc.Store(id="cocomo-store", storage_type="session"),
    dcc.Store(id="pert-store", storage_type="session"),
    dcc.Store(id="cost-store", storage_type="session"),
    # Dynamic row count stores
    dcc.Store(id="pert-row-count", data=5, storage_type="session"),
    dcc.Store(id="cost-row-count", data=4, storage_type="session"),

    # Footer
    html.Hr(),
    html.P(
        "IOT591U Enhanced Reflective Practice | Sprint Week 2026 | "
        "Elias (PM) · Dami (Research) · Tomiwa (Engineering) · Amaka (QA)",
        className="text-center text-muted small"
    )
], fluid=True)


# ============================================================
# TAB CONTENT RENDERING
# ============================================================

@callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
def render_tab(tab):
    if tab == "fpa":
        return render_fpa_tab()
    elif tab == "cocomo":
        return render_cocomo_tab()
    elif tab == "pert":
        return render_pert_tab()
    elif tab == "cost":
        return render_cost_tab()
    elif tab == "summary":
        return render_summary_tab()


# ============================================================
# TAB 1: FPA
# ============================================================

def render_fpa_tab():
    func_types = list(FPA_WEIGHTS.keys())
    rows = []
    for i, ft in enumerate(func_types):
        rows.append(dbc.Row([
            dbc.Col(html.Label(ft, className="fw-bold"), width=4),
            dbc.Col(dcc.Dropdown(
                id={"type": "fpa-complexity", "index": i},
                options=[{"label": c, "value": c} for c in ["Simple", "Average", "Complex"]],
                value="Average", clearable=False
            ), width=3),
            dbc.Col(dbc.Input(
                id={"type": "fpa-count", "index": i},
                type="number", value=5, min=0
            ), width=3),
        ], className="mb-2"))

    # GSC sliders
    gsc_sliders = []
    for i, name in enumerate(GSC_NAMES):
        gsc_sliders.append(dbc.Row([
            dbc.Col(html.Small(name), width=6),
            dbc.Col(dcc.Slider(
                id={"type": "gsc-slider", "index": i},
                min=0, max=5, step=1, value=3,
                marks={0: "0", 5: "5"}
            ), width=6),
        ], className="mb-1"))

    return html.Div([
        html.H4("Function Point Analysis (FPA)"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Provides an objective measure of a software system's size and complexity, independent of the technology used to implement it."]),
            html.Li([html.Strong("Use case: "), "When requirements are well-defined and you need to quantify scope before development begins - enabling comparison across projects regardless of programming language."]),
        ], className="mb-3"),

        html.H5("Step 1: Count Function Types", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        dbc.Row([
            dbc.Col(html.Strong("Function Type", style={"fontSize": "1.1rem"}), width=4),
            dbc.Col(html.Strong("Complexity", style={"fontSize": "1.1rem"}), width=3),
            dbc.Col(html.Strong("Count", style={"fontSize": "1.1rem"}), width=3),
        ], className="mb-2"),
        *rows,

        # Complexity explanation under the table
        html.P([
            html.Strong("Complexity"), " is determined by the number of data element types (DETs) and file types referenced (FTRs/RETs):"
        ], className="text-muted small mt-2"),
        html.P([
            html.Strong("Data Functions (ILF, EIF):"), html.Br(),
            "1 record type → Low complexity", html.Br(),
            "2-5 record types → Average complexity", html.Br(),
            "6+ record types → High complexity"
        ], className="text-muted small"),
        html.P([
            html.Strong("Transactional Functions (EI, EO, EQ):"), html.Br(),
            "0-1 file types referenced → Low complexity", html.Br(),
            "2 file types referenced → Average complexity", html.Br(),
            "3+ file types referenced → High complexity"
        ], className="text-muted small"),

        # Weight explanation
        html.P([
            html.Strong("Weight"), " is a fixed value from the Albrecht standard weight table - NOT user-entered. ", html.Br(),
            "The app automatically looks up the correct weight based on your Function Type + Complexity selection. ",
            "These weights represent relative development effort derived from empirical research across hundreds of IBM projects (Albrecht, 1979). ",
            html.A("View original source (IFPUG)", href="https://www.ifpug.org/standards/fpa/", target="_blank"),
            " | ",
            html.A("QSM Function Point reference", href="https://www.qsm.com/resources/function-point-languages-table", target="_blank"),
        ], className="text-muted small"),

        # Count explanation
        html.P([
            html.Strong("Count"), " is the number of distinct instances of each function type in your system.", html.Br(),
            "Count each unique form, report, lookup, data store, or external connection separately.", html.Br(),
            "There is no maximum - larger systems simply have higher counts."
        ], className="text-muted small"),

        html.Hr(),
        html.H5("Step 2: General System Characteristics (0-5 each)", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            "Rate how much each factor influences your system's overall complexity.", html.Br(),
            "0 = no influence, 5 = strong influence.", html.Br(),
            "These 14 factors adjust the raw function point count to account for the environment the system operates in."
        ], className="text-muted small"),
        *gsc_sliders,

        html.Hr(),
        html.H5("Calculation Logic", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            html.Strong("Function Point (FP) = UFP × VAF"), html.Br(), html.Br(),
            "1. For each function type: ", html.Strong("Contribution"), " = Count × Complexity Weight (from Albrecht standard table)", html.Br(),
            "2. ", html.Strong("Unadjusted Function Points (UFP)"), " = Sum of all contributions (the raw project size)", html.Br(),
            "3. ", html.Strong("Total Degree of Influence (TDI)"), " = Sum of all 14 GSC ratings (range: 0–70)", html.Br(),
            "4. ", html.Strong("Value Adjustment Factor (VAF)"), " = 0.65 + (0.01 × TDI)  - range: 0.65–1.35", html.Br(),
            "5. ", html.Strong("Adjusted FP"), " = UFP × VAF - the final technology-independent project size"
        ], className="small"),
        html.P([
            html.A("View 14 GSC definitions (PDF)", href="https://www.jodypaul.com/SWE/FunctionPointAnalysisFundamentals.pdf", target="_blank"),
        ], className="small"),

        # Standard Weight Table Reference
        dbc.Accordion([
            dbc.AccordionItem([
                html.P("These weights were derived empirically by Albrecht at IBM (1979) from studying hundreds of completed projects. "
                       "They represent the relative development effort for each function type.", className="small text-muted"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Function Type"), html.Th("Simple"), html.Th("Average"), html.Th("Complex")])),
                    html.Tbody([
                        html.Tr([html.Td("External Inputs"), html.Td("3"), html.Td("4"), html.Td("6")]),
                        html.Tr([html.Td("External Outputs"), html.Td("4"), html.Td("5"), html.Td("7")]),
                        html.Tr([html.Td("External Inquiries"), html.Td("3"), html.Td("4"), html.Td("6")]),
                        html.Tr([html.Td("Internal Logical Files"), html.Td("7"), html.Td("10"), html.Td("15")]),
                        html.Tr([html.Td("External Interface Files"), html.Td("5"), html.Td("7"), html.Td("10")]),
                    ])
                ], bordered=True, size="sm"),
                html.P([
                    html.Strong("Why are Internal Logical Files heaviest?"), " Because databases require design, normalisation, indexing, migration, and ongoing maintenance - significantly more effort per unit than input forms.", html.Br(),
                    html.Strong("Reference: "), "Albrecht, A.J. (1979) 'Measuring Application Development Productivity', IBM Applications Development Symposium."
                ], className="small text-muted"),
            ], title="View Standard Weight Table (Albrecht, 1979)")
        ], start_collapsed=True, className="mb-3"),

        # Worked Example
        dbc.Accordion([
            dbc.AccordionItem([
                html.P("Imagine a Student Registration System:", className="fw-bold"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Function Type"), html.Th("Examples"), html.Th("Count"), html.Th("Complexity"), html.Th("Weight"), html.Th("Contribution")])),
                    html.Tbody([
                        html.Tr([html.Td("External Inputs"), html.Td("Registration form, Enrolment form"), html.Td("2"), html.Td("Average"), html.Td("4"), html.Td("8")]),
                        html.Tr([html.Td("External Outputs"), html.Td("Transcript report, Confirmation email"), html.Td("2"), html.Td("Average"), html.Td("5"), html.Td("10")]),
                        html.Tr([html.Td("External Inquiries"), html.Td("View courses, Search courses"), html.Td("2"), html.Td("Simple"), html.Td("3"), html.Td("6")]),
                        html.Tr([html.Td("Internal Logical Files"), html.Td("Students DB, Courses DB"), html.Td("2"), html.Td("Average"), html.Td("10"), html.Td("20")]),
                        html.Tr([html.Td("External Interface Files"), html.Td("Payment gateway API"), html.Td("1"), html.Td("Average"), html.Td("7"), html.Td("7")]),
                        html.Tr([html.Td(html.Strong("TOTAL")), html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td(html.Strong("UFP = 51"))]),
                    ])
                ], bordered=True, size="sm"),
                html.P([
                    "If GSC sum = 42 (moderate complexity):", html.Br(),
                    html.Strong("Adjusted FP = 51 × (0.65 + (0.01 × 42)) = 51 × 1.07 = 54.6 Function Points")
                ], className="mt-2"),
            ], title="See Worked Example (Student Registration System)")
        ], start_collapsed=True, className="mb-3"),

        html.Hr(),
        dbc.Button("Calculate FPA", id="fpa-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="fpa-results")
    ])


@callback(
    Output("fpa-results", "children"),
    Output("fpa-store", "data"),
    Input("fpa-calculate-btn", "n_clicks"),
    State({"type": "fpa-complexity", "index": ALL}, "value"),
    State({"type": "fpa-count", "index": ALL}, "value"),
    State({"type": "gsc-slider", "index": ALL}, "value"),
    prevent_initial_call=True
)
def calculate_fpa(n_clicks, complexities, counts, gsc_values):
    func_types = list(FPA_WEIGHTS.keys())
    ufp = 0
    breakdown = []

    for i, ft in enumerate(func_types):
        comp = complexities[i] if complexities[i] else "Average"
        count = counts[i] if counts[i] else 0
        weight = FPA_WEIGHTS[ft][comp]
        contribution = weight * count
        ufp += contribution
        breakdown.append({"Function Type": ft, "Complexity": comp, "Count": count, "Weight": weight, "Contribution": contribution})

    tdi = sum(v for v in gsc_values if v is not None)
    vaf = round(0.65 + 0.01 * tdi, 2)
    adjusted_fp = round(ufp * vaf, 1)

    result_data = {"ufp": ufp, "vaf": tdi, "adjusted_fp": adjusted_fp}

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results", className="card-title"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Unadjusted Function Points (UFP)"), html.H3(str(ufp))])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Degree of Influence (TDI)"), html.H3(str(tdi))])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Adjusted Function Points"), html.H3(str(adjusted_fp))])), width=4),
            ]),
            html.P(f"TDI = {tdi}  →  VAF = 0.65 + (0.01 × {tdi}) = {vaf}", className="mt-2 text-muted"),
            html.P([html.Strong(f"Adjusted FP = {ufp} × {vaf} = {adjusted_fp} Function Points")], className="mt-1"),
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 2: COCOMO
# ============================================================

def render_cocomo_tab():
    return html.Div([
        html.H4("COCOMO - Constructive Cost Model"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "An algorithmic software cost estimation model that predicts effort, cost, and schedule based on project size metrics (Boehm, 1981)."]),
            html.Li([html.Strong("Use case: "), "When you have a size estimate (from FPA or KLOC) and need to forecast staffing, timeline, and budget - supporting resource allocation decisions."]),
        ], className="mb-3"),
        # Project Classification Table
        html.H5("Project Type Classification", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Aspect"), html.Th("Organic"), html.Th("Semi-Detached"), html.Th("Embedded")])),
            html.Tbody([
                html.Tr([html.Td(html.Strong("Project Size")), html.Td("2–50 KLOC"), html.Td("50–300 KLOC"), html.Td("300+ KLOC")]),
                html.Tr([html.Td(html.Strong("Complexity")), html.Td("Low"), html.Td("Medium"), html.Td("High")]),
                html.Tr([html.Td(html.Strong("Problem Understanding")), html.Td("Well-understood, previously solved"), html.Td("Somewhat understood, partial experience"), html.Td("High ambiguity, novel domain")]),
                html.Tr([html.Td(html.Strong("Team Experience")), html.Td("Highly experienced team"), html.Td("Mixed - some experienced, some not"), html.Td("Specialised experts required")]),
                html.Tr([html.Td(html.Strong("Environment")), html.Td("Flexible, few constraints"), html.Td("Moderate constraints"), html.Td("Highly rigorous, strict operational constraints")]),
                html.Tr([html.Td(html.Strong("Example")), html.Td("Simple payroll system"), html.Td("New system interfacing with legacy"), html.Td("Flight control software")]),
            ])
        ], bordered=True, striped=True, size="sm", className="mb-3 table-dark"),

        # Coefficient Constants Table
        html.H5("COCOMO Coefficient Constants (Boehm, 1981)", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            "These constants were empirically derived from studying 63 real software projects. ",
            "They determine how effort scales with project size for each type. ",
            html.A("Source: GeeksforGeeks COCOMO", href="https://www.geeksforgeeks.org/software-engineering/software-engineering-cocomo-model/", target="_blank"),
        ], className="text-muted small"),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Project Type"), html.Th("a"), html.Th("b"), html.Th("c"), html.Th("d")])),
            html.Tbody([
                html.Tr([html.Td("Organic"), html.Td("2.4"), html.Td("1.05"), html.Td("2.5"), html.Td("0.38")]),
                html.Tr([html.Td("Semi-Detached"), html.Td("3.0"), html.Td("1.12"), html.Td("2.5"), html.Td("0.35")]),
                html.Tr([html.Td("Embedded"), html.Td("3.6"), html.Td("1.20"), html.Td("2.5"), html.Td("0.32")]),
            ])
        ], bordered=True, size="sm", className="mb-2 table-dark"),
        html.P([
            html.Strong("How constants work: "), html.Br(),
            html.Strong("a"), " (effort multiplier): Scales base effort per KLOC. Higher values for embedded projects reflect the additional overhead imposed by strict operational constraints.", html.Br(),
            html.Strong("b"), " (effort exponent): Because b > 1, effort grows faster than linearly with size - larger projects are disproportionately harder due to integration complexity and coordination costs.", html.Br(),
            html.Strong("c"), " (duration multiplier): Sets the baseline calendar time from which schedule compression is calculated.", html.Br(),
            html.Strong("d"), " (duration exponent): Because d < 1, doubling effort required does NOT double duration. This models the diminishing returns of staffing - adding more labour introduces communication friction, mathematically supporting Brooks's Law.",
        ], className="text-muted small"),

        html.Hr(),
        html.H5("Step 1: Project Size (KLOC)", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            html.Strong("KLOC = FP × (LOC/FP) ÷ 1000"), html.Br(),
            "Where LOC/FP is the industry-standard lines of code per function point for your chosen language.", html.Br(),
            html.A("Full LOC/FP table for all languages (QSM)", href="https://www.qsm.com/resources/function-point-languages-table", target="_blank"),
        ], className="text-muted small"),
        dbc.Row([
            dbc.Col([
                html.Label("KLOC (thousands of lines of code)"),
                dbc.Input(id="cocomo-kloc", type="number", value=10, min=0.1, step=0.1),
            ], width=6),
            dbc.Col([
                html.Label("Language (for FP→KLOC conversion)"),
                dcc.Dropdown(
                    id="cocomo-language",
                    options=[{"label": f"{k} ({v} LOC/FP)", "value": k} for k, v in FP_TO_LOC.items()],
                    value="Python (Capers Jones)", clearable=False
                ),
                dbc.Button("Auto-fill from FPA", id="cocomo-autofill-btn", color="secondary", size="sm", className="mt-2"),
                html.Div(id="cocomo-autofill-explanation"),
                html.Small("15 common languages shown. ", className="text-muted"),
                html.A("See full table for all languages", href="https://www.qsm.com/resources/function-point-languages-table", target="_blank", className="small"),
            ], width=6),
        ]),

        html.Hr(),
        html.H5("Step 2: Select Project Type", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        dcc.Dropdown(
            id="cocomo-type",
            options=[
                {"label": "Organic - Well-understood problem, experienced team, flexible environment (2–50 KLOC)", "value": "Organic"},
                {"label": "Semi-Detached - Partially understood problem, mixed experience, moderate constraints (50–300 KLOC)", "value": "Semi-detached"},
                {"label": "Embedded - Novel/complex domain, strict constraints, specialised experts required (300+ KLOC)", "value": "Embedded"},
            ],
            value="Organic", clearable=False
        ),

        html.Hr(),
        html.H5("Formulas", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            html.Strong("Effort (E)"), " = a × (KLOC)^b  → person-months", html.Br(),
            html.Strong("Duration (T)"), " = c × (E)^d  → calendar months", html.Br(),
            html.Strong("Team Size"), " = E ÷ T  → people required", html.Br(),
        ], className="small"),

        html.Hr(),
        dbc.Button("Calculate COCOMO", id="cocomo-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="cocomo-results")
    ])


@callback(
    Output("cocomo-kloc", "value"),
    Output("cocomo-autofill-explanation", "children"),
    Input("cocomo-autofill-btn", "n_clicks"),
    State("fpa-store", "data"),
    State("cocomo-language", "value"),
    prevent_initial_call=True
)
def autofill_kloc(n_clicks, fpa_data, language):
    if fpa_data and fpa_data.get("adjusted_fp"):
        fp = fpa_data["adjusted_fp"]
        loc_per_fp = FP_TO_LOC.get(language, 53)
        kloc = round((fp * loc_per_fp) / 1000, 2)
        explanation = html.P([
            html.Strong("Auto-filled: "), f"KLOC = {fp} FP × {loc_per_fp} LOC/FP ÷ 1000 = ", html.Strong(f"{kloc} KLOC")
        ], className="text-success small mt-1")
        return kloc, explanation
    return dash.no_update, html.P("No FPA data found. Complete FPA first.", className="text-warning small mt-1")


@callback(
    Output("cocomo-results", "children"),
    Output("cocomo-store", "data"),
    Input("cocomo-calculate-btn", "n_clicks"),
    State("cocomo-kloc", "value"),
    State("cocomo-type", "value"),
    prevent_initial_call=True
)
def calculate_cocomo(n_clicks, kloc, project_type):
    if not kloc or kloc <= 0:
        return dbc.Alert("Please enter a valid KLOC value.", color="warning"), None

    params = COCOMO_PARAMS[project_type]
    effort = round(params["a"] * (kloc ** params["b"]), 2)
    duration = round(params["c"] * (effort ** params["d"]), 2)
    team_size = round(effort / duration, 1) if duration > 0 else 0

    result_data = {"kloc": kloc, "project_type": project_type, "effort": effort, "duration": duration, "team_size": team_size}

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results", className="card-title"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Effort"), html.H3(f"{effort} person-months")])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Duration"), html.H3(f"{duration} months")])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Team Size"), html.H3(f"~{team_size} people")])), width=4),
            ]),
            html.Hr(),
            # Formula (left) | Calculation (right)
            dbc.Table([
                html.Thead(html.Tr([html.Th("Formula"), html.Th("Calculation")])),
                html.Tbody([
                    html.Tr([
                        html.Td([html.Span("E = a × (KLOC)"), html.Sup("b")]),
                        html.Td(html.Strong([f"E = {params['a']} × ({kloc})", html.Sup(f"{params['b']}"), f" = {effort} person-months"]))
                    ]),
                    html.Tr([
                        html.Td([html.Span("T = c × (E)"), html.Sup("d")]),
                        html.Td(html.Strong([f"T = {params['c']} × ({effort})", html.Sup(f"{params['d']}"), f" = {duration} months"]))
                    ]),
                    html.Tr([
                        html.Td("Team Size = E ÷ T"),
                        html.Td(html.Strong(f"Team Size = {effort} ÷ {duration} = {team_size} people"))
                    ]),
                ])
            ], bordered=True, size="sm", className="mt-2"),
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 3: PERT
# ============================================================

def render_pert_tab():
    # Default 5 tasks - step=1 for whole numbers, min=0.1 for fractional input via keyboard
    task_rows = []
    default_tasks = ["Requirements", "Design", "Development", "Testing", "Deployment", "", "", "", "", ""]
    for i in range(10):
        visible = i < 5  # First 5 visible by default
        task_rows.append(dbc.Row([
            dbc.Col(dbc.Input(id={"type": "pert-name", "index": i}, value=default_tasks[i], placeholder="Task name"), width=4),
            dbc.Col(dbc.Input(id={"type": "pert-o", "index": i}, type="number", value=2 if visible else "", min=0.1, step=0.1, placeholder="O"), width=2),
            dbc.Col(dbc.Input(id={"type": "pert-m", "index": i}, type="number", value=4 if visible else "", min=0.1, step=0.1, placeholder="M"), width=2),
            dbc.Col(dbc.Input(id={"type": "pert-p", "index": i}, type="number", value=8 if visible else "", min=0.1, step=0.1, placeholder="P"), width=2),
        ], className="mb-2", id={"type": "pert-row", "index": i}, style={} if visible else {"display": "none"}))

    return html.Div([
        html.H4("PERT - Three-Point Estimation"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Quantifies estimation uncertainty by calculating a weighted average from three scenarios (Optimistic, Most Likely, Pessimistic), producing a confidence range rather than a single-point estimate."]),
            html.Li([html.Strong("Use case: "), "When project conditions are uncertain or novel, and stakeholders need to understand the range of possible outcomes - enabling risk-aware planning and contingency justification."]),
        ], className="mb-3"),

        html.H5("Formulas", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            html.Strong("Expected (weighted mean)"), " = (O + 4M + P) / 6  - calculated per task", html.Br(),
            html.Strong("Standard Deviation (σ)"), " = (P - O) / 6  - measures uncertainty per task", html.Br(),
            html.Strong("Total Expected"), " = Sum of all task Expecteds", html.Br(),
            html.Strong("Total σ"), " = √(σ₁² + σ₂² + σ₃² + ...)  - statistical combination of independent uncertainties",
        ], className="small"),

        # Explanation dropdown
        dbc.Accordion([
            dbc.AccordionItem([
                html.P([
                    html.Strong("Expected (E)"), " is the weighted mean duration for each task. "
                    "The formula weights the Most Likely estimate 4× more heavily than Optimistic or Pessimistic, "
                    "because most outcomes cluster around the middle scenario.", html.Br(), html.Br(),
                    html.Strong("Standard Deviation (σ)"), " measures how spread out the estimate is - how uncertain you are. ", html.Br(),
                    "A task with O=3, M=4, P=5 has LOW uncertainty (σ = 0.33 weeks).", html.Br(),
                    "A task with O=2, M=4, P=12 has HIGH uncertainty (σ = 1.67 weeks).", html.Br(), html.Br(),
                    html.Strong("Why both?"), " Expected alone gives false precision. σ tells stakeholders the RANGE of likely outcomes.", html.Br(), html.Br(),
                    html.Strong("Confidence Levels (Normal Distribution):"), html.Br(),
                    "68% confidence: Expected ± 1σ (fairly sure)", html.Br(),
                    "95% confidence: Expected ± 2σ (very confident)", html.Br(),
                    "99% confidence: Expected ± 3σ (nearly certain)", html.Br(),
                    html.A("Learn more about Normal Distribution", href="https://www.scribbr.co.uk/stats/the-normal-distribution/", target="_blank"),
                ], className="small"),
            ], title="How does PERT calculation work? (Expected vs Standard Deviation)")
        ], start_collapsed=True, className="mb-3"),

        # Worked Example
        dbc.Accordion([
            dbc.AccordionItem([
                html.P("Calculation is done PER TASK, then totals are combined:", className="fw-bold"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Task"), html.Th("O"), html.Th("M"), html.Th("P"), html.Th("Expected = (O+4M+P)/6"), html.Th("σ = (P-O)/6")])),
                    html.Tbody([
                        html.Tr([html.Td("Requirements"), html.Td("1"), html.Td("2"), html.Td("5"), html.Td("(1+8+5)/6 = 2.33"), html.Td("(5-1)/6 = 0.67")]),
                        html.Tr([html.Td("Design"), html.Td("2"), html.Td("3"), html.Td("6"), html.Td("(2+12+6)/6 = 3.33"), html.Td("(6-2)/6 = 0.67")]),
                        html.Tr([html.Td("Development"), html.Td("8"), html.Td("12"), html.Td("20"), html.Td("(8+48+20)/6 = 12.67"), html.Td("(20-8)/6 = 2.00")]),
                        html.Tr([html.Td(html.Strong("TOTAL")), html.Td(""), html.Td(""), html.Td(""), html.Td(html.Strong("18.33 weeks")), html.Td(html.Strong("√(0.67²+0.67²+2.00²) = 2.19"))]),
                    ])
                ], bordered=True, size="sm"),
                html.P([
                    html.Strong("Result: "), "Expected = 18.33 weeks", html.Br(),
                    "95% confidence (±2σ): 18.33 ± 4.38 = ", html.Strong("13.95 to 22.71 weeks")
                ]),
            ], title="See Worked Example")
        ], start_collapsed=True, className="mb-3"),

        html.H5("Enter Estimates Per Phase (in weeks)", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        html.P([
            "Tasks can be edited, added, or removed as needed - every project has different phases.", html.Br(),
            html.Strong("Rule: "), "P ≥ M ≥ O > 0 (Pessimistic must be ≥ Most Likely, which must be ≥ Optimistic. All must be positive.)"
        ], className="text-muted small"),
        dbc.Row([
            dbc.Col(html.Strong("Task/Phase"), width=4),
            dbc.Col(html.Strong("Optimistic (O)"), width=2),
            dbc.Col(html.Strong("Most Likely (M)"), width=2),
            dbc.Col(html.Strong("Pessimistic (P)"), width=2),
        ], className="mb-2"),
        *task_rows,
        dbc.Row([
            dbc.Col(dbc.Button("+ Add Task", id="pert-add-btn", color="secondary", size="sm"), width=2),
            dbc.Col(dbc.Button("- Remove Task", id="pert-remove-btn", color="secondary", size="sm"), width=2),
        ], className="mb-3"),

        html.Hr(),
        dbc.Button("Calculate PERT", id="pert-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="pert-results")
    ])


# PERT Add/Remove row callbacks
@callback(
    Output("pert-row-count", "data"),
    Output({"type": "pert-row", "index": ALL}, "style"),
    Input("pert-add-btn", "n_clicks"),
    Input("pert-remove-btn", "n_clicks"),
    State("pert-row-count", "data"),
    prevent_initial_call=True
)
def update_pert_rows(add_clicks, remove_clicks, current_count):
    triggered = ctx.triggered_id
    if triggered == "pert-add-btn":
        current_count = min((current_count or 5) + 1, 10)
    elif triggered == "pert-remove-btn":
        current_count = max((current_count or 5) - 1, 1)
    styles = [{} if i < current_count else {"display": "none"} for i in range(10)]
    return current_count, styles


@callback(
    Output("pert-results", "children"),
    Output("pert-store", "data"),
    Input("pert-calculate-btn", "n_clicks"),
    State({"type": "pert-name", "index": ALL}, "value"),
    State({"type": "pert-o", "index": ALL}, "value"),
    State({"type": "pert-m", "index": ALL}, "value"),
    State({"type": "pert-p", "index": ALL}, "value"),
    State("pert-row-count", "data"),
    prevent_initial_call=True
)
def calculate_pert(n_clicks, names, o_vals, m_vals, p_vals, row_count):
    visible_count = row_count or 5
    tasks = []
    for i in range(min(visible_count, len(names))):
        name = names[i] or f"Task {i+1}"
        o = float(o_vals[i]) if (o_vals[i] is not None and o_vals[i] != "") else 0
        m = float(m_vals[i]) if (m_vals[i] is not None and m_vals[i] != "") else 0
        p = float(p_vals[i]) if (p_vals[i] is not None and p_vals[i] != "") else 0
        # Skip rows with no meaningful name and all zeros
        if not names[i] and o == 0 and m == 0 and p == 0:
            continue
        expected = round((o + 4 * m + p) / 6, 2)
        sigma = round((p - o) / 6, 2)
        tasks.append({"name": name, "o": o, "m": m, "p": p, "expected": expected, "sigma": sigma})

    # Validate P >= M >= O > 0
    violations = []
    for t in tasks:
        if not (t["p"] >= t["m"] >= t["o"] > 0):
            violations.append(f"⚠️ {t['name']}: O={t['o']}, M={t['m']}, P={t['p']} - violates rule P ≥ M ≥ O > 0")

    if violations:
        warning = dbc.Alert([
            html.Strong("⚠️ Validation Warning: "), "Some tasks violate the PERT rule (P ≥ M ≥ O > 0):", html.Br(),
            html.Ul([html.Li(v) for v in violations]),
            "Results may be unreliable. Please correct the values above."
        ], color="warning", className="mt-2")
        return warning, None

    total_expected = round(sum(t["expected"] for t in tasks), 2)
    total_sigma = round(sum(t["sigma"] ** 2 for t in tasks) ** 0.5, 2)

    result_data = {"total_expected": total_expected, "total_sigma": total_sigma, "tasks": tasks}

    # Build results table
    table_rows = [html.Tr([html.Th("Task"), html.Th("O"), html.Th("M"), html.Th("P"), html.Th("Expected"), html.Th("σ")])]
    for t in tasks:
        table_rows.append(html.Tr([html.Td(t["name"]), html.Td(t["o"]), html.Td(t["m"]), html.Td(t["p"]), html.Td(t["expected"]), html.Td(f"±{t['sigma']}")]))

    conf_68_low = max(0, round(total_expected - total_sigma, 1))
    conf_68_high = round(total_expected + total_sigma, 1)
    conf_95_low = max(0, round(total_expected - 2 * total_sigma, 1))
    conf_95_high = round(total_expected + 2 * total_sigma, 1)
    conf_99_low = max(0, round(total_expected - 3 * total_sigma, 1))
    conf_99_high = round(total_expected + 3 * total_sigma, 1)

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results"),
            dbc.Table(table_rows, bordered=True, striped=True, size="sm"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Expected"), html.H3(f"{total_expected} weeks")])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total σ"), html.H3(f"±{total_sigma} weeks")])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("68% (±1σ)"), html.H3(f"{conf_68_low}–{conf_68_high} wks")])), width=2),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("95% (±2σ)"), html.H3(f"{conf_95_low}–{conf_95_high} wks")])), width=2),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("99% (±3σ)"), html.H3(f"{conf_99_low}–{conf_99_high} wks")])), width=2),
            ]),
            html.P([
                html.A("Understanding confidence intervals (Normal Distribution)", href="https://www.scribbr.co.uk/stats/the-normal-distribution/", target="_blank")
            ], className="small mt-2 text-muted"),
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 4: COST
# ============================================================

def render_cost_tab():
    role_rows = []
    default_roles = [("Project Manager", 500, 20), ("Developer", 450, 40), ("QA Engineer", 400, 25), ("UX Designer", 400, 15), ("", 0, 0), ("", 0, 0), ("", 0, 0), ("", 0, 0)]
    for i in range(8):
        visible = i < 4
        role, rate, alloc = default_roles[i]
        role_rows.append(dbc.Row([
            dbc.Col(dbc.Input(id={"type": "cost-role", "index": i}, value=role, placeholder="Role name"), width=3),
            dbc.Col(dbc.Input(id={"type": "cost-rate", "index": i}, type="number", value=rate, min=0), width=3),
            dbc.Col(dbc.Input(id={"type": "cost-alloc", "index": i}, type="number", value=alloc, min=0, max=100), width=3),
        ], className="mb-2", id={"type": "cost-row", "index": i}, style={} if visible else {"display": "none"}))

    return html.Div([
        html.H4("Cost Contingency Calculator"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Translates effort estimates into monetary terms by factoring in team composition, role-specific daily rates, allocation percentages, and a contingency buffer for risk."]),
            html.Li([html.Strong("Use case: "), "When you need a budget figure for project approval - accounting for the reality that different roles cost differently and that all estimates carry inherent uncertainty requiring contingency."]),
        ], className="mb-3"),

        # Contingency explanation dropdown
        dbc.Accordion([
            dbc.AccordionItem([
                html.P([
                    html.Strong("What is contingency?"), html.Br(),
                    "A percentage added to the base cost to account for estimation errors, scope changes, technical surprises, and resource risks.", html.Br(), html.Br(),
                    html.Strong("Industry standard guidance:"), html.Br(),
                    "10% - Low risk: familiar project, experienced team, stable requirements.", html.Br(),
                    "20% - Moderate risk: some novel elements, partially understood domain.", html.Br(),
                    "30% - High risk: novel project, new team, unclear requirements, significant unknowns.", html.Br(), html.Br(),
                    html.Strong("Why it matters:"), html.Br(),
                    "The QuickShop case study (Week 5) demonstrated that projects without contingency are guaranteed to overrun. ",
                    "Contingency IS risk management in financial terms - it's how you respond to identified risks without needing to re-budget.", html.Br(), html.Br(),
                    html.Strong("Professional practice:"), html.Br(),
                    "Every credible PM organisation (PMI, APM) recommends contingency. Not including it is considered unprofessional.", html.Br(),
                    html.A("PMI Practice Guide: Managing Change in Organizations", href="https://www.pmi.org/", target="_blank"), " | ",
                    html.A("APM Body of Knowledge", href="https://www.apm.org.uk/body-of-knowledge/", target="_blank"),
                ], className="small"),
            ], title="How does contingency work? (Industry standards)")
        ], start_collapsed=True, className="mb-3"),

        html.H5("Team Composition", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        dbc.Row([
            dbc.Col(html.P("Roles can be edited - adjust names, rates, and allocation to match your project team.", className="text-muted small mb-0"), width=8),
            dbc.Col([
                dbc.Button("+ Add Role", id="cost-add-btn", color="secondary", size="sm", className="me-2"),
                dbc.Button("- Remove Role", id="cost-remove-btn", color="secondary", size="sm"),
            ], width=4, className="text-end"),
        ], className="mb-2 align-items-center"),
        dbc.Row([
            dbc.Col(html.Strong("Role"), width=3),
            dbc.Col(html.Strong("Daily Rate (£)"), width=3),
            dbc.Col(html.Strong("% Allocation"), width=3),
        ], className="mb-2"),
        *role_rows,

        html.Hr(),
        html.H5("Duration & Contingency", style={"fontSize": "1.3rem", "fontWeight": "700"}),
        dbc.Row([
            dbc.Col([
                html.Label("Duration (months)"),
                dbc.Input(id="cost-duration", type="number", value=6, min=0.5, step=0.5)
            ], width=4),
            dbc.Col([
                html.Label("Working days/month"),
                dbc.Input(id="cost-days-per-month", type="number", value=22, min=15, max=25)
            ], width=4),
            dbc.Col([
                html.Label("Contingency (%)"),
                dcc.Slider(id="cost-contingency", min=0, max=30, step=1, value=20,
                           marks={0: "0%", 5: "5%", 10: "10%", 15: "15%", 20: "20%", 25: "25%", 30: "30%"})
            ], width=4),
        ]),

        html.Hr(),
        dbc.Button("Calculate Cost", id="cost-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="cost-results")
    ])


# Cost Add/Remove role callbacks
@callback(
    Output("cost-row-count", "data"),
    Output({"type": "cost-row", "index": ALL}, "style"),
    Input("cost-add-btn", "n_clicks"),
    Input("cost-remove-btn", "n_clicks"),
    State("cost-row-count", "data"),
    prevent_initial_call=True
)
def update_cost_rows(add_clicks, remove_clicks, current_count):
    triggered = ctx.triggered_id
    if triggered == "cost-add-btn":
        current_count = min((current_count or 4) + 1, 8)
    elif triggered == "cost-remove-btn":
        current_count = max((current_count or 4) - 1, 1)
    styles = [{} if i < current_count else {"display": "none"} for i in range(8)]
    return current_count, styles


@callback(
    Output("cost-results", "children"),
    Output("cost-store", "data"),
    Input("cost-calculate-btn", "n_clicks"),
    State({"type": "cost-role", "index": ALL}, "value"),
    State({"type": "cost-rate", "index": ALL}, "value"),
    State({"type": "cost-alloc", "index": ALL}, "value"),
    State("cost-duration", "value"),
    State("cost-days-per-month", "value"),
    State("cost-contingency", "value"),
    State("cost-row-count", "data"),
    prevent_initial_call=True
)
def calculate_cost(n_clicks, roles, rates, allocs, duration, days_per_month, contingency_pct, row_count):
    visible_count = row_count or 4
    total_days = (duration or 6) * (days_per_month or 22)
    base_cost = 0
    breakdown = []

    for i in range(min(visible_count, len(roles))):
        role = roles[i] or f"Role {i+1}"
        rate = float(rates[i]) if rates[i] else 0
        alloc = float(allocs[i]) if allocs[i] else 0
        # Skip rows with no meaningful name and zero values
        if not roles[i] and rate == 0 and alloc == 0:
            continue
        days = total_days * (alloc / 100)
        cost = days * rate
        base_cost += cost
        breakdown.append({"Role": role, "Rate": f"£{rate:.0f}/day", "Allocation": f"{alloc}%", "Days": round(days, 1), "Cost": f"£{cost:,.0f}"})

    contingency_amount = base_cost * ((contingency_pct or 0) / 100)
    total_cost = base_cost + contingency_amount

    result_data = {"base_cost": base_cost, "contingency_pct": contingency_pct, "total_cost": total_cost, "duration": duration}

    table_header = [html.Tr([html.Th(c) for c in ["Role", "Rate", "Allocation", "Days", "Cost"]])]
    table_body = [html.Tr([html.Td(breakdown[i][c]) for c in ["Role", "Rate", "Allocation", "Days", "Cost"]]) for i in range(len(breakdown))]

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results"),
            dbc.Table(table_header + table_body, bordered=True, striped=True, size="sm"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Base Cost"), html.H3(f"£{base_cost:,.0f}")])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6(f"Contingency ({contingency_pct}%)"), html.H3(f"£{contingency_amount:,.0f}")])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Estimated Cost (Base + Contingency)"), html.H3(f"£{total_cost:,.0f}")])), width=4),
            ]),
            html.P(f"Total = Base Cost × (1 + Contingency %) = £{base_cost:,.0f} × {round(1 + contingency_pct/100, 2)} = £{total_cost:,.0f}", className="mt-2 text-muted"),
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 5: SUMMARY
# ============================================================

def render_summary_tab():
    return html.Div([
        html.H4("Comparison and Summary"),
        dbc.Alert("Complete all modules (FPA → COCOMO → PERT → Cost) then click below to generate the summary.", color="info"),
        dbc.Button("Generate Summary", id="summary-btn", color="primary", className="mb-3"),
        html.Div(id="summary-results")
    ])


@callback(
    Output("summary-results", "children"),
    Input("summary-btn", "n_clicks"),
    State("fpa-store", "data"),
    State("cocomo-store", "data"),
    State("pert-store", "data"),
    State("cost-store", "data"),
    prevent_initial_call=True
)
def generate_summary(n_clicks, fpa_data, cocomo_data, pert_data, cost_data):
    rows = []

    if fpa_data:
        rows.append(html.Tr([html.Td("FPA (Size)"), html.Td(f"{fpa_data['adjusted_fp']} Function Points"), html.Td("How big is this project?"), html.Td("Well-defined requirements")]))
    if cocomo_data:
        rows.append(html.Tr([html.Td("COCOMO (Effort)"), html.Td(f"{cocomo_data['effort']} person-months, {cocomo_data['duration']} months"), html.Td("How much effort and how long?"), html.Td("Staffing & timeline planning")]))
    if pert_data:
        rows.append(html.Tr([html.Td("PERT (Uncertainty)"), html.Td(f"{pert_data['total_expected']} weeks (±{pert_data['total_sigma']})"), html.Td("How confident are we?"), html.Td("Uncertain/novel projects")]))
    if cost_data:
        rows.append(html.Tr([html.Td("Cost Model"), html.Td(f"£{cost_data['total_cost']:,.0f} (incl. {cost_data['contingency_pct']}%)"), html.Td("How much will it cost?"), html.Td("Budget approval")]))

    if not rows:
        return dbc.Alert("No data yet. Please complete at least one estimation module.", color="warning")

    # Executive summary
    exec_summary = dbc.Card([
        dbc.CardBody([
            html.H5("Executive Summary"),
            html.Table([
                html.Tr([html.Td(html.Strong("Size (FPA)")), html.Td(f"{fpa_data['adjusted_fp']} Function Points" if fpa_data else "-")]),
                html.Tr([html.Td(html.Strong("Effort (COCOMO)")), html.Td(f"{cocomo_data['effort']} person-months" if cocomo_data else "-")]),
                html.Tr([html.Td(html.Strong("Duration (COCOMO)")), html.Td(f"{cocomo_data['duration']} months" if cocomo_data else "-")]),
                html.Tr([html.Td(html.Strong("Team Size (COCOMO)")), html.Td(f"~{int(round(cocomo_data['team_size']))} people" if cocomo_data else "-")]),
                html.Tr([html.Td(html.Strong("Confidence (PERT)")), html.Td(f"{pert_data['total_expected']} weeks ± {pert_data['total_sigma']} weeks" if pert_data else "-")]),
                html.Tr([html.Td(html.Strong("Total Cost")), html.Td(f"£{cost_data['total_cost']:,.0f} (incl. {cost_data['contingency_pct']}% contingency)" if cost_data else "-")]),
            ], className="table"),
            html.Hr(),
            html.P([
                html.Strong("Recommendation: "),
                f"Based on multi-method analysis, we recommend a budget of £{cost_data['total_cost']:,.0f} "
                f"with a timeline of {cocomo_data['duration']} months and a team of ~{int(round(cocomo_data['team_size']))} people."
            ]) if (cocomo_data and cost_data) else ""
        ])
    ], color="light", className="mt-3")

    return html.Div([exec_summary])


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=8050)
