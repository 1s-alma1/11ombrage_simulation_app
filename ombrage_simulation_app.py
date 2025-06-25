# ombrage_simulation_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

st.set_page_config(page_title="Simulation Ombres & PV ☀️", layout="wide")
st.title("🏠 Simulation de l'effet d'ombrage sur un système photovoltaïque")
st.markdown("""
Sélectionnez les obstacles, leur hauteur, distance et orientation pour analyser leur impact sur la production solaire.
La maison est orientée **plein sud (azimut = 0°)** avec une toiture inclinée à **30°** à Marseille.
""")

# === ENTRÉES UTILISATEUR ===
st.sidebar.header("🌲 Obstacle(s) à simuler")
nb_obstacles = st.sidebar.slider("Nombre d'obstacles (max 3)", 0, 3, 1)

obstacles = []
for i in range(nb_obstacles):
    with st.sidebar.expander(f"🔧 Obstacle #{i+1}"):
        type_obs = st.selectbox(f"Type d'obstacle #{i+1}", ["Arbre", "Bâtiment", "Mur", "Colline"], key=f"type{i}")
        hauteur = st.slider(f"Hauteur (m)", 1, 20, 5, key=f"h{i}")
        distance = st.slider(f"Distance au panneau (m)", 1, 50, 10, key=f"d{i}")
        orientation = st.slider(f"Orientation par rapport au sud (°)", -90, 90, 0, key=f"o{i}")
        obstacles.append({"type": type_obs, "hauteur": hauteur, "distance": distance, "orientation": orientation})

# === MÉTÉO ET PANNEAU ===
st.sidebar.header("⚙️ Configuration solaire")
meteo = st.sidebar.radio("Conditions météorologiques", ["Ensoleillé", "Nuageux", "Pluvieux"])
nb_panneaux = st.sidebar.slider("Nombre de panneaux (400 Wc chacun)", 1, 25, 20)

# === FACTEURS ===
facteur_meteo = {"Ensoleillé": 1.0, "Nuageux": 0.75, "Pluvieux": 0.55}[meteo]
power_per_panel = 0.4  # kWc
surface_par_module = 1.7
irradiation_marseille = 1824  # kWh/m2/an
rendement_systeme = 0.85

# === PRODUCTION SANS OMBRE ===
kWp = nb_panneaux * power_per_panel
prod_theorique = kWp * irradiation_marseille * rendement_systeme * facteur_meteo / 1000  # kWh/an

# === CALCUL DES PERTES DUES À L'OMBRE ===
def calc_ombre_loss(obs):
    loss = 0
    for o in obs:
        angle_ombre_deg = math.degrees(math.atan(o["hauteur"] / o["distance"]))
        if angle_ombre_deg > 6:  # seuil de soleil hivernal
            loss += min(angle_ombre_deg / 90 * 25, 25)  # max 25% par obstacle
    return min(loss, 60)  # max total 60%

ombre_loss_percent = calc_ombre_loss(obstacles)
prod_apres_ombre = prod_theorique * (1 - ombre_loss_percent / 100)

# === ÉNERGIE AUTOCONSOMMÉE / INJECTÉE ===
conso_maison = 8260
autoconsommation = min(conso_maison, prod_apres_ombre) * 0.9
injection = max(0, prod_apres_ombre - autoconsommation)
reprise = max(0, conso_maison - autoconsommation)

# === VISUALISATION ===
st.subheader("🔎 Résultats de production")
st.metric("🌞 Production sans ombre (kWh/an)", f"{prod_theorique:.0f}")
st.metric("🌑 Production après ombrage (kWh/an)", f"{prod_apres_ombre:.0f}")
st.metric("❌ Pertes d’ombrage (%)", f"{ombre_loss_percent:.1f}%")

# === BAR CHART ===
st.subheader("⚡ Répartition annuelle de l’énergie")
fig, ax = plt.subplots()
labels = ["Autoconsommée", "Injectée", "Reprise réseau"]
values = [autoconsommation, injection, reprise]
colors = ["green", "orange", "red"]
ax.bar(labels, values, color=colors)
ax.set_ylabel("Énergie (kWh)")
ax.set_title("Répartition de l’énergie")
ax.grid(axis='y')
st.pyplot(fig)

# === VISUALISATION D’OMBRE SIMPLIFIÉE ===
if nb_obstacles > 0:
    st.subheader("🕶️ Visualisation de l’ombrage (schéma simplifié)")
    fig2, ax2 = plt.subplots(figsize=(10, 2))
    ax2.set_xlim(0, 60)
    ax2.set_ylim(0, 25)
    ax2.set_xlabel("Distance depuis les panneaux (m)")
    ax2.set_ylabel("Hauteur (m)")
    ax2.axhline(y=0, color='gray', linestyle='--')
    for o in obstacles:
        ax2.plot([o['distance']], [o['hauteur']], marker='o', label=f"{o['type']} ({o['hauteur']}m)")
        ax2.vlines(o['distance'], 0, o['hauteur'], linestyle='dotted')
    ax2.legend()
    st.pyplot(fig2)

st.markdown("---")
st.caption("Projet S8 – Simulation dynamique photovoltaïque – Attaibe Salma – Marseille 2025")
