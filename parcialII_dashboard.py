import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="HR Analytics", layout="wide", page_icon="👥")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F0F2F8; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem !important; max-width: 1400px; }
.header-banner {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1.5rem;
}
.header-title { color:#fff; font-size:2rem; font-weight:700; margin:0; letter-spacing:-0.5px; }
.header-sub   { color:#A0AEC0; font-size:0.95rem; margin:0.25rem 0 0 0; }
.header-badge {
    background: linear-gradient(135deg, #E94560, #C62A47); color:white;
    padding:0.4rem 1rem; border-radius:20px; font-size:0.8rem;
    font-weight:600; letter-spacing:0.5px; margin-left:auto;
}
.kpi-card {
    background:white; border-radius:14px; padding:1.4rem 1.6rem;
    box-shadow:0 2px 12px rgba(0,0,0,0.07); border-left:5px solid;
}
.kpi-label { font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; color:#718096; margin-bottom:0.4rem; }
.kpi-value { font-size:2.1rem; font-weight:700; line-height:1; }
.kpi-icon  { font-size:1.6rem; margin-bottom:0.6rem; }
.sec-title {
    font-size:1.1rem; font-weight:700; color:#1A202C;
    margin:1.8rem 0 0.8rem 0;
    border-bottom: 2px solid #E94560;
    padding-bottom: 0.4rem;
}
#MainMenu, footer, header { visibility:hidden; }
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label {
    color: #1A202C !important;
    font-weight: 500;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #1A202C !important;
}
div[data-testid="stSlider"] p {
    color: #1A202C !important;
}
</style>
""", unsafe_allow_html=True)


# ── DATOS ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar():
    p = "Tabla_dataset_RRHH.xlsx"
    df = pd.read_excel(p, sheet_name="Hoja1")
    return df

df = cargar()

# Renombrar columnas para facilitar manejo
df = df.rename(columns={
    "ID Empleado": "id_empleado",
    "Función": "funcion",
    "Departamento": "departamento",
    "Región": "region",
    "Educación": "educacion",
    "Género": "genero",
    "Jornada": "jornada",
    "Modalidad": "modalidad",
    "Fecha Contratación": "fecha_contratacion",
    "Estatus": "estatus",
    "Fecha Baja": "fecha_baja"
})

# Extraer año de contratación
df["año_contratacion"] = pd.to_datetime(df["fecha_contratacion"]).dt.year
df = df[df["año_contratacion"].notna() & df["año_contratacion"].between(2000, 2026)]
df["año_contratacion"] = df["año_contratacion"].astype(int)

# Limpiar valores nulos en columnas clave
df["departamento"] = df["departamento"].fillna("Sin departamento")
df["region"] = df["region"].fillna("Sin región")
df["educacion"] = df["educacion"].fillna("No especificado")
df["genero"] = df["genero"].fillna("No especificado")

# ── CONFIGURACIÓN BASE DE GRÁFICOS ────────────────────────────────────────────
NEGRO       = "#1A202C"
GRIS_TEXTO  = "#374151"
GRID_COLOR  = "#E8ECF0"
LINE_COLOR  = "#D1D5DB"

def eje(size=11, **kwargs):
    return dict(
        gridcolor=GRID_COLOR,
        linecolor=LINE_COLOR,
        tickfont=dict(size=size, color=NEGRO),
        title_font=dict(size=12, color=NEGRO),
        **kwargs
    )

def base_layout(title, height, extra=None):
    cfg = dict(
        title=dict(text=title, font=dict(size=15, color=NEGRO, family="Inter, sans-serif"), x=0.02),
        font=dict(family="Inter, sans-serif", size=12, color=NEGRO),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=50, b=35, l=15, r=15),
        height=height,
    )
    if extra:
        cfg.update(extra)
    return cfg

ESCALA_PURP = [[0,"#EDE9FF"],[0.5,"#6C63FF"],[1,"#2D1B8E"]]
ESCALA_TEAL = [[0,"#CCFBF1"],[0.5,"#2EC4B6"],[1,"#0D7A74"]]
ESCALA_WARM = [[0,"#FFF3CD"],[0.5,"#F7971E"],[1,"#C05C00"]]


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div>
  <div>
    <p class="header-title">HR Analytics Dashboard</p>
    <p class="header-sub">Análisis integral de la fuerza laboral · Contrataciones, rotación y estructura organizacional</p>
  </div>
  <div class="header-badge">RECURSOS HUMANOS</div>
</div>
""", unsafe_allow_html=True)


# ── FILTROS ───────────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([1, 1, 2])

with f1:
    depto_opciones = ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
    depto_sel = st.selectbox("Departamento", depto_opciones)

with f2:
    region_opciones = ["Todas"] + sorted(df["region"].dropna().unique().tolist())
    region_sel = st.selectbox("Región", region_opciones)

with f3:
    año_min = int(df["año_contratacion"].min())
    año_max = int(df["año_contratacion"].max())
    rango   = st.slider("Año de contratación", año_min, año_max, (2000, año_max))

# Aplicar filtros
dff = df.copy()
if depto_sel != "Todos":
    dff = dff[dff["departamento"] == depto_sel]
if region_sel != "Todas":
    dff = dff[dff["region"] == region_sel]
dff = dff[dff["año_contratacion"].between(rango[0], rango[1])]


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Indicadores Clave</p>', unsafe_allow_html=True)

total_emp = len(dff)
activos = len(dff[dff["estatus"] == "Activo"])
inactivos = len(dff[dff["estatus"] == "Inactivo"])
tasa_actividad = (activos / total_emp * 100) if total_emp > 0 else 0
deptos_unicos = dff["departamento"].nunique()
regiones_unicas = dff["region"].nunique()

kpis_data = [
    ("👥", "Total Empleados",  f"{total_emp}",       "#6C63FF"),
    ("✅", "Activos",          f"{activos}",          "#2EC4B6"),
    ("❌", "Inactivos",        f"{inactivos}",        "#E94560"),
    ("📈", "% Actividad",      f"{tasa_actividad:.1f}%",  "#F7971E"),
    ("🏢", "Departamentos",    str(deptos_unicos),   "#6C63FF"),
    ("🌎", "Regiones",         str(regiones_unicas), "#2EC4B6"),
]

columnas = st.columns(6)
for col, (icon, label, val, color) in zip(columnas, kpis_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color}">{val}</div>
        </div>""", unsafe_allow_html=True)


# ── DONA + LÍNEA ──────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Distribución de Estatus · Evolución de Contrataciones</p>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])

with c1:
    # Gráfico de dona: Activo vs Inactivo
    tc = dff["estatus"].value_counts().reset_index()
    tc.columns = ["Estatus", "Cantidad"]
    fig = go.Figure(go.Pie(
        labels=tc["Estatus"], values=tc["Cantidad"], hole=0.58,
        marker=dict(colors=["#2EC4B6","#E94560"], line=dict(color="white", width=3)),
        textinfo="label+percent",
        textfont=dict(size=13, color=NEGRO),
        hovertemplate="<b>%{label}</b><br>%{value:,} empleados<br>%{percent}<extra></extra>"
    ))
    fig.add_annotation(
        text=f"<b>{total_emp:,}</b><br><span style='font-size:11px'>empleados</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=NEGRO)
    )
    fig.update_layout(**base_layout("Activos vs Inactivos", 330, {
        "legend": dict(orientation="h", y=-0.05, x=0.2, font=dict(color=NEGRO, size=12))
    }))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    # Línea de contrataciones por año
    pa = dff.groupby("año_contratacion").size().reset_index(name="Cantidad")
    fig = go.Figure(go.Scatter(
        x=pa["año_contratacion"], y=pa["Cantidad"],
        mode="lines", line=dict(color="#6C63FF", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(108,99,255,0.10)",
        hovertemplate="<b>%{x}</b> → %{y} contrataciones<extra></extra>"
    ))
    fig.update_layout(**base_layout("Contrataciones por año", 330, {
        "xaxis": eje(title="Año"),
        "yaxis": eje(title="Contrataciones"),
        "showlegend": False,
        "hovermode": "x unified"
    }))
    st.plotly_chart(fig, use_container_width=True)


# ── DEPARTAMENTOS ─────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Distribución por Departamento</p>', unsafe_allow_html=True)
top_dep = dff["departamento"].value_counts().head(12).reset_index()
top_dep.columns = ["Departamento", "Empleados"]

dc1, dc2 = st.columns([3, 1])
with dc1:
    fig = go.Figure(go.Bar(
        x=top_dep["Empleados"], y=top_dep["Departamento"], orientation="h",
        marker=dict(color=top_dep["Empleados"], colorscale=ESCALA_PURP,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Top departamentos con más personal", 420, {
        "xaxis": eje(title="Cantidad de empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with dc2:
    st.markdown("**Ranking**")
    td = top_dep.copy(); td.index = range(1, len(td)+1)
    st.dataframe(td.style.bar(subset=["Empleados"], color="#C7C2FF"), use_container_width=True, height=380)


# ── REGIONES ──────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Distribución por Región</p>', unsafe_allow_html=True)
top_reg = dff["region"].value_counts().reset_index()
top_reg.columns = ["Región", "Empleados"]

rc1, rc2 = st.columns([3, 1])
with rc1:
    fig = go.Figure(go.Bar(
        x=top_reg["Empleados"], y=top_reg["Región"], orientation="h",
        marker=dict(color=top_reg["Empleados"], colorscale=ESCALA_TEAL,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Empleados por región", 350, {
        "xaxis": eje(title="Cantidad de empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with rc2:
    st.markdown("**Ranking**")
    tr = top_reg.copy(); tr.index = range(1, len(tr)+1)
    st.dataframe(tr.style.bar(subset=["Empleados"], color="#99F0EA"), use_container_width=True, height=310)


# ── GÉNERO Y MODALIDAD ───────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Género · Modalidad · Jornada</p>', unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

with g1:
    gen = dff["genero"].value_counts().reset_index()
    gen.columns = ["Género", "Cantidad"]
    fig = go.Figure(go.Bar(
        x=gen["Cantidad"], y=gen["Género"], orientation="h",
        marker=dict(color=gen["Cantidad"], colorscale=ESCALA_WARM,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Por Género", 280, {
        "xaxis": eje(title="Empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)

with g2:
    mod = dff["modalidad"].value_counts().reset_index()
    mod.columns = ["Modalidad", "Cantidad"]
    fig = go.Figure(go.Bar(
        x=mod["Cantidad"], y=mod["Modalidad"], orientation="h",
        marker=dict(color=mod["Cantidad"], colorscale=ESCALA_TEAL,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Por Modalidad", 280, {
        "xaxis": eje(title="Empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)

with g3:
    jor = dff["jornada"].value_counts().reset_index()
    jor.columns = ["Jornada", "Cantidad"]
    fig = go.Figure(go.Bar(
        x=jor["Cantidad"], y=jor["Jornada"], orientation="h",
        marker=dict(color=jor["Cantidad"], colorscale=ESCALA_PURP,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Por Jornada", 280, {
        "xaxis": eje(title="Empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)


# ── EDUCACIÓN ─────────────────────────────────────────────────────────────────
st.markdown('<p class="sec-title">Nivel Educativo</p>', unsafe_allow_html=True)
top_ed = dff["educacion"].value_counts().reset_index()
top_ed.columns = ["Educación", "Empleados"]

ec1, ec2 = st.columns([3, 1])
with ec1:
    fig = go.Figure(go.Bar(
        x=top_ed["Empleados"], y=top_ed["Educación"], orientation="h",
        marker=dict(color=top_ed["Empleados"], colorscale=ESCALA_WARM,
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
        hovertemplate="<b>%{y}</b><br>%{x:,} empleados<extra></extra>"
    ))
    fig.update_layout(**base_layout("Distribución por nivel educativo", 300, {
        "xaxis": eje(title="Cantidad de empleados"),
        "yaxis": eje(size=11, categoryorder="total ascending"),
    }))
    st.plotly_chart(fig, use_container_width=True)
with ec2:
    st.markdown("**Ranking**")
    te = top_ed.copy(); te.index = range(1, len(te)+1)
    st.dataframe(te.style.bar(subset=["Empleados"], color="#FDE68A"), use_container_width=True, height=260)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;color:#94A3B8;font-size:0.8rem">
    HR Analytics Dashboard · Fuerza Laboral · Streamlit & Plotly
</div>
""", unsafe_allow_html=True)