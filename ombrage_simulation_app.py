import streamlit as st
import math

# --- CONFIG ---
st.set_page_config(page_title="Simulation Ombres PV", layout="centered")
st.title("🌤️ Simulation d’ombrage simple")

st.markdown("Définissez les obstacles autour de votre installation photovoltaïque pour estimer les pertes liées à l’ombre.")

# --- ENTRÉES UTILISATEUR ---
st.sidebar.header("🪵 Obstacles")
nb_obstacles = st.sidebar.slider("Nombre d'obstacles", 0, 3, 1)

obstacles = []
for i in range(nb_obstacles):
    with st.sidebar.expander(f"Obstacle #{i+1}", expanded=True):
        type_obs = st.selectbox("Type", ["Arbre", "Bâtiment", "Mur"], key=f"type{i}")
        hauteur = st.slider("Hauteur (m)", 1, 20, 5, key=f"haut{i}")
        distance = st.slider("Distance (m)", -20, 40, 10, key=f"dist{i}")  # autoriser distance négative
        obstacles.append({
            "type": type_obs,
            "hauteur": hauteur,
            "distance": distance
        })

# --- PARAMÈTRES SYSTÈME ---
power_per_panel = 0.4  # kWc
nb_panneaux = 20
rendement = 0.85
irradiation = 1824  # kWh/m²/an
kWp = power_per_panel * nb_panneaux

# --- CALCULS ---
prod_brute = kWp * rendement * irradiation / 1000  # kWh/an

def calcul_perte(obs_list):
    total = 0
    for o in obs_list:
        try:
            angle = math.degrees(math.atan(o["hauteur"] / abs(o["distance"])))
        except ZeroDivisionError:
            angle = 90
        perte = min(angle / 90 * 25, 25)
        total += perte
    return min(total, 60)

perte_pct = calcul_perte(obstacles)
prod_corrigee = prod_brute * (1 - perte_pct / 100)

# --- RÉSULTATS ---
st.subheader("📊 Résultats")
st.write(f"**🌞 Production brute estimée :** `{prod_brute:.0f} kWh/an`")
st.write(f"**🌫️ Pertes dues à l’ombrage :** `{perte_pct:.1f} %`")
st.write(f"**⚡ Production corrigée estimée :** `{prod_corrigee:.0f} kWh/an`")

st.markdown("---")
st.caption("Projet S8 – Simulation simplifiée d’ombrage – 2025")

