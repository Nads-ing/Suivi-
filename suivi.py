import streamlit as st
import x as pd
import os
import time

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS PERSONNALISÉ POUR EMBELLIR LE TABLEAU ET AGRANDIR LE TEXTE
st.markdown("""
    <style>
        /* Agrandir la police du tableau */
        div[data-testid="stDataFrame"] div[data-testid="stTable"] {
            font-size: 1.2rem !important;
        }
        /* Agrandir les headers (Titres des colonnes) */
        div[data-testid="stDataFrame"] th {
            font-size: 1.3rem !important;
            background-color: #f0f2f6;
            color: #1f77b4;
        }
        /* Enlever les marges pour l'image d'intro */
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Style pour l'inspecteur */
        .inspecteur-box {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Vérifie si l'intro a déjà été montrée
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

# --- SÉCURITÉ : MOT DE PASSE ADMIN ---
st.sidebar.divider()
st.sidebar.markdown("### 🔒 Espace Ingénieur")
password = st.sidebar.text_input("Mot de passe Admin", type="password")

# On définit si l'utilisateur est admin ou pas
IS_ADMIN = False
if password == "Noria2026":  # <--- Change ton mot de passe ici !
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

# ==========================================
# VUE 1 : TABLEAU DE SUIVI GÉNÉRAL
# ==========================================
if choix_menu == "📊 Tableau de Suivi Général":
    st.title("📊 Tableau de Bord - Suivi 108 Villas")
    
    df = charger_donnees()

    # --- A. LE GRAND TABLEAU (D'ABORD) ---
    st.markdown("### 👁️ Vue Globale du Chantier")
    st.markdown("Usez de la barre de défilement en bas du tableau pour voir les 108 Villas.")

    # Fonction de couleur améliorée
    def colorer_cellules(val):
        color = 'white'
        border = '1px solid #eee'
        font_weight = 'normal'
        
        if val == 'OK':
            color = '#d4edda' # Vert clair
            font_weight = 'bold'
        elif val == 'Non Conforme':
            color = '#f8d7da' # Rouge clair
            font_weight = 'bold'
        elif val == 'En cours':
            color = '#fff3cd' # Jaune
            
        return f'background-color: {color}; border: {border}; font-weight: {font_weight}; color: black;'

    # Affichage du tableau avec hauteur agrandie pour lisibilité
    st.dataframe(
        df.style.applymap(colorer_cellules), 
        use_container_width=True, 
        height=500  # Tableau plus haut
    )

    st.divider()

    # --- B. L'INSPECTEUR INTELLIGENT (EN BAS) ---
    # On met ça dans un conteneur pour faire joli
    with st.container():
        st.markdown("""<div class="inspecteur-box"><h3>🔎 Inspecteur de Tâche & Validation</h3>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            villa_select = st.selectbox("Choisir la Villa :", LISTE_VILLAS)
        with c2:
            tache_select = st.selectbox("Choisir la Tâche :", LISTE_TACHES)

        # Récupération du statut actuel
        statut_actuel = df.at[tache_select, villa_select]
        
        st.markdown("---")
        
        col_docs, col_valid = st.columns([2, 1])

        # PARTIE GAUCHE : LES DOCUMENTS (Lecture pour tout le monde)
        with col_docs:
            st.markdown(f"#### 📂 Documents : {tache_select}")
            st.info(f"Preuves pour la {villa_select}")
            
            # Logique d'affichage des boutons
            if "Réception des axes" in tache_select:
                tabs = st.tabs(["📐 Archi", "🗺️ Topo"])
                with tabs[0]:
                    c_a, c_b = st.columns(2)
                    c_a.button(f"Voir Autocontrôle", key="auto_archi")
                    c_b.button(f"Voir PV Archi", key="pv_archi")
                with tabs[1]:
                    st.button(f"Voir Scan Topo", key="scan_topo")

            elif "fond de fouille" in tache_select:
                 st.button(f"📄 Voir le Document Unique", key="doc_fouile")

            elif "semelles" in tache_select:
                c_a, c_b = st.columns(2)
                c_a.button(f"Voir Autocontrôle", key="auto_sem")
                c_b.button(f"Voir PV Réception", key="pv_sem")
            
            else:
                st.write("Pas de documents configurés.")

        # PARTIE DROITE : LA VALIDATION (Réservée à l'ADMIN)
        with col_valid:
            st.markdown("#### ✅ Validation")
            
            if IS_ADMIN:
                # Si tu as mis le mot de passe : Tu vois les boutons pour modifier
                options_statut = ["À faire", "En cours", "OK", "Non Conforme"]
                index_statut = 0
                if statut_actuel in options_statut:
                    index_statut = options_statut.index(statut_actuel)
                
                nouveau_statut = st.radio("Changer l'état :", options_statut, index=index_statut)
                
                if nouveau_statut != statut_actuel:
                    df.at[tache_select, villa_select] = nouveau_statut
                    sauvegarder(df)
                    st.success("Statut mis à jour !")
                    time.sleep(0.5)
                    st.rerun()
            else:
                # Si c'est le Boss (pas de mot de passe) : Il voit juste le texte
                st.markdown(f"Statut actuel : **{statut_actuel}**")
                
                # Petite logique visuelle pour le boss
                if statut_actuel == "OK":
                    st.markdown("🟢 **VALIDÉ**")
                elif statut_actuel == "Non Conforme":
                    st.markdown("🔴 **NON CONFORME**")
                else:
                    st.markdown("⚪ En attente")
                    
                st.caption("🔒 Modification réservée à l'ingénieur")

        st.markdown("</div>", unsafe_allow_html=True) # Fin de la boite


# ==========================================
# VUE 2 & 3 (Restent pareilles pour l'instant)
# ==========================================
elif choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage Chantier")
    st.write("Section en construction...")

elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers")
    st.write("Section en construction...")