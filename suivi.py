import streamlit as st
import pandas as pd
import os
import time

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS PERSONNALISÉ
st.markdown("""
    <style>
        /* Agrandir la police du tableau */
        div[data-testid="stDataFrame"] div[data-testid="stTable"] {
            font-size: 1.1rem !important;
        }
        /* Headers du tableau */
        div[data-testid="stDataFrame"] th {
            font-size: 1.2rem !important;
            background-color: #f0f2f6;
            color: #1f77b4;
            text-align: center;
        }
        /* Enlever les marges de l'image */
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Style pour l'inspecteur (Zone du bas) */
        .inspecteur-box {
            background-color: #e3f2fd; /* Bleu très clair pour attirer l'oeil */
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
            margin-top: 10px;
            margin-bottom: 50px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        /* Style pour la boite d'aide (Info Boss) */
        .help-box {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Intro (Image Noria)
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

# --- 3. BARRE LATÉRALE (NAVIGATION & SÉCURITÉ) ---
st.sidebar.title("🗂️ Navigation")

# --- SÉCURITÉ ---
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

    # --- A. BOITE D'AIDE INTELLIGENTE (REMPLACE LE TEXTE MOCHE) ---
    st.markdown("""
        <div class="help-box">
            👉 <b>Guide Rapide :</b><br>
            1. <b>Cliquez sur une ligne du tableau</b> ci-dessous pour inspecter une tâche.<br>
            2. Descendez vers la zone bleue en bas pour voir les <b>documents (PV, Autocontrôle)</b>.
        </div>
    """, unsafe_allow_html=True)

    # --- B. LE TABLEAU INTERACTIF ---
    
    # Fonction de couleur
    def colorer_cellules(val):
        color = 'white'
        if val == 'OK': color = '#d4edda'; font_weight = 'bold' # Vert
        elif val == 'Non Conforme': color = '#f8d7da'; font_weight = 'bold' # Rouge
        elif val == 'En cours': color = '#fff3cd'; font_weight = 'normal' # Jaune
        else: color = 'white'; font_weight = 'normal'
        return f'background-color: {color}; color: black; font-weight: {font_weight}'

    # Affichage du tableau avec SELECTION ACTIVÉE
    # on_select="rerun" permet de recharger la page dès qu'on clique
    event = st.dataframe(
        df.style.applymap(colorer_cellules),
        use_container_width=True,
        height=400,
        on_select="rerun",  # <--- C'est ça qui enlève le lag et active le clic
        selection_mode="single-row" # On sélectionne une ligne (une tâche)
    )

    # --- LOGIQUE DE SYNCHRONISATION (LE CLIC MAGIQUE) ---
    # Par défaut, on garde la sélection précédente ou la première
    index_tache_selectionnee = 0 
    
    # Si l'utilisateur a cliqué sur une ligne
    if len(event.selection.rows) > 0:
        row_index = event.selection.rows[0]
        # On met à jour la variable pour l'inspecteur en bas
        index_tache_selectionnee = row_index
        # Petit message pour confirmer le clic
        st.toast(f"Tâche sélectionnée : {LISTE_TACHES[row_index]}", icon="👇")


    # --- C. L'INSPECTEUR INTELLIGENT (Zone Bleue) ---
    
    # Ancre HTML pour le repère visuel
    st.markdown("<div id='inspecteur_zone'></div>", unsafe_allow_html=True)
    
    with st.container():
        # Début de la boite stylisée
        st.markdown("""<div class="inspecteur-box"><h3>🔎 Détails & Documents</h3>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # Le sélecteur de Tâche se met à jour AUTOMATIQUEMENT grâce à index=index_tache_selectionnee
            tache_select = st.selectbox(
                "Tâche sélectionnée :", 
                LISTE_TACHES, 
                index=index_tache_selectionnee,
                key="tache_box"
            )
        with c2:
            # Sélecteur de Villa (Reste manuel car impossible à détecter 100% fiable au clic simple)
            villa_select = st.selectbox("Choisir la Villa concernée :", LISTE_VILLAS)

        # Récupération des données
        statut_actuel = df.at[tache_select, villa_select]
        
        st.markdown("---")
        
        col_docs, col_valid = st.columns([2, 1])

        # DOCUMENTS
        with col_docs:
            st.markdown(f"**📂 Preuves : {tache_select} / {villa_select}**")
            
            # Logique des boutons de preuves
            if "Réception des axes" in tache_select:
                doc_type = st.radio("Type :", ["Archi", "Topo"], horizontal=True, label_visibility="collapsed")
                if doc_type == "Archi":
                    c_a, c_b = st.columns(2)
                    c_a.button("📂 Autocontrôle", use_container_width=True)
                    c_b.button("📄 PV Archi", use_container_width=True)
                else:
                    st.button("📐 Scan Topo", use_container_width=True)

            elif "fond de fouille" in tache_select:
                 st.button("📄 Document Unique", use_container_width=True)

            elif "semelles" in tache_select:
                c_a, c_b = st.columns(2)
                c_a.button("📂 Autocontrôle", use_container_width=True)
                c_b.button("📄 PV Réception", use_container_width=True)
            
            else:
                st.info("Aucun document requis pour cette étape.")

        # VALIDATION (Admin Seulement)
        with col_valid:
            st.markdown("**Validation**")
            if IS_ADMIN:
                opts = ["À faire", "En cours", "OK", "Non Conforme"]
                idx = opts.index(statut_actuel) if statut_actuel in opts else 0
                new_statut = st.radio("Statut", opts, index=idx, label_visibility="collapsed")
                
                if new_statut != statut_actuel:
                    df.at[tache_select, villa_select] = new_statut
                    sauvegarder(df)
                    st.success("Enregistré !")
                    time.sleep(0.5)
                    st.rerun()
            else:
                # Vue Boss
                color_text = "green" if statut_actuel == "OK" else "red" if statut_actuel == "Non Conforme" else "grey"
                st.markdown(f"<h3 style='color:{color_text}'>{statut_actuel}</h3>", unsafe_allow_html=True)
                if statut_actuel == "OK": st.balloons()

        st.markdown("</div>", unsafe_allow_html=True) # Fin de la boite bleue


# ==========================================
# AUTRES VUES
# ==========================================
elif choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage")
    st.info("Espace de stockage global.")

elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers")
    st.info("Vue détaillée par dossiers.")