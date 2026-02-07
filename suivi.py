import streamlit as st
import pandas as pd
import os
import time  # <--- NOUVEL IMPORT IMPORTANT

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
# On configure la page pour qu'elle prenne toute la largeur
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# Vérifie si l'intro a déjà été montrée
if "intro_complete" not in st.session_state:
    # C'est le tout premier lancement !
    
    # On crée un conteneur vide pour l'animation
    intro_placeholder = st.empty()
    
    with intro_placeholder.container():
        # 1. On affiche l'image en grand
        # Assure-toi que l'image s'appelle bien "noria.jpg" et est dans le dossier
        st.image("noria.jpg", use_container_width=True) 
        
        # 2. On affiche le texte "Flottant" avec du style HTML/CSS (Centré, Bleu, Gros)
        st.markdown("""
            <div style='text-align: center; color: #1f77b4; margin-top: -50px;'>
                <h1 style='font-size: 50px;'>Projet Noria Parcelle G1</h1>
                <h2 style='font-size: 30px;'>Construction 108 Villas</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # On attend 3 secondes
    time.sleep(3)
    
    # On efface tout !
    intro_placeholder.empty()
    
    # On marque l'intro comme "Vue" pour ne plus la refaire
    st.session_state["intro_complete"] = True
# --- 1. CONFIGURATION ---
# C'est ici que le fichier de sauvegarde sera créé
FICHIER_DONNEES = "mon_suivi.csv"

# Tes listes (tu pourras les changer plus tard)
LISTE_VILLAS = ["Villa 108", "Villa 70", "Villa 101"]
LISTE_TACHES = [
    "1. Réception des axes",
    "2. Fond de fouille",
    "3. Ferraillage Semelles",
    "4. Coulage Béton",
    "5. Poteaux"
]

# --- 2. FONCTIONS (Le cerveau) ---
def charger_donnees():
    """Charge ou crée le tableau de données"""
    if os.path.exists(FICHIER_DONNEES):
        return pd.read_csv(FICHIER_DONNEES)
    else:
        # Si le fichier n'existe pas, on le crée vide
        data = []
        for villa in LISTE_VILLAS:
            for tache in LISTE_TACHES:
                data.append({
                    "Villa": villa,
                    "Tache": tache,
                    "Statut": "À faire",
                    "Preuve": "Aucun fichier"
                })
        df = pd.DataFrame(data)
        df.to_csv(FICHIER_DONNEES, index=False)
        return df

def sauvegarder(df):
    df.to_csv(FICHIER_DONNEES, index=False)

# --- 3. INTERFACE (Ce que tu vois) ---
st.title("🏗️ Suivi Chantier - Villas")

# On charge le tableau
df = charger_donnees()

# Menu à gauche pour choisir la Villa
villa_choisie = st.sidebar.selectbox("🔎 Choisir une Villa :", LISTE_VILLAS)

st.header(f"Suivi : {villa_choisie}")

# On filtre pour n'afficher que la villa choisie
masque = df["Villa"] == villa_choisie
lignes_villa = df[masque]

# On affiche chaque tâche ligne par ligne
for index, row in lignes_villa.iterrows():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(row["Tache"])
        # Ici on ajoutera plus tard le bouton pour le fichier preuve
        st.caption(f"Preuve actuelle : {row['Preuve']}")
        
    with col2:
        # La couleur change selon le statut
        statut_actuel = row["Statut"]
        options = ["À faire", "En cours", "OK", "Non Conforme"]
        
        # Le menu déroulant
        nouveau_statut = st.selectbox(
            "État", 
            options, 
            index=options.index(statut_actuel),
            key=f"{row['Villa']}-{row['Tache']}" # Clé unique obligatoire
        )
        
        # Si on change l'état, on sauvegarde
        if nouveau_statut != statut_actuel:
            df.loc[index, "Statut"] = nouveau_statut
            sauvegarder(df)
            st.success("✅ Mis à jour !")
            st.rerun() # Recharge la page

    st.divider() # Ligne de séparation
