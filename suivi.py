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
        /* Agrandir la police du tableau */
        div[data-testid="stDataFrame"] div[data-testid="stTable"] {
            font-size: 1.1rem !important;
        }
        div[data-testid="stDataFrame"] th {
            font-size: 1.2rem !important;
            background-color: #f0f2f6;
            color: #1f77b4;
            text-align: center;
        }
        
        /* FIXE LE PROBLÈME DE FLOTTEMENT */
        div[data-testid="stDataFrame"] {
            position: relative !important;
        }
        
        div[data-testid="stDataFrame"] > div {
            overflow-x: auto !important;
            overflow-y: auto !important;
        }
        
        /* Empêcher le déplacement des cellules */
        div[data-testid="stDataFrame"] table {
            table-layout: fixed !important;
            width: 100% !important;
        }
        
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* Zone Inspecteur (Cible du scroll) */
        .inspecteur-target {
            scroll-margin-top: 20px;
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
    
    # Initialisation des variables de session
    if 'selected_tache_index' not in st.session_state:
        st.session_state['selected_tache_index'] = 0
    if 'selected_villa_index' not in st.session_state:
        st.session_state['selected_villa_index'] = 0
    if 'trigger_scroll' not in st.session_state:
        st.session_state['trigger_scroll'] = False
    if 'last_clicked_cell' not in st.session_state:
        st.session_state['last_clicked_cell'] = None

    # --- A. LE TABLEAU (AVEC DÉTECTION DU CLIC SUR CELLULE) ---
    st.info("👇 Cliquez sur une cellule pour voir les détails en bas (Tâche + Villa)")

    def colorer_cellules(val):
        color = 'white'
        if val == 'OK': 
            color = '#d4edda'
            font_weight = 'bold'
        elif val == 'Non Conforme': 
            color = '#f8d7da'
            font_weight = 'bold'
        elif val == 'En cours': 
            color = '#fff3cd'
            font_weight = 'normal'
        else: 
            color = 'white'
            font_weight = 'normal'
        return f'background-color: {color}; color: black; font-weight: {font_weight}'

    st.dataframe(
        df.style.applymap(colorer_cellules),
        use_container_width=True,
        height=600 # Vous pouvez augmenter la hauteur puisqu'il y a plus de place
    )

    # --- LOGIQUE INTELLIGENTE : CLIC CELLULE → MISE À JOUR TÂCHE + VILLA → SCROLL ---
    cell_clicked = False
    
    if len(event.selection.rows) > 0 and len(event.selection.columns) > 0:
        row_index = event.selection.rows[0]
        col_index = event.selection.columns[0]
        
        # Créer un identifiant unique de la cellule
        current_cell = (row_index, col_index)
        
        # Vérifier si c'est une nouvelle cellule cliquée
        if current_cell != st.session_state['last_clicked_cell']:
            cell_clicked = True
            st.session_state['last_clicked_cell'] = current_cell
            st.session_state['selected_tache_index'] = row_index
            st.session_state['selected_villa_index'] = col_index
            st.session_state['trigger_scroll'] = True

    # Afficher quelle cellule est sélectionnée
    if st.session_state['last_clicked_cell'] is not None:
        tache_name = LISTE_TACHES[st.session_state['selected_tache_index']]
        villa_name = LISTE_VILLAS[st.session_state['selected_villa_index']]
        st.markdown(
            f"""<div class="selected-cell-info">
            📍 Cellule sélectionnée : <strong>{tache_name}</strong> × <strong>{villa_name}</strong>
            </div>""", 
            unsafe_allow_html=True
        )

    # --- B. ANCRE HTML POUR LE SCROLL ---
    st.markdown("<div id='inspecteur_ancre' class='inspecteur-target'></div>", unsafe_allow_html=True)

    # --- C. JAVASCRIPT POUR FAIRE LE SCROLL AUTOMATIQUE ---
    if st.session_state['trigger_scroll']:
        components.html("""
            <script>
                setTimeout(function() {
                    var element = window.parent.document.getElementById('inspecteur_ancre');
                    if (element) {
                        element.scrollIntoView({behavior: 'smooth', block: 'start'});
                    }
                }, 100);
            </script>
        """, height=0)
        st.session_state['trigger_scroll'] = False

    


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