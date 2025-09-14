# dashboard_app.py
# Requisitos: pip install dash pandas plotly dash-bootstrap-components openpyxl
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import base64
import io

# ------------------ Layout inicial ------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="Dashboard KPI - Gestión de Mantenimiento")

# Inicializar dataframe vacío
df = pd.DataFrame()

app.layout = dbc.Container([
    # Título - Centrado
    dbc.Row([
        dbc.Col(html.H1("📊 Dashboard KPI de Gestión de Mantenimiento",
                        className="text-center my-2",
                        style={"fontSize": "2.2rem", "fontWeight": "bold", "color": "#FFFFFF"}))
    ]),
    
    dbc.Row([
        dbc.Col(html.P("Monitoreo de indicadores clave de mantenimiento", 
                       className="text-center text-light mb-3",
                       style={"fontSize": "0.9rem"}))
    ]),

    # Panel de carga de archivos y filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Cargar Datos y Configurar Filtros", 
                              className="bg-primary text-white py-2",
                              style={"fontSize": "1rem"}),
                dbc.CardBody([
                    dbc.Row([
                        # Upload component
                        dbc.Col([
                            html.Label("Cargar archivo Excel", className="text-light mb-1", style={"fontSize": "0.9rem"}),
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Arrastra o ',
                                    html.A('selecciona un archivo', style={"color": "#1E90FF"})
                                ], style={"fontSize": "0.9rem"}),
                                style={
                                    'width': '100%',
                                    'height': '50px',
                                    'lineHeight': '50px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '5px 0'
                                },
                                multiple=False
                            ),
                            html.Div(id='output-data-upload', className="text-light mt-1", style={"fontSize": "0.8rem"}),
                        ], width=4),
                        
                        # Filtro de fechas
                        dbc.Col([
                            html.Label("Rango de Fechas", className="text-light mb-1", style={"fontSize": "0.9rem"}),
                            dcc.DatePickerRange(
                                id="date-range",
                                start_date_placeholder_text="Fecha inicio",
                                end_date_placeholder_text="Fecha fin",
                                display_format="YYYY-MM-DD",
                                className="mb-1 w-100",
                                style={"color": "#000000", "fontSize": "0.9rem"}
                            )
                        ], width=4),
                        
                        # Filtro de ámbito (con texto negro)
                        dbc.Col([
                            html.Label("Ámbito de Análisis", className="text-light mb-1", style={"fontSize": "0.9rem"}),
                            dcc.Dropdown(
                                id="scope-dropdown",
                                options=[],
                                placeholder="Selecciona un ámbito...",
                                className="mb-1",
                                style={'color': 'black', 'fontSize': '0.9rem'}  # Texto negro en el dropdown
                            )
                        ], width=4),
                    ], align="center")
                ], className="py-2")
            ], className="mb-3")
        ])
    ]),

    # Tarjetas KPI - Más compactas
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div("📈", style={"fontSize": "1.5rem", "marginRight": "8px"}),
                    html.Div([
                        html.H4("Disponibilidad", className="card-title mb-1", style={"fontSize": "0.9rem"}),
                        html.H3(id="kpi-availability", className="card-text mb-0", children="N/A", style={"fontSize": "1.1rem"})
                    ])
                ], className="d-flex align-items-center")
            ], className="py-2")
        ], color="success", outline=True, className="text-center m-1"), width=3, lg=3, md=6, sm=6),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div("⏱️", style={"fontSize": "1.5rem", "marginRight": "8px"}),
                    html.Div([
                        html.H4("MTBF (hrs)", className="card-title mb-1", style={"fontSize": "0.9rem"}),
                        html.H3(id="kpi-mtbf", className="card-text mb-0", children="N/A", style={"fontSize": "1.1rem"})
                    ])
                ], className="d-flex align-items-center")
            ], className="py-2")
        ], color="info", outline=True, className="text-center m-1"), width=3, lg=3, md=6, sm=6),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div("🔧", style={"fontSize": "1.5rem", "marginRight": "8px"}),
                    html.Div([
                        html.H4("MTTR (hrs)", className="card-title mb-1", style={"fontSize": "0.9rem"}),
                        html.H3(id="kpi-mttr", className="card-text mb-0", children="N/A", style={"fontSize": "1.1rem"})
                    ])
                ], className="d-flex align-items-center")
            ], className="py-2")
        ], color="warning", outline=True, className="text-center m-1"), width=3, lg=3, md=6, sm=6),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Div("📋", style={"fontSize": "1.5rem", "marginRight": "8px"}),
                    html.Div([
                        html.H4("Intervenciones", className="card-title mb-1", style={"fontSize": "0.9rem"}),
                        html.H3(id="kpi-interventions", className="card-text mb-0", children="N/A", style={"fontSize": "1.1rem"})
                    ])
                ], className="d-flex align-items-center")
            ], className="py-2")
        ], color="primary", outline=True, className="text-center m-1"), width=3, lg=3, md=6, sm=6),
    ], justify="center", className="mb-3", id="kpi-cards", style={"display": "none"}),

    # Fila 1 de gráficos - Más compactos
    dbc.Row([
        dbc.Col(dcc.Graph(id="chart-availability", config={"displayModeBar": False}, 
                         style={"height": "300px"}), width=6, lg=6, md=12, sm=12),
        dbc.Col(dcc.Graph(id="chart-maint-pie", config={"displayModeBar": False}, 
                         style={"height": "300px"}), width=6, lg=6, md=12, sm=12),
    ], className="mb-3", id="graph-row-1", style={"display": "none"}),

    # Fila 2 de gráficos - Más compactos
    dbc.Row([
        dbc.Col(dcc.Graph(id="chart-mtbf", config={"displayModeBar": False}, 
                         style={"height": "300px"}), width=6, lg=6, md=12, sm=12),
        dbc.Col(dcc.Graph(id="chart-mttr", config={"displayModeBar": False}, 
                         style={"height": "300px"}), width=6, lg=6, md=12, sm=12),
    ], className="mb-3", id="graph-row-2", style={"display": "none"}),
    
    # Información adicional - Más compacta
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("ℹ️ Información del Dashboard", className="py-2", style={"fontSize": "1rem"}),
                dbc.CardBody([
                    html.P("Este dashboard muestra los principales KPIs de mantenimiento:", 
                           className="mb-2", style={"fontSize": "0.9rem"}),
                    html.Ul([
                        html.Li("Disponibilidad: Porcentaje de tiempo que los equipos están operativos", 
                                style={"fontSize": "0.9rem"}),
                        html.Li("MTBF: Tiempo Medio Entre Fallas (Mean Time Between Failures)", 
                                style={"fontSize": "0.9rem"}),
                        html.Li("MTTR: Tiempo Medio de Reparación (Mean Time To Repair)", 
                                style={"fontSize": "0.9rem"}),
                    ], className="mb-2"),
                    html.P("Carga un archivo Excel con los datos de mantenimiento para comenzar el análisis.", 
                          className="text-muted mt-1", style={"fontSize": "0.8rem"})
                ], className="py-2")
            ], className="mt-3")
        ], width=12)
    ], id="info-row", style={"display": "none"}),
    
    # Footer con información del autor (parte inferior derecha)
    dbc.Row([
        dbc.Col([
            html.Div(
                html.P([
                    "Desarrollado por: ",
                    html.A("Pablo Gómez", href="https://www.linkedin.com/in/pablo-g%C3%B3mez-69274b125/", 
                           target="_blank", style={"color": "#FFFFFF", "textDecoration": "underline", "fontSize": "1xp"})
                ], style={"textAlign": "center", "color": "#FFFFFF", "marginTop": "15px", "marginBottom": "5px"})
            )
        ], width=12)
    ])
], fluid=True, style={"backgroundColor": "#1a1a1a", "minHeight": "100vh", "overflow": "hidden", "padding": "10px"})


# ------------------ Funciones de procesamiento ------------------
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'xlsx' in filename:
            # Leer el archivo Excel
            df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
            
            # Procesar los datos (asumiendo la misma estructura que el ejemplo)
            if "start_datetime" in df.columns:
                df["start_datetime"] = pd.to_datetime(df["start_datetime"])
            if "end_datetime" in df.columns:
                df["end_datetime"] = pd.to_datetime(df["end_datetime"])
            if "duration_minutes" in df.columns:
                df["duration_hours"] = df["duration_minutes"] / 60.0
                
            return df, f"Archivo '{filename}' cargado correctamente."
        else:
            return None, "Formato no compatible. Por favor, sube un archivo Excel (.xlsx)."
    except Exception as e:
        print(e)
        return None, f"Error al procesar el archivo: {str(e)}"


def filter_df(dff, start_date, end_date, scope_value):
    if dff is None or dff.empty:
        return pd.DataFrame()
    
    dff_filtered = dff.copy()
    if start_date:
        dff_filtered = dff_filtered[dff_filtered["start_datetime"].dt.date >= pd.to_datetime(start_date).date()]
    if end_date:
        dff_filtered = dff_filtered[dff_filtered["end_datetime"].dt.date <= pd.to_datetime(end_date).date()]
    if scope_value and scope_value != "ALL":
        if scope_value.startswith("AREA__"):
            area = scope_value.split("AREA__")[1]
            dff_filtered = dff_filtered[dff_filtered["area"] == area]
        elif scope_value.startswith("EQUIP__"):
            equip = scope_value.split("EQUIP__")[1]
            dff_filtered = dff_filtered[dff_filtered["equipment"] == equip]
    return dff_filtered


# ------------------ Callbacks ------------------
@app.callback(
    Output('output-data-upload', 'children'),
    Output('date-range', 'start_date'),
    Output('date-range', 'end_date'),
    Output('scope-dropdown', 'options'),
    Output('scope-dropdown', 'value'),
    Output('kpi-cards', 'style'),
    Output('graph-row-1', 'style'),
    Output('graph-row-2', 'style'),
    Output('info-row', 'style'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data(contents, filename):
    if contents is None:
        return ("Por favor, carga un archivo Excel con datos de mantenimiento.", 
                None, None, [], "ALL", 
                {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"})
    
    df_parsed, message = parse_contents(contents, filename)
    
    if df_parsed is None:
        return (message, None, None, [], "ALL", 
                {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"})
    
    # Actualizar opciones del dropdown de ámbito
    scope_options = [{"label": "Toda la Planta", "value": "ALL"}]
    if "area" in df_parsed.columns:
        for a in sorted(df_parsed["area"].unique()):
            scope_options.append({"label": f"Área: {a}", "value": f"AREA__{a}"})
    if "equipment" in df_parsed.columns:
        for e in sorted(df_parsed["equipment"].unique()):
            scope_options.append({"label": f"Equipo: {e}", "value": f"EQUIP__{e}"})
    
    # Obtener fechas mínimas y máximas
    min_date = df_parsed["start_datetime"].min().date() if "start_datetime" in df_parsed.columns else None
    max_date = df_parsed["end_datetime"].max().date() if "end_datetime" in df_parsed.columns else None
    
    return (message, min_date, max_date, scope_options, "ALL", 
            {"display": "flex"}, {"display": "flex"}, {"display": "flex"}, {"display": "block"})


@app.callback(
    Output("kpi-availability", "children"),
    Output("kpi-mtbf", "children"),
    Output("kpi-mttr", "children"),
    Output("kpi-interventions", "children"),
    Output("chart-availability", "figure"),
    Output("chart-maint-pie", "figure"),
    Output("chart-mtbf", "figure"),
    Output("chart-mttr", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("scope-dropdown", "value"),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_dashboard(start_date, end_date, scope_value, contents, filename):
    # Verificar si hay datos cargados
    if contents is None:
        return "N/A", "N/A", "N/A", "N/A", {}, {}, {}, {}
    
    # Obtener los datos del archivo cargado
    df_parsed, _ = parse_contents(contents, filename)
    if df_parsed is None:
        return "N/A", "N/A", "N/A", "N/A", {}, {}, {}, {}
    
    # Filtrar datos
    dff = filter_df(df_parsed, start_date, end_date, scope_value)
    
    if dff.empty:
        return "N/A", "N/A", "N/A", "N/A", {}, {}, {}, {}
    
    # Calcular número total de intervenciones
    total_interventions = dff.shape[0]
    
    # Cálculos existentes
    total_period_hours = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days * 24
    if total_period_hours <= 0:
        total_period_hours = (dff["end_datetime"].max() - dff["start_datetime"].min()).total_seconds() / 3600

    total_downtime_hours = dff["duration_hours"].sum()
    availability = 1 - (total_downtime_hours / total_period_hours) if total_period_hours > 0 else np.nan
    availability_pct = f"{availability*100:.2f}%" if not pd.isna(availability) else "N/A"

    mttr = dff[dff["is_failure"]]["duration_hours"].mean() if "is_failure" in dff.columns else np.nan
    mttr_val = f"{mttr:.2f}" if not pd.isna(mttr) else "N/A"

    failures = dff[dff["is_failure"]].shape[0] if "is_failure" in dff.columns else 0
    equip_count = dff["equipment"].nunique() if dff.shape[0] > 0 else 1
    mtbf = (total_period_hours * equip_count) / failures if failures > 0 else np.nan
    mtbf_val = f"{mtbf:.2f}" if not pd.isna(mtbf) else "N/A"

    # ---- 📊 Gráfico de Disponibilidad Mensual ----
    dff["month"] = dff["start_datetime"].dt.to_period("M").dt.to_timestamp()
    monthly = dff.groupby("month").agg({"duration_hours": "sum"}).reset_index()
    monthly["hours_in_month"] = monthly["month"].dt.days_in_month * 24
    monthly["availability"] = 1 - (monthly["duration_hours"] / monthly["hours_in_month"])

    availability_fig = px.bar(monthly, x="month", y="availability",
                              labels={"availability": "Disponibilidad", "month": "Mes"},
                              text=monthly["availability"].apply(lambda x: f"{x*100:.1f}%"),
                              title="Disponibilidad Mensual",
                              color_discrete_sequence=['#2ECC71'])
    availability_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_x=0.5,
        title_font_size=16,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    availability_fig.update_traces(textposition="outside")
    availability_fig.update_yaxes(tickformat=".0%", range=[0, 1])
    availability_fig.update_xaxes(tickangle=45)

    # ---- 📊 Gráfico circular (colores fijos) ----
    if "maintenance_type" in dff.columns:
        dff_pie = dff[dff["maintenance_type"].isin(["Correctivo", "Preventivo", "Predictivo"])]
        pie_colors = {"Correctivo": "#E74C3C", "Preventivo": "#3498DB", "Predictivo": "#2ECC71"}
        pie = px.pie(dff_pie, names="maintenance_type", hole=0.4,
                     color="maintenance_type", color_discrete_map=pie_colors,
                     title="Distribución por Tipo de Mantenimiento")
    else:
        # Crear un gráfico vacío si no hay datos
        pie = px.pie(title="Distribución por Tipo de Mantenimiento (Datos no disponibles)")
    
    pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_x=0.5,
        title_font_size=16,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # ---- 📊 Gráfico de línea MTBF ----
    if "is_failure" in dff.columns:
        fails_month = dff[dff["is_failure"]].groupby("month").size().reset_index(name="failures")
        fails_month["hours_in_month"] = fails_month["month"].dt.days_in_month * 24
        fails_month["MTBF"] = (fails_month["hours_in_month"] * equip_count) / fails_month["failures"].replace(0, np.nan)
        mtbf_fig = px.line(fails_month, x="month", y="MTBF", markers=True, 
                           title="Tendencia MTBF (hrs)", color_discrete_sequence=['#3498DB'])
    else:
        # Crear un gráfico vacío si no hay datos
        mtbf_fig = px.line(title="Tendencia MTBF (hrs) (Datos no disponibles)")
    
    mtbf_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_x=0.5,
        title_font_size=16,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    mtbf_fig.update_xaxes(tickangle=45)

    # ---- 📊 Gráfico de línea MTTR ----
    if "is_failure" in dff.columns:
        mttr_month = dff[dff["is_failure"]].groupby("month")["duration_hours"].mean().reset_index()
        mttr_fig = px.line(mttr_month, x="month", y="duration_hours", markers=True, 
                           title="Tendencia MTTR (hrs)", color_discrete_sequence=['#F39C12'])
    else:
        # Crear un gráfico vacío si no hay datos
        mttr_fig = px.line(title="Tendencia MTTR (hrs) (Datos no disponibles)")
    
    mttr_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_x=0.5,
        title_font_size=16,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    mttr_fig.update_xaxes(tickangle=45)
    
    return availability_pct, mtbf_val, mttr_val, total_interventions, availability_fig, pie, mtbf_fig, mttr_fig

if __name__ == "__main__":
    app.run(debug=True)
