import streamlit as st
import pandas as pd
import os
import time
import streamlit.components.v1 as components 

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS PERSONNALISÉ
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
            margin-top: 10px;
            margin-bottom: 50px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Intro
if "intro_complete" not in st.session_state:
    intro_placeholder = st.empty()
    with intro_placeholder.container():
        st.image("noria.jpg", use_container_width=True)
    time.sleep(1.5)
    with st.spinner("Chargement du tableau de bord..."):
        time.sleep(0.5)
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
    if 'scroll_needed' not in st.session_state:
        st.session_state['scroll_needed'] = False

    # --- A. LE TABLEAU (AVEC DÉTECTION DU CLIC) ---
    st.info("👇 Cliquez sur une ligne de tâche. La page descendra automatiquement.")

    def colorer_cellules(val):
        color = 'white'
        if val == 'OK': color = '#d4edda'; font_weight = 'bold'
        elif val == 'Non Conforme': color = '#f8d7da'; font_weight = 'bold'
        elif val == 'En cours': color = '#fff3cd'; font_weight = 'normal'
        else: color = 'white'; font_weight = 'normal'
        return f'background-color: {color}; color: black; font-weight: {font_weight}'

    # Affichage du tableau PROPRE (Sans checkboxes)
    event = st.dataframe(
        df.style.applymap(colorer_cellules),
        use_container_width=True,
        height=400,
        on_select="rerun", 
        selection_mode="single-row",
        hide_index=True  # <--- C'est ça qui enlève les numéros et cases moches à gauche
    )

    # --- LOGIQUE INTELLIGENTE : CLIC -> MISE À JOUR -> SCROLL ---
    if len(event.selection.rows) > 0:
        row_clicked = event.selection.rows[0]
        
        # Si c'est une nouvelle ligne cliquée, on met à jour et on déclenche le scroll
        if row_clicked != st.session_state['selected_tache_index']:
            st.session_state['selected_tache_index'] = row_clicked
            st.session_state['scroll_needed'] = True # On arme le scroll
    
    # --- B. ANCRE HTML CIBLE ---
    st.markdown("<div id='target_inspector'></div>", unsafe_allow_html=True)

    # --- C. SCRIPT DE SCROLL FORCÉ ---
    if st.session_state['scroll_needed']:
        # Script Javascript plus robuste
        js_code = """
            <script>
                var element = window.parent.document.getElementById('target_inspector');
                if (element) {
                    element.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            </script>
        """
        components.html(js_code, height=0)
        st.session_state['scroll_needed'] = False


    # --- D. L'INSPECTEUR (ZONE BLEUE) ---
    with st.container():
        st.markdown("""<div class="inspecteur-box"><h3>🔎 Détails & Documents</h3>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # SÉLECTEUR DE TÂCHE : Piloté par le tableau
            tache_select = st.selectbox(
                "Tâche sélectionnée :", 
                LISTE_TACHES, 
                index=st.session_state['selected_tache_index'],
                key="box_tache",
                disabled=True # On grise pour montrer que ça vient du tableau
            )
        with c2:
            # SÉLECTEUR DE VILLA : Reste en mémoire
            villa_select = st.selectbox(
                "Choisir la Villa concernée :", 
                LISTE_VILLAS,
                index=st.session_state['selected_villa_index'], 
                key="box_villa"
            )
            # Sauvegarde de la villa pour la prochaine fois
            st.session_state['selected_villa_index'] = LISTE_VILLAS.index(villa_select)

        # Récupération du statut
        statut_actuel = df.at[tache_select, villa_select]
        
        st.markdown("---")
        
        col_docs, col_valid = st.columns([2, 1])

        # DOCUMENTS DYNAMIQUES
        with col_docs:
            st.markdown(f"**📂 Preuves pour : {tache_select}**")
            
            if "Réception des axes" in tache_select:
                doc_type = st.radio("Type de doc :", ["Archi", "Topo"], horizontal=True)
                if doc_type == "Archi":
                    c_a, c_b = st.columns(2)
                    c_a.button(f"📂 Autocontrôle ({villa_select})", use_container_width=True)
                    c_b.button(f"📄 PV Archi ({villa_select})", use_container_width=True)
                else:
                    st.button(f"📐 Scan Topo ({villa_select})", use_container_width=True)

            elif "fond de fouille" in tache_select:
                 st.button(f"📄 Document Unique ({villa_select})", use_container_width=True)

            elif "semelles" in tache_select:
                c_a, c_b = st.columns(2)
                c_a.button(f"📂 Autocontrôle ({villa_select})", use_container_width=True)
                c_b.button(f"📄 PV Réception ({villa_select})", use_container_width=True)
            
            else:
                st.info("Pas de configuration pour cette tâche.")

        # VALIDATION
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
                color_text = "green" if statut_actuel == "OK" else "red" if statut_actuel == "Non Conforme" else "grey"
                st.markdown(f"<h3 style='color:{color_text}'>{statut_actuel}</h3>", unsafe_allow_html=True)
                if statut_actuel == "OK": st.balloons()

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