import streamlit as st
import plotly.graph_objects as go
import math

# --- CONFIG ---
st.set_page_config(page_title="Simulation Ombres PV", layout="centered")
st.title("🏡 Etude d'ombrage")

st.markdown("Sélectionnez les obstacles pour visualiser leur impact sur l’ensoleillement, les pertes et la production d’énergie.")

# --- ENTRÉES UTILISATEUR ---
st.sidebar.header("🪵 Obstacles")
nb_obstacles = st.sidebar.slider("Nombre d'obstacles", 0, 3, 1)

obstacles = []
for i in range(nb_obstacles):
    with st.sidebar.expander(f"Obstacle #{i+1}", expanded=True):
        type_obs = st.selectbox("Type", ["Arbre", "Bâtiment", "Mur"], key=f"type{i}")
        hauteur = st.slider("Hauteur (m)", 1, 20, 5, key=f"haut{i}")
        distance = st.slider("Distance (m)", 1, 40, 10, key=f"dist{i}")
        obstacles.append({
            "type": type_obs,
            "hauteur": hauteur,
            "distance": distance
        })

# --- CALCULS ---
power_per_panel = 0.4  # kWc
nb_panneaux = 20
rendement = 0.85
irradiation_marseille = 1824  # kWh/m²/an
kWp = power_per_panel * nb_panneaux

# Production brute
prod_brute = kWp * rendement * irradiation_marseille / 1000  # kWh/an

# Pertes par obstacle (simplifié)
def calcul_perte(obs_list):
    total = 0
    for o in obs_list:
        angle = math.degrees(math.atan(o["hauteur"] / o["distance"]))
        perte = min(angle / 90 * 25, 25)  # max 25% par obstacle
        total += perte
    return min(total, 60)  # max global

perte_pct = calcul_perte(obstacles)
prod_corrigee = prod_brute * (1 - perte_pct / 100)

# --- RÉSULTATS ---
col1, col2, col3 = st.columns(3)
col1.metric("🌞 Production brute", f"{prod_brute:.0f} kWh/an")
col2.metric("🌫️ Pertes d’ombrage", f"{perte_pct:.1f} %")
col3.metric("⚡ Production corrigée", f"{prod_corrigee:.0f} kWh/an")

# --- VISUALISATION ---
st.subheader("🖼️ Visualisation de l’ombrage")

fig = go.Figure()

# Maison
fig.add_trace(go.Scatter(
    x=[0, 0],
    y=[0, 6],
    mode="lines+text",
    line=dict(width=10, color="gray"),
    text=["Maison"],
    textposition="top right",
    name="Maison"
))

# Obstacles
colors = ["green", "brown", "black"]
for i, obs in enumerate(obstacles):
    fig.add_trace(go.Scatter(
        x=[obs["distance"], obs["distance"]],
        y=[0, obs["hauteur"]],
        mode="lines+text",
        line=dict(width=6, color=colors[i % len(colors)]),
        text=[f"{obs['type']} ({obs['hauteur']}m)"],
        textposition="top center",
        name=f"{obs['type']}"
    ))

# Soleil
fig.add_trace(go.Scatter(
    x=[-5], y=[18],
    mode="markers+text",
    marker=dict(size=30, color="gold"),
    text=["☀️ Soleil"],
    textposition="bottom right",
    name="Soleil"
))

fig.update_layout(
    height=400,
    xaxis=dict(title="Distance (m)", range=[-10, 50]),
    yaxis=dict(title="Hauteur (m)", range=[0, 25]),
    plot_bgcolor="#f8f9fa",
    paper_bgcolor="#ffffff",
    margin=dict(l=40, r=40, t=40, b=40),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Projet S8 – Attaibe Salma – Simulation d’ombrage photovoltaïque – 2025")

