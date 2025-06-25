# ombrage_simulation_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import plotly.graph_objects as go

# CONFIGURATION
st.set_page_config(page_title="Simulation Ombres PV", layout="wide")
st.markdown("""
<style>
    body {
        background-color: #f2f6fc;
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    h1, h2, h3, .stSlider label, .stSelectbox label, .stRadio label {
        color: #234;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏡 Simulation esthétique de l’ombrage solaire")
st.write("""
Cette application vous permet de **choisir les obstacles (type, hauteur)** pour observer leur **effet sur l’ombre projetée**, la **production solaire**, les **pertes** et le **rendement global**.
""")

# ENTRÉES UTILISATEUR
st.sidebar.header("🌳 Obstacle(s)")
nb_obstacles = st.sidebar.slider("Nombre d’obstacles", 0, 3, 1)
obstacles = []

for i in range(nb_obstacles):
    with st.sidebar.expander(f"Obstacle #{i+1}", expanded=True):
        type_obs = st.selectbox("Type", ["Arbre", "Bâtiment", "Mur"], key=f"type{i}")
        hauteur = st.slider("Hauteur (m)", 1, 20, 5, key=f"h{i}")
        distance = st.slider("Distance au panneau (m)", 1, 40, 10, key=f"d{i}")
        obstacles.append({"type": type_obs, "hauteur": hauteur, "distance": distance})

# CALCUL
power_per_panel = 0.4  # kWc
irradiation = 1824  # Marseille kWh/m²/an
rendement = 0.85
nb_panneaux = 20
kWp = nb_panneaux * power_per_panel
prod_base = kWp * irradiation * rendement / 1000  # en kWh/an

# Pertes d’ombrage simplifiées
def pertes_ombrage(obs):
    perte_totale = 0
    for o in obs:
        angle = math.degrees(math.atan(o['hauteur'] / o['distance']))
        perte = min(angle / 90 * 25, 25)  # max 25% par obstacle
        perte_totale += perte
    return min(perte_totale, 60)

perte_pct = pertes_ombrage(obstacles)
prod_corrigée = prod_base * (1 - perte_pct / 100)

# Résultats
col1, col2, col3 = st.columns(3)
col1.metric("🔆 Production brute", f"{prod_base:.0f} kWh/an")
col2.metric("📉 Perte d’ombrage", f"{perte_pct:.1f}%")
col3.metric("⚡ Production nette", f"{prod_corrigée:.0f} kWh/an")

# VISUALISATION PLOTLY
st.subheader("🖼️ Visualisation esthétique de l’ombrage")
fig = go.Figure()

# Maison
fig.add_trace(go.Scatter(
    x=[0, 0], y=[0, 6], mode='lines+text', line=dict(width=6),
    text=["Maison"], textposition="top right",
    name='Maison'))

# Obstacles
colors = ["green", "brown", "gray"]
for i, obs in enumerate(obstacles):
    fig.add_trace(go.Scatter(
        x=[obs['distance'], obs['distance']],
        y=[0, obs['hauteur']],
        mode='lines+text',
        line=dict(width=4, color=colors[i % len(colors)]),
        text=[f"{obs['type']} ({obs['hauteur']}m)"],
        textposition="top center",
        name=f"Obstacle {i+1}"
    ))

# Soleil
fig.add_trace(go.Scatter(
    x=[-5], y=[20], mode='markers+text', marker=dict(size=30, color='gold'),
    text=["☀️ Soleil"], textposition="bottom right", name="Soleil"
))

fig.update_layout(
    xaxis=dict(title='Distance (m)', range=[-10, 50]),
    yaxis=dict(title='Hauteur (m)', range=[0, 25]),
    plot_bgcolor='#f0f2f6',
    paper_bgcolor='#f9fbfe',
    margin=dict(l=40, r=40, t=40, b=40),
    height=400,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Simulation esthétique – Projet S8 – Attaibe Salma – 2025")
