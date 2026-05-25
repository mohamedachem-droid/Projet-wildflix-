import streamlit as st
import pandas as pd
import joblib
from streamlit_authenticator import Authenticate
from datetime import datetime
import os
import requests

# === FONCTION  : AFFICHAGE GRILLE DE FILMS ===

# Affiche un DataFrame de films sous forme de grille (5 colonnes).
# Chaque carte contient : affiche, titre, année·genre, note.
# Ajoute un bouton de vote qui enregistre le choix dans votes.csv.


def afficher_grille(df):

    cols = st.columns(5)
    # On parcourt le DataFrame et les colonnes simultanément avec zip
    for col, (_, film) in zip(cols, df.iterrows()):
        with col:
            st.image(
                f"https://image.tmdb.org/t/p/w500{film['poster_path']}"
            )
            st.markdown(f"**{film['title']}**")
            st.caption(
                f"{int(film['Year'])} · {film['genre_principal']}"
            )
            st.caption(
                f"⭐ {film['vote_average']}/10"
            )

            # ===== BOUTON VOTE =====
            # key unique par film pour éviter les conflits Streamlit

            # key basée sur l'index pandas (unique) pour éviter les conflits
            # Streamlit si 2 films ont le même titre
            if st.button(f"👍 Voter", key=f"vote_{film.name}"):

                username = st.session_state["username"]

                # On charge les votes existants (ou DataFrame vide)
                if os.path.exists("votes.csv"):
                    votes_df = pd.read_csv("votes.csv")
                else:
                    votes_df = pd.DataFrame(columns=["username", "film", "date_vote"])

                # On vérifie que l'utilisateur n'a pas déjà voté pour ce film
                deja_vote = (
                    (votes_df["username"] == username)
                    & (votes_df["film"] == film["title"])
                ).any()

                if deja_vote:
                    st.warning(f"Tu as déjà voté pour {film['title']}")
                else:
                    nouveau_vote = pd.DataFrame([{
                        "username": username,
                        "film": film["title"],
                        "date_vote": datetime.now().strftime("%Y-%m-%d")
                    }])
                    votes_df = pd.concat([votes_df, nouveau_vote], ignore_index=True)
                    votes_df.to_csv("votes.csv", index=False)
                    st.success(f"Vote enregistré pour {film['title']} ✅")


# === MISE EN PLACE DE L'AUTHENTIFICATION ===


# On charge les comptes utilisateurs depuis un CSV
try:
    df_comptes = pd.read_csv("comptes.csv")
except FileNotFoundError:
    st.error("⚠️ Fichier comptes.csv introuvable. Contactez l'admin.")
    st.stop()


# streamlit_authenticator attend un dictionnaire structuré, pas un DataFrame.
# On reconstruit donc ce format : {"usernames": {nom: {infos du compte}}}
compte_uti = {"usernames": {}}


# On parcourt chaque ligne du CSV pour remplir le dictionnaire
for index, row in df_comptes.iterrows():

    username = row["name"]

    compte_uti["usernames"][username] = {
        "name": row["name"],
        "password": row["password"],
        "email": row["email"],
        "failed_login_attemps": row["failed_login_attemps"],
        "logged_in": row["logged_in"],
        "role": row["role"],
    }


# Création de l'objet d'authentification
authenticator = Authenticate(
    compte_uti,            # Les données des comptes
    "cookie name",         # Le nom du cookie, un str quelconque
    "cookie key",          # La clé du cookie, un str quelconque
    30,                    # Le nombre de jours avant que le cookie expire
)


# Affiche le formulaire de connexion à l'utilisateur
authenticator.login()


# === CHARGEMENT DES DONNÉES (avec cache) ===
#
# IMPORTANT : ces fonctions sont définies au niveau module, PAS dans un `if`.
# Sinon Streamlit les recrée à chaque rerun → le cache est invalidé et les
# CSV sont relus à chaque clic.
#
# @st.cache_data : emballe la fonction dans une logique de cache.
# 1er appel  : exécute, lit le fichier, GARDE le résultat en mémoire
# 2ème appel : renvoie directement la mémoire, SANS relire le fichier


@st.cache_data
def charger_donnees():
    df = pd.read_csv("films_clean.csv")
    X = pd.read_csv("X_scaled.csv")
    return df, X


# @st.cache_resource : idem, mais pour les objets "vivants" (modèle ML)
@st.cache_resource
def charger_modele():
    return joblib.load("modele.pkl")


# Tout le code ci-dessous ne s'exécute QUE si l'utilisateur est bien connecté
if st.session_state["authentication_status"]:

    # Bouton de déconnexion dans la sidebar
    with st.sidebar:
        st.write(f"Connecté : **{st.session_state['name']}**")
        authenticator.logout("Déconnexion", "sidebar")

    # Récupération des données et du modèle entraîné
    # (les appels restent dans le `if` pour ne rien charger si non connecté)
    df_clean, X = charger_donnees()   # films avec colonnes d'affichage
    modele = charger_modele()         # NearestNeighbors entraîné dans le notebook

    # Titre de l'app + petit message de vérification du chargement
    st.title("🐺 WildFlix : La meilleur plateforme pour les Creusois ")
    st.write(f"Dataset chargé : {df_clean.shape[0]} films, {X.shape[1]} features")

    # === SECTIONS D'ACCUEIL ===

    st.markdown("---")

    # Section 1 : films au hasard
    st.subheader("🎲 À découvrir")
    afficher_grille(df_clean.sample(5))

    # Section 2 : films les plus récents
    st.subheader("🆕 Les plus récents")
    afficher_grille(df_clean.sort_values("Year", ascending=False).head(5))

    # Section 3 : films les mieux notés
    st.subheader("⭐ Les mieux notés")
    afficher_grille(df_clean.sort_values("vote_average", ascending=False).head(5))

    # === SÉLECTION DU FILM ===

    st.markdown("---")   # trait horizontal de séparation visuelle
    st.subheader("📌 Choisissez un film")

    # Menu déroulant avec recherche intégrée.
    # sorted() : on trie les titres par ordre alphabétique.
    # .unique() : on évite les doublons si un titre apparaît plusieurs fois.
    film_choisi = st.selectbox(
        "Tapez ou sélectionnez un titre",
        options=sorted(df_clean["title"].unique())
    )

    st.write(f"Tu as choisi : **{film_choisi}**")

    # === AFFICHE DU FILM CHOISI ===

    # On récupère la ligne complète du film sélectionné.
    # .iloc[0] : transforme le résultat (DataFrame d'1 ligne) en Series,
    # ce qui permet d'accéder aux valeurs avec film["colonne"].
    film = df_clean[df_clean["title"] == film_choisi].iloc[0]

    # Mise en page en 2 colonnes : affiche étroite (1) + infos larges (2)
    col_affiche, col_infos = st.columns([1, 2])

    with col_affiche:
        # poster_path est un chemin relatif TMDB : on ajoute le préfixe pour l'URL complète
        st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}")

    with col_infos:
        st.markdown(f"### {film['title']}")
        st.write(f"📅 Année : {int(film['Year'])}")   # int() pour éviter l'affichage "2009.0"
        st.write(f"🎭 Genre : {film['genre_principal']}")
        st.write(f"⭐ Note : {film['vote_average']:.2}/10")
        st.write(film['overview'])

    # ===== BANDE-ANNONCE =====

    youtube_search = (
        "https://www.youtube.com/results?"
        f"search_query={film['title']}+official+trailer"
    )

    st.link_button(
        "🎬 Voir la bande-annonce",
        youtube_search
    )

    # === RECOMMANDATIONS PAR MODÈLE ===

    st.markdown("---")
    st.subheader(f"⭐ Films similaires à {film_choisi}")

    # 1. On retrouve la position (index) du film choisi dans le DataFrame.
    # Cet index sert à aller chercher les bonnes features dans X.
    idx = df_clean[df_clean["title"] == film_choisi].index[0]

    # 2. Le modèle renvoie les 6 films les plus proches :
    # - distances : à quel point ils sont proches
    # - indices : leurs positions dans le DataFrame
    # X.iloc[[idx]] : double crochet pour passer un DataFrame 2D (attendu par sklearn)
    distances, indices = modele.kneighbors(X.iloc[[idx]])

    # 3. indices[0] = la liste des 6 résultats.
    # [1:] : on enlève le 1er, car c'est le film choisi lui-même (distance 0).
    indices_recos = indices[0][1:]

    # 4. Afficher les 5 recos en grille (5 colonnes)
    cols = st.columns(5)

    # zip() associe chaque colonne à un indice de reco.
    # On parcourt les deux ensemble : colonne 1 ↔ reco 1, colonne 2 ↔ reco 2, etc.
    for col, idx_reco in zip(cols, indices_recos):
        with col:
            film = df_clean.iloc[idx_reco]
            st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}")
            st.markdown(f"**{film['title']}**")
            st.caption(f"{int(film['Year'])} · {film['genre_principal']}")
            st.caption(f"⭐ {film['vote_average']:.2}/10")

    # === TOP DES FILMS ===

    st.markdown("---")
    st.subheader("🏆 Classement des films")

    if os.path.exists("votes.csv"):

        votes_df = pd.read_csv("votes.csv")

        classement = (
            votes_df["film"]
            .value_counts()
            .reset_index()
        )

        classement.columns = ["Film", "Votes"]

        st.dataframe(classement)

        if not classement.empty:

            gagnant = classement.iloc[0]

            st.success(
                f"🎉 Film le plus populaire : "
                f"{gagnant['Film']} "
                f"avec {gagnant['Votes']} votes"
            )


# === LES MESSAGES DE CONNECTION ===

# Si l'identifiant ou le mot de passe est faux
elif st.session_state["authentication_status"] is False:
    st.error("L'username ou le password est/sont incorrect")

# Si l'utilisateur n'a pas encore rempli le formulaire (état initial)
elif st.session_state["authentication_status"] is None:
    st.warning("Les champs username et mot de passe doivent être remplis")
