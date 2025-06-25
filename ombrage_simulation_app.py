# ombrage_simulation_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation
import time

st.set_page_config(page_title="🌞 Simulation Ombres PV", layout="wide")
st.title("🏡 Simulation dynamique de l’effet d’ombrage sur un système photovoltaïque")
st.markdown("""
Cette application vous permet de simuler l'impact de différents obstacles (arbres, bâtiments...) sur la production d'énergie solaire d'une maison à Marseille.

- 🏠 Maison orientée plein sud avec toiture inclinée à 30°.
- ☀️ Simulation dynamique heure par heure du déplacement du soleil.
- 🌳 Sélection des obstacles avec visualisation de l’ombre projetée.
""")

# === ENTRÉES ===
st.sidebar.header("🔧 Configuration de la simulation")
nb_obstacles = st.sidebar.slider("Nombre d'obstacles", 0, 3, 1)

obstacles = []
for i in range(nb_obstacles):
    with st.sidebar.expander(f"🚧 Obstacle #{i+1}"):
        type_obs = st.selectbox(f"Type", ["Arbre", "Bâtiment", "Mur", "Colline"], key=f"type{i}")
        hauteur = st.slider("Hauteur (m)", 1, 20, 5, key=f"h{i}")
        distance = st.slider("Distance (m)", 1, 50, 10, key=f"d{i}")
        orientation = st.slider("Orientation (°)", -90, 90, 0, key=f"o{i}")
        obstacles.append({"type": type_obs, "hauteur": hauteur, "distance": distance, "orientation": orientation})

meteo = st.sidebar.radio("☁️ Conditions météo", ["Ensoleillé", "Nuageux", "Pluvieux"])
nb_panneaux = st.sidebar.slider("Nombre de panneaux (400 Wc chacun)", 1, 25, 20)

# === FACTEURS ===
power_per_panel = 0.4  # kWc
irradiation = 1824
rendement = 0.85
facteur_meteo = {"Ensoleillé": 1.0, "Nuageux": 0.75, "Pluvieux": 0.55}[meteo]
kWp = nb_panneaux * power_per_panel
prod_base = kWp * irradiation * rendement * facteur_meteo / 1000  # kWh/an

# === CALCUL PERTE D’OMBRAGE ===
def calc_ombrage(obs, heure):
    pertes = 0
    angle_solaire = max(5, min(80, 90 - abs(12 - heure) * 6))  # approx simplifiée
    for o in obs:
        angle_obs = math.degrees(math.atan(o["hauteur"] / o["distance"]))
        if angle_obs > angle_solaire:
            pertes += min(angle_obs / 90 * 20, 20)
    return min(pertes, 50)

# === ANIMATION DE L'OMBRE ===
st.subheader("🎬 Animation heure par heure")
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 60)
ax.set_ylim(0, 25)
ax.set_xlabel("Distance depuis la maison (m)")
ax.set_ylabel("Hauteur (m)")

# Représentation de la maison
ax.add_patch(plt.Rectangle((0, 0), 2, 6, color="gray", label="Maison"))

bars = []
text = ax.text(45, 22, '', fontsize=12, color='blue')

for i, obs in enumerate(obstacles):
    b = ax.bar(obs["distance"], obs["hauteur"], color="brown", width=1, label=obs["type"])
    bars.append(b[0])

@st.cache_resource(show_spinner=False)
def animate_shadow():
    images = []
    for heure in range(6, 19):
        ax.collections.clear()
        for i, obs in enumerate(obstacles):
            bar = bars[i]
            bar.set_height(obs["hauteur"])
            bar.set_x(obs["distance"])
        angle_sun = max(5, min(80, 90 - abs(12 - heure) * 6))
        text.set_text(f"☀️ Heure: {heure}h – Angle solaire: {angle_sun}°")
        fig.canvas.draw()
        images.append(fig)
    return images

st.pyplot(fig)

# === CALCUL ÉNERGIE ===
heure_actuelle = st.slider("Heure de la journée", 6, 18, 12)
perte_ombrage = calc_ombrage(obstacles, heure_actuelle)
prod_apres_ombre = prod_base * (1 - perte_ombrage / 100)

conso = 8260
autoconso = min(prod_apres_ombre, conso) * 0.9
injection = max(0, prod_apres_ombre - autoconsommation)
reprise = max(0, conso - autoconsommation)

st.subheader("📊 Résultats énergétiques")
st.metric("Production brute (kWh/an)", f"{prod_base:.0f}")
st.metric("Perte ombrage à {heure_actuelle}h", f"{perte_ombrage:.1f}%")
st.metric("Production réelle", f"{prod_apres_ombre:.0f} kWh/an")

# === GRAPHIQUE ÉNERGIE ===
fig2, ax2 = plt.subplots()
labels = ["Autoconsommée", "Injectée", "Reprise"]
values = [autoconso, injection, reprise]
colors = ["green", "orange", "red"]
ax2.bar(labels, values, color=colors)
ax2.set_title("Répartition de l’énergie")
ax2.set_ylabel("kWh/an")
st.pyplot(fig2)

st.markdown("---")
st.caption("Projet S8 – Attaibe Salma – Simulation dynamique d’ombrage – 2025")
