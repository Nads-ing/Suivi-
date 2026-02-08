import streamlit as st
import pandas as pd
import os
import time

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS PERSONNALISÉ
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Style Inspecteur */
        .inspecteur-box {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
            margin-top: 20px;
            margin-bottom: 50px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        /* Boutons cellules */
        div.stButton > button {
            width: 100%;
            height: 45px;
            font-size: 0.85rem;
            font-weight: bold;
            border-radius: 5px;
            border: 1px solid #ddd;
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

def couleur_statut(statut):
    """Retourne la couleur selon le statut"""
    if statut == "OK":
        return "#28a745"  # Vert
    elif statut == "Non Conforme":
        return "#dc3545"  # Rouge
    elif statut == "En cours":
        return "#ffc107"  # Jaune
    else:
        return "#6c757d"  # Gris

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
    
    # Initialisation des variables de session
    if 'selected_tache' not in st.session_state:
        st.session_state['selected_tache'] = LISTE_TACHES[0]
    if 'selected_villa' not in st.session_state:
        st.session_state['selected_villa'] = LISTE_VILLAS[0]
    if 'scroll_to_inspector' not in st.session_state:
        st.session_state['scroll_to_inspector'] = False

    # --- A. SÉLECTION RAPIDE (OPTIONNEL - POUR LE BOSS) ---
    with st.expander("🎯 Accès Rapide - Sélection Manuelle", expanded=False):
        col_t, col_v = st.columns(2)
        with col_t:
            quick_tache = st.selectbox("Tâche", LISTE_TACHES, key="quick_tache")
        with col_v:
            quick_villa = st.selectbox("Villa", LISTE_VILLAS, key="quick_villa")
        
        if st.button("📍 Charger cette cellule", use_container_width=True):
            st.session_state['selected_tache'] = quick_tache
            st.session_state['selected_villa'] = quick_villa
            st.session_state['scroll_to_inspector'] = True
            st.rerun()

    st.divider()

    # --- B. TABLEAU VISUEL AVEC BOUTONS CLIQUABLES ---
    st.subheader("📋 Vue d'ensemble des 4 tâches")
    st.info("👇 Cliquez sur n'importe quelle case pour voir les détails en bas.")
    
    # Pour chaque tâche, on affiche une ligne avec des boutons cliquables
    for tache in LISTE_TACHES:
        st.markdown(f"**{tache}**")
        
        # On affiche 9 villas par ligne (pour que ça rentre)
        num_cols = 9
        villa_chunks = [LISTE_VILLAS[i:i+num_cols] for i in range(0, len(LISTE_VILLAS), num_cols)]
        
        for chunk in villa_chunks:
            cols = st.columns(len(chunk))
            
            for idx, villa in enumerate(chunk):
                statut = df.at[tache, villa]
                couleur = couleur_statut(statut)
                
                with cols[idx]:
                    # Bouton cliquable avec couleur
                    label = f"{villa.split()[1]}"  # Juste le numéro (ex: "1" au lieu de "Villa 1")
                    
                    # Utilisation d'un key unique pour chaque bouton
                    button_key = f"btn_{tache}_{villa}"
                    
                    # Style inline du bouton
                    st.markdown(
                        f"""<style>
                        div[data-testid="stButton"] button[kind="secondary"][data-key="{button_key}"] {{
                            background-color: {couleur} !important;
                            color: white !important;
                        }}
                        </style>""",
                        unsafe_allow_html=True
                    )
                    
                    if st.button(label, key=button_key, use_container_width=True):
                        # ✅ MISE À JOUR INSTANTANÉE
                        st.session_state['selected_tache'] = tache
                        st.session_state['selected_villa'] = villa
                        st.session_state['scroll_to_inspector'] = True
                        st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

    # --- C. ZONE INSPECTEUR (AUTO-SCROLL SIMULÉ) ---
    
    # Si on vient de cliquer, on affiche d'abord un placeholder vide pour "pousser" vers le bas
    if st.session_state['scroll_to_inspector']:
        st.markdown("<br>" * 3, unsafe_allow_html=True)  # Espacement
        st.session_state['scroll_to_inspector'] = False

    st.markdown("---")
    st.markdown("## 🔎 Inspecteur de Cellule")
    
    with st.container():
        st.markdown("""<div class="inspecteur-box">""", unsafe_allow_html=True)
        
        # Affichage de la sélection actuelle
        st.markdown(f"### 📍 Cellule Sélectionnée : **{st.session_state['selected_tache']}** × **{st.session_state['selected_villa']}**")
        
        tache_select = st.session_state['selected_tache']
        villa_select = st.session_state['selected_villa']
        
        # Récupération du statut
        statut_actuel = df.at[tache_select, villa_select]
        
        st.markdown("---")
        
        col_docs, col_valid = st.columns([2, 1])

        # PARTIE DOCUMENTS (DYNAMIQUE SELON LA TÂCHE)
        with col_docs:
            st.markdown(f"**📂 Preuves pour : {tache_select}**")
            
            if "Réception des axes" in tache_select:
                doc_type = st.radio("Type de doc :", ["Archi", "Topo"], horizontal=True, key="radio_doc_type")
                if doc_type == "Archi":
                    c_a, c_b = st.columns(2)
                    c_a.button(f"📂 Autocontrôle ({villa_select})", use_container_width=True, key="btn_auto_archi")
                    c_b.button(f"📄 PV Archi ({villa_select})", use_container_width=True, key="btn_pv_archi")
                else:
                    st.button(f"📐 Scan Topo ({villa_select})", use_container_width=True, key="btn_topo")

            elif "fond de fouille" in tache_select:
                 st.button(f"📄 Document Unique ({villa_select})", use_container_width=True, key="btn_fond_fouille")

            elif "semelles" in tache_select:
                c_a, c_b = st.columns(2)
                c_a.button(f"📂 Autocontrôle ({villa_select})", use_container_width=True, key="btn_auto_sem")
                c_b.button(f"📄 PV Réception ({villa_select})", use_container_width=True, key="btn_pv_sem")
            
            else:
                st.info("Pas de configuration pour cette tâche.")

        # PARTIE VALIDATION (ADMIN SEULEMENT)
        with col_valid:
            st.markdown("**Validation**")
            if IS_ADMIN:
                opts = ["À faire", "En cours", "OK", "Non Conforme"]
                idx = opts.index(statut_actuel) if statut_actuel in opts else 0
                new_statut = st.radio("Statut", opts, index=idx, label_visibility="collapsed", key="radio_statut")
                
                if new_statut != statut_actuel:
                    df.at[tache_select, villa_select] = new_statut
                    sauvegarder(df)
                    st.success("✅ Enregistré !")
                    time.sleep(0.8)
                    st.rerun()
            else:
                # Vue Boss (Lecture seule)
                color_text = "green" if statut_actuel == "OK" else "red" if statut_actuel == "Non Conforme" else "orange" if statut_actuel == "En cours" else "grey"
                st.markdown(f"<h2 style='color:{color_text}; text-align:center;'>{statut_actuel}</h2>", unsafe_allow_html=True)
                if statut_actuel == "OK": 
                    st.balloons()

        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# VUES SECONDAIRES
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