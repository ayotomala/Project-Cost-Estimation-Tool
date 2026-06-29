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
        "https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="Project Cost Estimation Tool"
)
server = app.server  # Required for Render deployment

# ============================================================
# CONSTANTS — PM THEORY DATA
# ============================================================

# FPA Weight Table (Albrecht, 1979)
FPA_WEIGHTS = {
    "External Inputs": {"Simple": 3, "Average": 4, "Complex": 6},
    "External Outputs": {"Simple": 4, "Average": 5, "Complex": 7},
    "External Inquiries": {"Simple": 3, "Average": 4, "Complex": 6},
    "Internal Logical Files": {"Simple": 7, "Average": 10, "Complex": 15},
    "External Interface Files": {"Simple": 5, "Average": 7, "Complex": 10},
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

# FP to LOC conversion ratios (industry averages, LOC per FP)
FP_TO_LOC = {
    "Python": 53,
    "Java": 53,
    "JavaScript": 47,
    "C#": 54,
    "C++": 64,
    "SQL": 13,
}

# ============================================================
# LAYOUT
# ============================================================

# Navigation tabs
tabs = dbc.Tabs(
    id="main-tabs",
    active_tab="fpa",
    children=[
        dbc.Tab(label="1. FPA — Size", tab_id="fpa"),
        dbc.Tab(label="2. COCOMO — Effort", tab_id="cocomo"),
        dbc.Tab(label="3. PERT — Uncertainty", tab_id="pert"),
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
        <style>
            * { font-family: 'EB Garamond', serif !important; }
            h1, h2, h3, h4, h5, h6 { font-family: 'EB Garamond', serif !important; font-weight: 600; }
            .card-body h3 { font-size: 1.5rem; }
            .nav-link { font-family: 'EB Garamond', serif !important; font-size: 1.05rem; }
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
                type="number", value=5, min=0, max=200
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
            html.Li([html.Strong("Use case: "), "When requirements are well-defined and you need to quantify scope before development begins — enabling comparison across projects regardless of programming language."]),
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
            html.Strong("Complexity"), " is determined by the number of data fields involved and how many internal files/tables the function references:", html.Br(),
            "Simple = few fields, references 0-1 files.", html.Br(),
            "Average = moderate fields, references 2 files.", html.Br(),
            "Complex = many fields, references 3+ files."
        ], className="text-muted small mt-2"),

        # Count explanation
        html.P([
            html.Strong("Count"), " is the number of distinct instances of each function type in your system.", html.Br(),
            "Count each unique form, report, lookup, data store, or external connection separately.", html.Br(),
            "There is no maximum — larger systems simply have higher counts."
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
            "1. For each function type: ", html.Strong("Weight"), " (from the Albrecht standard weight table — see below) × ", html.Strong("Count"), " = Contribution", html.Br(),
            "2. Sum all contributions = ", html.Strong("Unadjusted Function Points (UFP)"), " — the raw size before environmental adjustment", html.Br(),
            "3. Sum all 14 GSC ratings = ", html.Strong("Value Adjustment Factor (VAF)"), " — how complex the operating environment is", html.Br(),
            "4. Final formula: ", html.Strong("Adjusted FP = UFP × (0.65 + 0.01 × VAF)"), " — the technology-independent project size"
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
                    html.Strong("Why are Internal Logical Files heaviest?"), " Because databases require design, normalisation, indexing, migration, and ongoing maintenance — significantly more effort per unit than input forms.", html.Br(),
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
                    html.Strong("Adjusted FP = 51 × (0.65 + 0.01 × 42) = 51 × 1.07 = 54.6 Function Points")
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

    vaf = sum(v for v in gsc_values if v is not None)
    adjusted_fp = round(ufp * (0.65 + 0.01 * vaf), 1)

    result_data = {"ufp": ufp, "vaf": vaf, "adjusted_fp": adjusted_fp}

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results", className="card-title"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Unadjusted Function Points (UFP)"), html.H3(str(ufp))])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Value Adjustment Factor (VAF)"), html.H3(str(vaf))])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Adjusted Function Points"), html.H3(str(adjusted_fp))])), width=4),
            ]),
            html.P(f"Formula: {ufp} × (0.65 + 0.01 × {vaf}) = {adjusted_fp}", className="mt-3 text-muted"),
            dbc.Alert(f"Your project is {adjusted_fp} Function Points. Proceed to COCOMO.", color="success")
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 2: COCOMO
# ============================================================

def render_cocomo_tab():
    return html.Div([
        html.H4("COCOMO — Constructive Cost Model"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Converts a project's estimated size into effort (person-months), duration (months), and recommended team size using empirically-derived parametric formulas."]),
            html.Li([html.Strong("Use case: "), "When you have a size estimate (from FPA or KLOC) and need to forecast how many people, how long, and how much effort the project requires — supporting staffing and budget decisions."]),
        ], className="mb-3"),

        html.H5("Step 1: Project Size"),
        dbc.Row([
            dbc.Col([
                html.Label("KLOC (thousands of lines of code)"),
                dbc.Input(id="cocomo-kloc", type="number", value=10, min=0.1, step=0.5),
                html.Small("Tip: If you completed FPA, use conversion: FP × LOC-per-FP ÷ 1000", className="text-muted")
            ], width=6),
            dbc.Col([
                html.Label("Language (for FP→KLOC conversion)"),
                dcc.Dropdown(
                    id="cocomo-language",
                    options=[{"label": f"{k} ({v} LOC/FP)", "value": k} for k, v in FP_TO_LOC.items()],
                    value="Python", clearable=False
                ),
                dbc.Button("Auto-fill from FPA", id="cocomo-autofill-btn", color="secondary", size="sm", className="mt-2")
            ], width=6),
        ]),

        html.Hr(),
        html.H5("Step 2: Project Type"),
        dcc.Dropdown(
            id="cocomo-type",
            options=[
                {"label": "Organic — Small team, familiar domain, flexible requirements", "value": "Organic"},
                {"label": "Semi-detached — Medium team, mixed experience", "value": "Semi-detached"},
                {"label": "Embedded — Tight constraints, safety-critical", "value": "Embedded"},
            ],
            value="Organic", clearable=False
        ),

        html.Hr(),
        dbc.Button("Calculate COCOMO", id="cocomo-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="cocomo-results")
    ])


@callback(
    Output("cocomo-kloc", "value"),
    Input("cocomo-autofill-btn", "n_clicks"),
    State("fpa-store", "data"),
    State("cocomo-language", "value"),
    prevent_initial_call=True
)
def autofill_kloc(n_clicks, fpa_data, language):
    if fpa_data and fpa_data.get("adjusted_fp"):
        fp = fpa_data["adjusted_fp"]
        loc_per_fp = FP_TO_LOC.get(language, 53)
        return round((fp * loc_per_fp) / 1000, 2)
    return dash.no_update


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
            html.P([
                html.Strong("Formulas:"), html.Br(),
                f"Effort = {params['a']} × ({kloc})^{params['b']} = {effort} person-months", html.Br(),
                f"Duration = {params['c']} × ({effort})^{params['d']} = {duration} months", html.Br(),
                f"Team Size = {effort} ÷ {duration} = {team_size} people"
            ], className="text-muted"),
            dbc.Alert(f"COCOMO: {effort} person-months over {duration} months. Proceed to PERT.", color="success")
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 3: PERT
# ============================================================

def render_pert_tab():
    # Default 5 tasks
    task_rows = []
    default_tasks = ["Requirements", "Design", "Development", "Testing", "Deployment"]
    for i in range(5):
        task_rows.append(dbc.Row([
            dbc.Col(dbc.Input(id={"type": "pert-name", "index": i}, value=default_tasks[i], placeholder="Task name"), width=3),
            dbc.Col(dbc.Input(id={"type": "pert-o", "index": i}, type="number", value=2, min=0.1, step=0.5, placeholder="O"), width=2),
            dbc.Col(dbc.Input(id={"type": "pert-m", "index": i}, type="number", value=4, min=0.1, step=0.5, placeholder="M"), width=2),
            dbc.Col(dbc.Input(id={"type": "pert-p", "index": i}, type="number", value=8, min=0.1, step=0.5, placeholder="P"), width=2),
            dbc.Col(html.Div(id={"type": "pert-result-cell", "index": i}), width=3),
        ], className="mb-2"))

    return html.Div([
        html.H4("PERT — Three-Point Estimation"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Quantifies estimation uncertainty by calculating a weighted average from three scenarios (Optimistic, Most Likely, Pessimistic), producing a confidence range rather than a single-point estimate."]),
            html.Li([html.Strong("Use case: "), "When project conditions are uncertain or novel, and stakeholders need to understand the range of possible outcomes — enabling risk-aware planning and contingency justification."]),
            html.Li([html.Strong("Formula: "), "Expected = (O + 4M + P) / 6  |  Standard Deviation σ = (P - O) / 6"]),
        ], className="mb-3"),

        html.H5("Enter Estimates Per Phase (in weeks)"),
        dbc.Row([
            dbc.Col(html.Strong("Task/Phase"), width=3),
            dbc.Col(html.Strong("Optimistic"), width=2),
            dbc.Col(html.Strong("Most Likely"), width=2),
            dbc.Col(html.Strong("Pessimistic"), width=2),
            dbc.Col(html.Strong("Expected (±σ)"), width=3),
        ], className="mb-2"),
        *task_rows,

        html.Hr(),
        dbc.Button("Calculate PERT", id="pert-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="pert-results")
    ])


@callback(
    Output("pert-results", "children"),
    Output("pert-store", "data"),
    Input("pert-calculate-btn", "n_clicks"),
    State({"type": "pert-name", "index": ALL}, "value"),
    State({"type": "pert-o", "index": ALL}, "value"),
    State({"type": "pert-m", "index": ALL}, "value"),
    State({"type": "pert-p", "index": ALL}, "value"),
    prevent_initial_call=True
)
def calculate_pert(n_clicks, names, o_vals, m_vals, p_vals):
    tasks = []
    for i in range(len(names)):
        name = names[i] or f"Task {i+1}"
        o = float(o_vals[i]) if o_vals[i] else 2
        m = float(m_vals[i]) if m_vals[i] else 4
        p = float(p_vals[i]) if p_vals[i] else 8
        expected = round((o + 4 * m + p) / 6, 2)
        sigma = round((p - o) / 6, 2)
        tasks.append({"name": name, "o": o, "m": m, "p": p, "expected": expected, "sigma": sigma})

    total_expected = round(sum(t["expected"] for t in tasks), 2)
    total_sigma = round(sum(t["sigma"] ** 2 for t in tasks) ** 0.5, 2)

    result_data = {"total_expected": total_expected, "total_sigma": total_sigma, "tasks": tasks}

    # Build results table
    table_rows = [html.Tr([html.Th("Task"), html.Th("O"), html.Th("M"), html.Th("P"), html.Th("Expected"), html.Th("σ")])]
    for t in tasks:
        table_rows.append(html.Tr([html.Td(t["name"]), html.Td(t["o"]), html.Td(t["m"]), html.Td(t["p"]), html.Td(t["expected"]), html.Td(f"±{t['sigma']}")]))

    conf_68_low = round(total_expected - total_sigma, 1)
    conf_68_high = round(total_expected + total_sigma, 1)
    conf_95_low = round(total_expected - 2 * total_sigma, 1)
    conf_95_high = round(total_expected + 2 * total_sigma, 1)

    results = dbc.Card([
        dbc.CardBody([
            html.H5("Results"),
            dbc.Table(table_rows, bordered=True, striped=True, size="sm"),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Expected"), html.H3(f"{total_expected} weeks")])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total σ"), html.H3(f"±{total_sigma} weeks")])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("68% Confidence"), html.H3(f"{conf_68_low}–{conf_68_high} wks")])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("95% Confidence"), html.H3(f"{conf_95_low}–{conf_95_high} wks")])), width=3),
            ]),
            dbc.Alert(f"PERT: Expected {total_expected} weeks (95% range: {conf_95_low}–{conf_95_high}). Proceed to Cost.", color="success", className="mt-3")
        ])
    ], className="mt-3")

    return results, result_data


# ============================================================
# TAB 4: COST
# ============================================================

def render_cost_tab():
    role_rows = []
    default_roles = [("Project Manager", 500, 20), ("Developer", 450, 40), ("QA Engineer", 400, 25), ("UX Designer", 400, 15)]
    for i, (role, rate, alloc) in enumerate(default_roles):
        role_rows.append(dbc.Row([
            dbc.Col(dbc.Input(id={"type": "cost-role", "index": i}, value=role), width=3),
            dbc.Col(dbc.Input(id={"type": "cost-rate", "index": i}, type="number", value=rate, min=0), width=3),
            dbc.Col(dbc.Input(id={"type": "cost-alloc", "index": i}, type="number", value=alloc, min=0, max=100), width=3),
        ], className="mb-2"))

    return html.Div([
        html.H4("Cost Calculation"),
        html.Ul([
            html.Li([html.Strong("Definition: "), "Translates effort estimates into monetary terms by factoring in team composition, role-specific daily rates, allocation percentages, and a contingency buffer for risk."]),
            html.Li([html.Strong("Use case: "), "When you need a budget figure for project approval — accounting for the reality that different roles cost differently and that all estimates carry inherent uncertainty requiring contingency."]),
        ], className="mb-3"),

        html.H5("Team Composition"),
        dbc.Row([
            dbc.Col(html.Strong("Role"), width=3),
            dbc.Col(html.Strong("Daily Rate (£)"), width=3),
            dbc.Col(html.Strong("% Allocation"), width=3),
        ], className="mb-2"),
        *role_rows,

        html.Hr(),
        html.H5("Duration & Contingency"),
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
                dcc.Slider(id="cost-contingency", min=0, max=30, step=5, value=20,
                           marks={0: "0%", 10: "10%", 20: "20%", 30: "30%"})
            ], width=4),
        ]),

        html.Hr(),
        dbc.Button("Calculate Cost", id="cost-calculate-btn", color="primary", className="mb-3"),
        html.Div(id="cost-results")
    ])


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
    prevent_initial_call=True
)
def calculate_cost(n_clicks, roles, rates, allocs, duration, days_per_month, contingency_pct):
    total_days = (duration or 6) * (days_per_month or 22)
    base_cost = 0
    breakdown = []

    for i in range(len(roles)):
        role = roles[i] or f"Role {i+1}"
        rate = float(rates[i]) if rates[i] else 0
        alloc = float(allocs[i]) if allocs[i] else 0
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
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Estimated Cost"), html.H3(f"£{total_cost:,.0f}")])), width=4),
            ]),
            dbc.Alert([
                html.Strong(f"Why {contingency_pct}% contingency? "),
                "Projects without contingency are guaranteed to overrun (QuickShop case study, Week 5). ",
                f"A {contingency_pct}% buffer accounts for estimation uncertainty and unforeseen challenges."
            ], color="warning", className="mt-3"),
            dbc.Alert(f"Total: £{total_cost:,.0f}. Proceed to Summary.", color="success")
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

    comparison_table = dbc.Table(
        [html.Tr([html.Th("Method"), html.Th("Key Output"), html.Th("Question Answered"), html.Th("Best For")])] + rows,
        bordered=True, striped=True
    )

    # Executive summary
    exec_summary = []
    if fpa_data and cocomo_data and cost_data:
        exec_summary = dbc.Card([
            dbc.CardBody([
                html.H5("Executive Summary"),
                html.Table([
                    html.Tr([html.Td(html.Strong("Size")), html.Td(f"{fpa_data['adjusted_fp']} Function Points")]),
                    html.Tr([html.Td(html.Strong("Effort")), html.Td(f"{cocomo_data['effort']} person-months")]),
                    html.Tr([html.Td(html.Strong("Duration")), html.Td(f"{cocomo_data['duration']} months")]),
                    html.Tr([html.Td(html.Strong("Team Size")), html.Td(f"~{cocomo_data['team_size']} people")]),
                    html.Tr([html.Td(html.Strong("Total Cost")), html.Td(f"£{cost_data['total_cost']:,.0f}")]),
                    html.Tr([html.Td(html.Strong("Confidence")), html.Td(f"±{pert_data['total_sigma']} weeks" if pert_data else "Complete PERT for range")]),
                ], className="table"),
                html.Hr(),
                html.P([
                    html.Strong("Recommendation: "),
                    f"Based on multi-method analysis, we recommend a budget of £{cost_data['total_cost']:,.0f} ",
                    f"with a timeline of {cocomo_data['duration']} months and a team of ~{cocomo_data['team_size']} people."
                ])
            ])
        ], color="light", className="mt-3")

    method_guide = dbc.Card([
        dbc.CardBody([
                html.H5("Method Selection Guide"),
            dbc.Table([
                html.Tr([html.Th("Scenario"), html.Th("Method"), html.Th("Why")]),
                html.Tr([html.Td("Requirements well-defined"), html.Td("FPA"), html.Td("Technology-independent sizing")]),
                html.Tr([html.Td("Need staffing/timeline"), html.Td("COCOMO"), html.Td("Converts size to effort")]),
                html.Tr([html.Td("High uncertainty"), html.Td("PERT"), html.Td("Provides confidence range")]),
                html.Tr([html.Td("Budget approval"), html.Td("Cost Model"), html.Td("Monetary terms + contingency")]),
                html.Tr([html.Td(html.Strong("Complete picture")), html.Td(html.Strong("All four")), html.Td(html.Strong("Each answers a different question"))]),
            ], bordered=True, size="sm")
        ])
    ], className="mt-3")

    return html.Div([
        html.H5("Side-by-Side Comparison"),
        comparison_table,
        exec_summary if exec_summary else "",
        method_guide
    ])


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=8050)
