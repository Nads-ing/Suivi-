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
        /* Style pour l'inspecteur qui apparaît */
        .inspecteur-box {
            background-color: #e3f2fd; /* Bleu très clair */
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #2196f3;
            margin-top: 10px;
            margin-bottom: 20px;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Intro (Code inchangé)
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
st.sidebar.divider()
choix_menu = st.sidebar.radio("Aller vers :", ["📊 Tableau de Suivi Général", "📁 Dossier de démarrage", "📂 Suivi de chaque tâche"])

# --- 4. AFFICHAGE PRINCIPAL ---

if choix_menu == "📊 Tableau de Suivi Général":
    
    # --- POP-UP D'AIDE (Sidebar Droite ou Expander) ---
    with st.expander("ℹ️ AIDE : Comment utiliser ce tableau ?", expanded=True):
        st.info("👆 **Cliquez simplement sur une case** du tableau pour voir les documents et la validation.")

    st.title("📊 Tableau de Bord - Suivi 108 Villas")
    
    df = charger_donnees()

    # --- A. LE GRAND TABLEAU INTERACTIF ---
    # C'est ici la magie : on_select="rerun" + selection_mode="single-cell"
    
    def colorer_cellules(val):
        color = 'white'
        if val == 'OK': color = '#d4edda' # Vert
        elif val == 'Non Conforme': color = '#f8d7da' # Rouge
        elif val == 'En cours': color = '#fff3cd' # Jaune
        return f'background-color: {color}; color: black;'

    # On affiche le tableau et on capture l'événement de sélection
    event = st.dataframe(
        df.style.applymap(colorer_cellules),
        use_container_width=True,
        height=500,
        on_select="rerun",           # Recharge la page au clic
        selection_mode="single-column" # Sélectionne par colonne (Villa) ou case
    )

    # --- B. L'INSPECTEUR DYNAMIQUE (S'ouvre au clic) ---
    
    # On vérifie si une case a été cliquée
    # event.selection ressemble à : {'rows': [0], 'columns': ['Villa 3']}
    if len(event.selection['rows']) > 0 and len(event.selection['columns']) > 0:
        
        # On récupère les indices
        idx_ligne = event.selection['rows'][0]
        nom_colonne = event.selection['columns'][0] # C'est le nom de la Villa (ex: "Villa 3")
        
        # On trouve le nom de la tâche grâce à l'index
        nom_tache = df.index[idx_ligne]
        
        # On scrolle vers le bas (Astuce Streamlit : on met l'élément en premier dans le code mais il s'affiche après le reload)
        # Malheureusement le scroll auto pur est bloqué par les navigateurs, mais l'élément apparaîtra clairement.
        
        st.markdown("---")
        
        # --- LA BOITE MAGIQUE ---
        with st.container():
            st.markdown(f"""<div class="inspecteur-box"><h3>🔎 INSPECTION : {nom_colonne}</h3>""", unsafe_allow_html=True)
            st.markdown(f"**Tâche sélectionnée :** {nom_tache}")
            
            col_docs, col_valid = st.columns([2, 1])

            # PARTIE GAUCHE : DOCUMENTS
            with col_docs:
                st.markdown("#### 📂 Documents disponibles")
                
                # Logique des boutons selon la tâche
                if "Réception des axes" in nom_tache:
                    tabs = st.tabs(["📐 Archi", "🗺️ Topo"])
                    with tabs[0]:
                        c_a, c_b = st.columns(2)
                        st.button(f"📂 Autocontrôle ({nom_colonne})", key=f"btn_ac_{nom_colonne}")
                        st.button(f"📄 PV Archi ({nom_colonne})", key=f"btn_pv_{nom_colonne}")
                    with tabs[1]:
                        st.button(f"📐 Scan Topo ({nom_colonne})", key=f"btn_topo_{nom_colonne}")
                
                elif "fond de fouille" in nom_tache:
                     st.button(f"📄 Document Unique ({nom_colonne})", key=f"btn_doc_{nom_colonne}")

                elif "semelles" in nom_tache:
                    c_a, c_b = st.columns(2)
                    st.button(f"📂 Autocontrôle ({nom_colonne})", key=f"btn_sem_ac_{nom_colonne}")
                    st.button(f"📄 PV Réception ({nom_colonne})", key=f"btn_sem_pv_{nom_colonne}")
                
                else:
                    st.warning("Aucun document configuré pour cette tâche.")

            # PARTIE DROITE : VALIDATION
            with col_valid:
                st.markdown("#### ✅ Validation")
                statut_actuel = df.at[nom_tache, nom_colonne]
                
                if IS_ADMIN:
                    options = ["À faire", "En cours", "OK", "Non Conforme"]
                    idx = options.index(statut_actuel) if statut_actuel in options else 0
                    new_statut = st.radio("État :", options, index=idx, key=f"radio_{nom_colonne}_{nom_tache}")
                    
                    if new_statut != statut_actuel:
                        df.at[nom_tache, nom_colonne] = new_statut
                        sauvegarder(df)
                        st.success("Sauvegardé !")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    if statut_actuel == "OK": st.success(f"STATUT : {statut_actuel}")
                    elif statut_actuel == "Non Conforme": st.error(f"STATUT : {statut_actuel}")
                    else: st.info(f"STATUT : {statut_actuel}")
            
            st.markdown("</div>", unsafe_allow_html=True)

# Autres menus (inchangés)
elif choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage Chantier")
    st.write("En construction...")
elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers")
    st.write("En construction...")