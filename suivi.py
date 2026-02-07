import streamlit as st
import pandas as pd
import os
import time

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# Vérifie si l'intro a déjà été montrée
if "intro_complete" not in st.session_state:
    
    intro_placeholder = st.empty()
    
    with intro_placeholder.container():
        # CSS pour image plein écran
        st.markdown("""
            <style>
                   .block-container {
                        padding-top: 1rem;
                        padding-left: 0rem;
                        padding-right: 0rem;
                    }
            </style>
            """, unsafe_allow_html=True)
        
        st.image("noria.jpg", use_container_width=True)
    
    # 1. On affiche l'image pendant 2 secondes (un peu moins long)
    time.sleep(2)
    
    # 2. TRANSITION DOUCE : On affiche un "spinner" de chargement
    # Cela permet à l'œil de comprendre que la page va changer
    with st.spinner("Chargement du tableau de bord..."):
        time.sleep(1.5) # On fait semblant de charger pendant 1.5 secondes
    
    # 3. On efface l'intro
    intro_placeholder.empty()
    
    # 4. Petit message "Toast" en bas à droite pour dire bienvenue (Optionnel mais sympa)
    st.toast("Bienvenue sur le projet Noria !", icon="🏗️")
    
    st.session_state["intro_complete"] = True

# --- 1. CONFIGURATION ---
FICHIER_DONNEES = "mon_suivi.csv"

LISTE_VILLAS = ["Villa 108", "Villa 70", "Villa 101"]
LISTE_TACHES = [
    "1. Réception des axes",
    "2. Fond de fouille",
    "3. Ferraillage Semelles",
    "4. Coulage Béton",
    "5. Poteaux"
]

# --- 2. FONCTIONS ---
def charger_donnees():
    if os.path.exists(FICHIER_DONNEES):
        return pd.read_csv(FICHIER_DONNEES)
    else:
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

# --- 3. INTERFACE PRINCIPALE ---
st.title("🏗️ Suivi Chantier - Villas")

df = charger_donnees()

villa_choisie = st.sidebar.selectbox("🔎 Choisir une Villa :", LISTE_VILLAS)

st.header(f"Suivi : {villa_choisie}")

masque = df["Villa"] == villa_choisie
lignes_villa = df[masque]

for index, row in lignes_villa.iterrows():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(row["Tache"])
        st.caption(f"Preuve actuelle : {row['Preuve']}")
        
    with col2:
        statut_actuel = row["Statut"]
        options = ["À faire", "En cours", "OK", "Non Conforme"]
        
        nouveau_statut = st.selectbox(
            "État", 
            options, 
            index=options.index(statut_actuel),
            key=f"{row['Villa']}-{row['Tache']}"
        )
        
        if nouveau_statut != statut_actuel:
            df.loc[index, "Statut"] = nouveau_statut
            sauvegarder(df)
            st.success("✅ Mis à jour !")
            st.rerun()

    st.divider()