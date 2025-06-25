import streamlit as st
import plotly.graph_objects as go
import math

# --- CONFIG ---
st.set_page_config(page_title="Simulation Ombres PV", layout="centered")
st.title("🌞 Simulation d’ombrage photovoltaïque")

st.markdown("Ajoutez les obstacles devant les panneaux (orientation plein sud) pour estimer les pertes d’énergie.")

# --- ENTRÉES UTILISATEUR ---
st.sidebar.header("🪵 Obstacles")
nb_obstacles = st.sidebar.slider("Nombre d'obstacles", 0, 3, 1)

obstacles = []
for i in range(nb_obstacles):
    with st.sidebar.expander(f"Obstacle #{i+1}", expanded=True):
        type_obs = st.selectbox("Type", ["Arbre", "Bâtiment", "Mur"], key=f"type{i}")
        hauteur = st.slider("Hauteur (m)", 1, 20, 5, key=f"haut{i}")
        distance = st.slider("Distance (m)", -20, 40, 10, key=f"dist{i}")  # Autorise obstacle derrière
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

# --- AFFICHAGE DES RÉSULTATS (Version esthétique) ---
st.subheader("📊 Résultats")

st.markdown("""
<div style="background-color: #f0f4f8; padding: 20px; border-radius: 10px; font-size: 18px; color: #333;">
    <b>🌞 Production brute estimée :</b> <span style="font-size: 22px; color: green;"><b>{:.0f} kWh/an</b></span><br><br>
    <b>🌫️ Pertes dues à l’ombrage :</b> <span style="font-size: 22px; color: orange;"><b>{:.1f} %</b></span><br><br>
    <b>⚡ Production corrigée estimée :</b> <span style="font-size: 22px; color: blue;"><b>{:.0f} kWh/an</b></span>
</div>
""".format(prod_brute, perte_pct, prod_corrigee), unsafe_allow_html=True)


# --- VISUALISATION ---
st.subheader("🖼️ Vue simplifiée (orientation sud)")

fig = go.Figure()

# Maison
fig.add_trace(go.Scatter(
    x=[0, 0],
    y=[0, 6],
    mode="lines+text",
    line=dict(width=10, color="gray"),
    text=["Maison"],
    textposition="top right"
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
        textposition="top center"
    ))

# Soleil positionné plein sud à midi
fig.add_trace(go.Scatter(
    x=[0],
    y=[20],
    mode="markers+text",
    marker=dict(size=30, color="gold"),
    text=["☀️ Soleil (Sud)"],
    textposition="bottom center"
))

fig.update_layout(
    height=400,
    xaxis=dict(title="Distance (m)", range=[-25, 50]),
    yaxis=dict(title="Hauteur (m)", range=[0, 25]),
    plot_bgcolor="#f8f9fa",
    paper_bgcolor="#ffffff",
    margin=dict(l=40, r=40, t=40, b=40),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Projet S8 – Attaibe Salma – Simulation d'ombrage – 2025")
