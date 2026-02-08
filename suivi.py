import streamlit as st
import pandas as pd
import os
import time
import streamlit.components.v1 as components

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS PERSONNALISÉ AMÉLIORÉ
st.markdown("""
    <style>
        /* Stabilise le conteneur du tableau */
        div[data-testid="stDataFrame"] {
            position: static !important;
            width: 100% !important;
        }
        
        /* Enlève les bordures de sélection bleues au clic */
        canvas {
            outline: none !important;
        }

        /* Style des en-têtes */
        div[data-testid="stDataFrame"] th {
            background-color: #f0f2f6;
            color: #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

# Intro
if "intro_complete" not in st.session_state:
    intro_placeholder = st.empty()
    with intro_placeholder.container():
        st.image("noria.jpg", use_container_width=True)
    time.sleep(2)
    with st.spinner("Chargement du tableau de bord..."):
        time.sleep(1.0)
    intro_placeholder.empty()
    st.toast("Bienvenue sur le projet Noria !", icon="🏗️")
    st.session_state["intro_complete"] = True

# --- 1. CONFIGURATION DES DONNÉES ---
FICHIER_DONNEES = "mon_suivi_general.csv"
LISTE_VILLAS = [f"Villa {i}" for i in range(1, 109)]
LISTE_TACHES = [
    "1. Réception des axes",
    "2. Réception fond de fouille",
    "3. Réception coffrage et ferraillage semelles",
    "4. Réception béton des semelles (Labo)"
]

# --- 2. FONCTIONS ---
def charger_donnees():
    if os.path.exists(FICHIER_DONNEES):
        df = pd.read_csv(FICHIER_DONNEES, index_col=0)
    else:
        df = pd.DataFrame(index=LISTE_TACHES, columns=LISTE_VILLAS)
        df = df.fillna("À faire")
        df.to_csv(FICHIER_DONNEES)
    return df

def sauvegarder(df):
    df.to_csv(FICHIER_DONNEES)

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🗂️ Navigation")

st.sidebar.divider()
st.sidebar.markdown("### 🔒 Espace Ingénieur")
password = st.sidebar.text_input("Mot de passe Admin", type="password")

IS_ADMIN = False
if password == "Noria2026": 
    IS_ADMIN = True
    st.sidebar.success("Mode Édition Activé ✅")
else:
    st.sidebar.info("Mode Lecture Seule 👀")

st.sidebar.divider()

choix_menu = st.sidebar.radio(
    "Aller vers :",
    ["📊 Tableau de Suivi Général", "📁 Dossier de démarrage", "📂 Suivi de chaque tâche"]
)

# --- 4. AFFICHAGE PRINCIPAL ---

if choix_menu == "📊 Tableau de Suivi Général":
    st.title("📊 Tableau de Bord - Suivi 108 Villas")
    
    df = charger_donnees()

    def colorer_cellules(val):
        color = 'white'
        if val == 'OK': color = '#d4edda'
        elif val == 'Non Conforme': color = '#f8d7da'
        elif val == 'En cours': color = '#fff3cd'
        return f'background-color: {color}; color: black;'

    # Affichage simple et stable
    st.dataframe(
        df.style.applymap(colorer_cellules),
        use_container_width=True,
        height=700
    )
    

    


# ==========================================
# VUES SECONDAIRES (LIÉES AUX MÊMES DONNÉES)
# ==========================================
elif choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage")
    st.info("Plans généraux, Permis, etc.")

elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers (Vue Arborescence)")
    
    folder_tache = st.selectbox("Ouvrir le dossier de la tâche :", LISTE_TACHES)
    folder_villa = st.selectbox("Ouvrir la villa :", LISTE_VILLAS)
    
    st.markdown(f"### 📂 {folder_tache} > {folder_villa}")
    
    if "Réception des axes" in folder_tache:
        st.write("📄 **Sous-dossier Archi** : [Autocontrôle.pdf] | [PV.pdf]")
        st.write("📐 **Sous-dossier Topo** : [Scan_Topo.pdf]")
    elif "semelles" in folder_tache:
        st.write("📄 **Documents** : [Autocontrôle.pdf] | [PV.pdf]")
    else:
        st.write("📄 **Document** : [Doc_Unique.pdf]")
    
    df = charger_donnees()
    statut = df.at[folder_tache, folder_villa]
    st.caption(f"Statut actuel dans le tableau : {statut}")