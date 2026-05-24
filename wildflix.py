import streamlit as st
import pandas as pd
import joblib

# === CHARGEMENT DES DONNÉES (avec cache) ===

@st.cache_data
def charger_donnees():
    df = pd.read_csv("films_clean.csv")
    X = pd.read_csv("X_scaled.csv")
    return df, X

@st.cache_resource
def charger_modele():
    return joblib.load("modele.pkl")

df_clean = charger_donnees()[0]
X = charger_donnees()[1]
modele = charger_modele()

# Test que tout est bien chargé
st.title("🐺 WildFlix")
st.write(f"Dataset chargé : {df_clean.shape[0]} films, {X.shape[1]} features")

# === SÉLECTION DU FILM ===

st.markdown("---")  # ligne de séparation
st.subheader("📌 Choisissez un film")

film_choisi = st.selectbox(
    "Tapez ou sélectionnez un titre",
    options=sorted(df_clean["title"].unique())
)

st.write(f"Tu as choisi : **{film_choisi}**")

# === RECOMMANDATIONS ===

st.markdown("---")
st.subheader(f"⭐ Films similaires à {film_choisi}")

# 1. Trouver l'index du film choisi
idx = df_clean[df_clean["title"] == film_choisi].index[0]

# 2. Demander les 6 plus proches voisins (5 recos + le film lui-même)
distances, indices = modele.kneighbors(X.iloc[[idx]])

# 3. Récupérer les indices des recos (on enlève le 1er = le film lui-même)
indices_recos = indices[0][1:]

# 4. Afficher les 5 recos en grille (5 colonnes)
cols = st.columns(5)

for col, idx_reco in zip(cols, indices_recos):
    with col:
        film = df_clean.iloc[idx_reco]
        st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}")
        st.markdown(f"**{film['title']}**")
        st.caption(f"{int(film['Year'])} · {film['genre_principal']}")
        st.caption(f"⭐ {film['vote_average']}/10")