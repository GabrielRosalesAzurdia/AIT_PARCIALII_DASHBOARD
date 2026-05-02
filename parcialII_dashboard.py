import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Videojuegos — Panel PS, S.A", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F4F6FB; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem !important; max-width: 1500px; }

.header-banner {
    background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
    border-radius: 16px; padding: 1.8rem 2.5rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1.5rem;
}
.header-title { color:#fff; font-size:1.8rem; font-weight:700; margin:0; letter-spacing:-0.5px; }
.header-sub   { color:#94A3B8; font-size:0.9rem; margin:0.3rem 0 0 0; }
.header-badge {
    background: rgba(255,255,255,0.12); color:white; border: 1px solid rgba(255,255,255,0.2);
    padding:0.4rem 1.1rem; border-radius:20px; font-size:0.78rem;
    font-weight:600; letter-spacing:0.6px; margin-left:auto; white-space:nowrap;
}

.kpi-card {
    background:white; border-radius:14px; padding:1.2rem 1.4rem;
    box-shadow:0 2px 10px rgba(0,0,0,0.06); border-top:4px solid;
    height: 120px;
}
.kpi-label { font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; color:#6B7280; margin-bottom:0.5rem; }
.kpi-value { font-size:1.6rem; font-weight:700; line-height:1.1; color:#111827; }
.kpi-sub   { font-size:0.75rem; color:#9CA3AF; margin-top:0.25rem; }

.sec-title {
    font-size:1rem; font-weight:700; color:#111827; letter-spacing:0.2px;
    margin:1.8rem 0 0.8rem 0; padding-bottom:0.4rem;
    border-bottom: 2px solid #3B82F6;
    display: inline-block;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stMultiSelect"] label {
    color: #111827 !important; font-weight: 500;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] span { color: #111827 !important; }
div[data-testid="stSlider"] p { color: #111827 !important; }

#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ── DATOS ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    df = pd.read_excel("PS_S-A.xlsx", sheet_name="Ventas Videojuegos")
    df = df.dropna(subset=["Ventas Global"])
    df["Plataforma"] = df["Plataforma"].astype(str)
    df = df[df["Año"].notna()]
    df["Año"] = df["Año"].astype(int)
    return df

df_raw = cargar()


# ── LAYOUT BASE GRÁFICOS ──────────────────────────────────────────────────────
NEGRO = "#111827"
GRID  = "#F3F4F6"
LINE  = "#E5E7EB"

def eje(title="", size=11, **kw):
    return dict(title=dict(text=title, font=dict(size=12, color=NEGRO)),
                gridcolor=GRID, linecolor=LINE,
                tickfont=dict(size=size, color=NEGRO), **kw)

def blayout(title, height, extra=None):
    cfg = dict(
        title=dict(text=title, font=dict(size=14, color=NEGRO, family="Inter"), x=0.02),
        font=dict(family="Inter", size=12, color=NEGRO),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(t=50, b=35, l=15, r=15), height=height,
    )
    if extra:
        cfg.update(extra)
    return cfg

ESC_AZUL  = [[0,"#DBEAFE"],[0.5,"#3B82F6"],[1,"#1E3A8A"]]
ESC_VERDE = [[0,"#D1FAE5"],[0.5,"#10B981"],[1,"#065F46"]]
ESC_PURP  = [[0,"#EDE9FF"],[0.5,"#8B5CF6"],[1,"#3B0764"]]
ESC_AMBER = [[0,"#FEF3C7"],[0.5,"#F59E0B"],[1,"#78350F"]]
COLORES_REG = ["#3B82F6","#10B981","#F59E0B","#EF4444"]


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div>
    <p class="header-title">Panel Comercial — PS, S.A</p>
    <p class="header-sub">Rendimiento histórico de ventas por título, región, plataforma, género y editorial</p>
  </div>
  <div class="header-badge">ANÁLISIS DE VENTAS GLOBALES</div>
</div>
""", unsafe_allow_html=True)


# ── FILTROS ───────────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
with f1:
    generos = ["Todos"] + sorted(df_raw["Genero"].dropna().unique().tolist())
    gen_sel = st.selectbox("Género", generos)
with f2:
    plats = ["Todas"] + sorted(df_raw["Plataforma"].dropna().unique().tolist())
    plat_sel = st.selectbox("Plataforma", plats)
with f3:
    top_eds = df_raw.groupby("Editorial")["Ventas Global"].sum().nlargest(20).index.tolist()
    eds = ["Todas"] + top_eds
    ed_sel = st.selectbox("Editorial (Top 20)", eds)
with f4:
    año_min, año_max = int(df_raw["Año"].min()), int(df_raw["Año"].max())
    rango = st.slider("Período", año_min, año_max, (1995, año_max))

df = df_raw.copy()
if gen_sel  != "Todos":  df = df[df["Genero"]    == gen_sel]
if plat_sel != "Todas":  df = df[df["Plataforma"] == plat_sel]
if ed_sel   != "Todas":  df = df[df["Editorial"]  == ed_sel]
df = df[df["Año"].between(rango[0], rango[1])]


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<span class="sec-title">Indicadores Generales</span>', unsafe_allow_html=True)

ventas_tot   = df["Ventas Global"].sum()
n_titulos    = df["Nombre"].nunique()
juego_top    = df.groupby("Nombre")["Ventas Global"].sum().idxmax() if len(df) > 0 else "—"
plat_top     = df.groupby("Plataforma")["Ventas Global"].sum().idxmax() if len(df) > 0 else "—"
ed_top       = df.groupby("Editorial")["Ventas Global"].sum().idxmax() if len(df) > 0 else "—"
prom_vtas    = df["Ventas Global"].mean()
año_top      = df.groupby("Año")["Ventas Global"].sum().idxmax() if len(df) > 0 else "—"
tasa_jp      = (df["Ventas JP"].sum() / df["Ventas Global"].sum() * 100) if len(df) > 0 else 0

kpis = [
    ("Ventas Globales Totales", f"{ventas_tot:,.2f}M USD", "millones de dólares",     "#3B82F6"),
    ("Títulos Analizados",      f"{n_titulos:,}",          "juegos únicos",            "#10B981"),
    ("Juego Más Vendido",       juego_top[:22]+"…" if len(str(juego_top))>22 else juego_top,
                                                            "mayor volumen acumulado",  "#8B5CF6"),
    ("Plataforma Líder",        plat_top,                  "mayor volumen de ventas",  "#F59E0B"),
    ("Editorial Dominante",     ed_top[:18]+"…" if len(str(ed_top))>18 else ed_top,
                                                            "mayor volumen acumulado",  "#EF4444"),
    ("Promedio por Juego",      f"{prom_vtas:.2f}M USD",   "ventas promedio",          "#06B6D4"),
    ("Año Pico de Ventas",      str(año_top),              "mayor volumen anual",      "#F97316"),
    ("Participación Japón",     f"{tasa_jp:.1f}%",         "del total global",         "#6366F1"),
]

cols = st.columns(4)
for i, (label, val, sub, color) in enumerate(kpis):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color:{color}; margin-bottom:0.8rem">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)


# ── VENTAS POR AÑO ────────────────────────────────────────────────────────────
st.markdown('<span class="sec-title">Evolución de Ventas por Año</span>', unsafe_allow_html=True)

por_año = df.groupby("Año")[["Ventas NA","Ventas EU","Ventas JP","Ventas Otros"]].sum().reset_index()
fig = go.Figure()
regiones = ["Ventas NA","Ventas EU","Ventas JP","Ventas Otros"]
nombres  = ["Norteamérica","Europa","Japón","Otros"]
for reg, nom, color in zip(regiones, nombres, COLORES_REG):
    fig.add_trace(go.Scatter(
        x=por_año["Año"], y=por_año[reg], name=nom, mode="lines",
        line=dict(width=2, color=color), stackgroup="one",
        hovertemplate=f"<b>{nom}</b><br>%{{y:.2f}}M<extra></extra>"
    ))
fig.update_layout(**blayout("Ventas acumuladas por región y año (millones USD)", 380, {
    "xaxis": eje("Año"),
    "yaxis": eje("Ventas (M USD)"),
    "hovermode": "x unified",
    "legend": dict(orientation="h", y=1.08, x=0.02, font=dict(color=NEGRO, size=11))
}))
st.plotly_chart(fig, use_container_width=True)


# ── FILA: VENTAS POR REGIÓN + GÉNERO ──────────────────────────────────────────
st.markdown('<span class="sec-title">Ventas por Región y por Género</span>', unsafe_allow_html=True)
rc1, rc2 = st.columns(2)

with rc1:
    reg_totales = {
        "Norteamérica": df["Ventas NA"].sum(),
        "Europa":       df["Ventas EU"].sum(),
        "Japón":        df["Ventas JP"].sum(),
        "Otros":        df["Ventas Otros"].sum(),
    }
    fig = go.Figure(go.Pie(
        labels=list(reg_totales.keys()),
        values=list(reg_totales.values()),
        hole=0.52,
        marker=dict(colors=COLORES_REG, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color=NEGRO),
        hovertemplate="<b>%{label}</b><br>%{value:.2f}M USD<br>%{percent}<extra></extra>"
    ))
    fig.add_annotation(text=f"<b>{sum(reg_totales.values()):.0f}M</b><br>total",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=NEGRO))
    fig.update_layout(**blayout("Distribución de ventas por región", 340, {
        "legend": dict(orientation="h", y=-0.08, x=0.1, font=dict(color=NEGRO, size=11))
    }))
    st.plotly_chart(fig, use_container_width=True)

with rc2:
    por_gen = df.groupby("Genero")["Ventas Global"].sum().sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=por_gen.values, y=por_gen.index, orientation="h",
        marker=dict(color=por_gen.values, colorscale=ESC_PURP, showscale=False,
                    line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}M USD<extra></extra>"
    ))
    fig.update_layout(**blayout("Ventas totales por género (M USD)", 340, {
        "xaxis": eje("Ventas (M USD)"),
        "yaxis": eje(size=11),
    }))
    st.plotly_chart(fig, use_container_width=True)


# ── FILA: TOP PLATAFORMAS + TOP EDITORIALES ───────────────────────────────────
st.markdown('<span class="sec-title">Plataformas y Editoriales</span>', unsafe_allow_html=True)
pc1, pc2 = st.columns(2)

with pc1:
    top_plat = df.groupby("Plataforma")["Ventas Global"].sum().nlargest(12).sort_values()
    fig = go.Figure(go.Bar(
        x=top_plat.values, y=top_plat.index, orientation="h",
        marker=dict(color=top_plat.values, colorscale=ESC_AZUL, showscale=False,
                    line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}M USD<extra></extra>"
    ))
    fig.update_layout(**blayout("Top 12 Plataformas por ventas globales", 400, {
        "xaxis": eje("Ventas (M USD)"),
        "yaxis": eje(size=11),
    }))
    st.plotly_chart(fig, use_container_width=True)

with pc2:
    top_ed = df.groupby("Editorial")["Ventas Global"].sum().nlargest(12).sort_values()
    fig = go.Figure(go.Bar(
        x=top_ed.values, y=top_ed.index, orientation="h",
        marker=dict(color=top_ed.values, colorscale=ESC_VERDE, showscale=False,
                    line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}M USD<extra></extra>"
    ))
    fig.update_layout(**blayout("Top 12 Editoriales por ventas globales", 400, {
        "xaxis": eje("Ventas (M USD)"),
        "yaxis": eje(size=11),
    }))
    st.plotly_chart(fig, use_container_width=True)


# ── TOP 15 JUEGOS ─────────────────────────────────────────────────────────────
st.markdown('<span class="sec-title">Top 15 Juegos Más Vendidos</span>', unsafe_allow_html=True)

top_juegos = df.groupby("Nombre")["Ventas Global"].sum().nlargest(15).sort_values()
fig = go.Figure(go.Bar(
    x=top_juegos.values, y=top_juegos.index, orientation="h",
    marker=dict(color=top_juegos.values, colorscale=ESC_AMBER, showscale=False,
                line=dict(color="rgba(0,0,0,0)")),
    hovertemplate="<b>%{y}</b><br>%{x:.2f}M USD<extra></extra>"
))
fig.update_layout(**blayout("Top 15 títulos con mayor volumen de ventas globales (M USD)", 480, {
    "xaxis": eje("Ventas globales (M USD)"),
    "yaxis": eje(size=11),
}))
st.plotly_chart(fig, use_container_width=True)


# ── JAPÓN vs GLOBAL ───────────────────────────────────────────────────────────
st.markdown('<span class="sec-title">Japón vs Resto del Mundo — Comparativa por Año</span>', unsafe_allow_html=True)

jp_año = df.groupby("Año").agg(JP=("Ventas JP","sum"), Global=("Ventas Global","sum")).reset_index()
jp_año["Resto"] = jp_año["Global"] - jp_año["JP"]
jp_año["Tasa JP (%)"] = (jp_año["JP"] / jp_año["Global"] * 100).round(2)

fig = go.Figure()
fig.add_trace(go.Bar(x=jp_año["Año"], y=jp_año["JP"], name="Japón",
    marker_color="#6366F1",
    hovertemplate="<b>%{x}</b><br>JP: %{y:.2f}M<extra></extra>"))
fig.add_trace(go.Bar(x=jp_año["Año"], y=jp_año["Resto"], name="Resto del mundo",
    marker_color="#D1D5DB",
    hovertemplate="<b>%{x}</b><br>Resto: %{y:.2f}M<extra></extra>"))
fig.add_trace(go.Scatter(x=jp_año["Año"], y=jp_año["Tasa JP (%)"], name="% Japón",
    yaxis="y2", mode="lines+markers",
    line=dict(color="#EF4444", width=2), marker=dict(size=4),
    hovertemplate="%{y:.1f}%<extra></extra>"))
fig.update_layout(**blayout("Ventas Japón vs resto del mundo (barras apiladas) · % participación JP (línea roja)", 400, {
    "xaxis":  eje("Año"),
    "yaxis":  eje("Ventas (M USD)"),
    "yaxis2": dict(title=dict(text="% Japón", font=dict(size=12, color="#EF4444")),
                   overlaying="y", side="right", showgrid=False,
                   tickfont=dict(size=11, color="#EF4444"), ticksuffix="%"),
    "barmode": "stack",
    "hovermode": "x unified",
    "legend": dict(orientation="h", y=1.08, x=0.02, font=dict(color=NEGRO, size=11))
}))
st.plotly_chart(fig, use_container_width=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;color:#9CA3AF;font-size:0.78rem">
    Panel Comercial de Videojuegos &nbsp;·&nbsp; Datos históricos de ventas globales &nbsp;·&nbsp; Streamlit & Plotly
</div>
""", unsafe_allow_html=True)