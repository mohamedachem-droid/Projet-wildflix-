# 🐺 WildFlix

**WildFlix** est une plateforme de recommandation de films développée en Python avec **Streamlit**, destinée (avec humour) aux Creusois. L'application combine un système d'authentification, un moteur de recommandations basé sur du Machine Learning (`NearestNeighbors`), un système de vote et un classement des films les plus appréciés.

---

## ✨ Fonctionnalités

- 🔐 **Authentification** des utilisateurs via `streamlit-authenticator` (comptes stockés dans `comptes.csv`)
- 🎲 **Découverte** : films au hasard, derniers sortis, mieux notés
- 📌 **Recherche** d'un film par titre avec menu déroulant
- 🖼️ **Affiches TMDB** et fiches détaillées (année, genre, note, synopsis)
- 🎬 **Bande-annonce** : redirection automatique vers YouTube
- ⭐ **Recommandations** : 5 films similaires via un modèle ML pré-entraîné (`modele.pkl`)
- 👍 **Système de vote** : chaque utilisateur peut voter pour ses films préférés
- 🏆 **Classement** des films les plus populaires (basé sur les votes)

---

## 📂 Structure du projet

```
Projet-wildflix-/
├── wildflix.py              # Application Streamlit principale
├── modele.pkl               # Modèle ML NearestNeighbors entraîné
├── films_clean.csv          # Dataset nettoyé des films (affichage)
├── X_scaled.csv             # Features normalisées (entrée du modèle)
├── comptes.csv              # Comptes utilisateurs
├── requirements.txt         # Dépendances Python
├── datasets/                # Copies des datasets
├── docs/                    # Notebooks de préparation et d'entraînement
│   ├── prepa_df_streamlit.ipynb
│   └── ML + streamlit fichier fusion_2.ipynb
└── .devcontainer/           # Configuration Dev Container
```

---

## 🚀 Installation & lancement

### Prérequis
- Python 3.10+
- `pip` ou `venv`

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/mohamedachem-droid/Projet-wildflix-.git
cd Projet-wildflix-

# 2. Créer un environnement virtuel
python -m venv my_env
source my_env/bin/activate     # Linux/Mac
# my_env\Scripts\activate      # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run wildflix.py
```

L'app sera accessible sur [http://localhost:8501](http://localhost:8501).

---

## 🔐 Connexion

Les identifiants sont définis dans `comptes.csv` (colonnes : `name`, `password`, `email`, `role`, etc.).

> ⚠️ **Note de sécurité** : `comptes.csv` contient des identifiants en clair. Pour la production, il faudrait hasher les mots de passe (bcrypt) et ne pas versionner ce fichier.

---

## 🧠 Pipeline ML

Les notebooks dans `docs/` détaillent la préparation des données et l'entraînement du modèle :

1. **`prepa_df_streamlit.ipynb`** : nettoyage du dataset, sélection des features, gestion des valeurs manquantes
2. **`ML + streamlit fichier fusion_2.ipynb`** : encodage, normalisation (`X_scaled.csv`), entraînement du modèle `NearestNeighbors` et export en `modele.pkl`

Le modèle renvoie les **6 films les plus proches** d'un film donné (le 1er étant le film lui-même, on affiche donc les 5 suivants).

---

## 📊 Données

- **Source des affiches** : [TMDB](https://www.themoviedb.org/) (`https://image.tmdb.org/t/p/w500{poster_path}`)
- **Bandes-annonces** : recherche YouTube dynamique
- **Votes** : stockés localement dans `votes.csv` (créé au premier vote)

---

## 🛠️ Stack technique

| Outil | Usage |
|---|---|
| **Streamlit** | Interface web |
| **Pandas** | Manipulation des données |
| **scikit-learn** | Modèle `NearestNeighbors` |
| **joblib** | Chargement du modèle sérialisé |
| **streamlit-authenticator** | Gestion de l'authentification |

---

## 🐳 Dev Container

Le projet inclut une configuration `.devcontainer/devcontainer.json` permettant de l'ouvrir directement dans VS Code avec un environnement préconfiguré.

---

## 📝 Améliorations possibles

- [ ] Hasher les mots de passe (bcrypt)
- [ ] Migrer `comptes.csv` et `votes.csv` vers une vraie BDD (SQLite/PostgreSQL)
- [ ] Ajouter des filtres (genre, année, note minimale)
- [ ] Historique des films vus par utilisateur
- [ ] Déploiement sur Streamlit Cloud
- [ ] Tests unitaires

---

## 👥 Auteurs

Projet réalisé dans le cadre d'une formation Data / Machine Learning.

- Mohamed Hachem
- Pascal Bafoin
- Etienne Atangana Abega
- De Sousa Fabrice
