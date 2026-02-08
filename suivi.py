import streamlit as st
import time

# --- 0. CONFIGURATION DE LA PAGE & INTRO ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# Intro (Animation de bienvenue)
if "intro_complete" not in st.session_state:
    intro_placeholder = st.empty()
    with intro_placeholder.container():
        st.image("noria.jpg", use_container_width=True)
    time.sleep(2)
    with st.spinner("Chargement de l'espace projet..."):
        time.sleep(1.0)
    intro_placeholder.empty()
    st.toast("Bienvenue sur le projet Noria !", icon="🏗️")
    st.session_state["intro_complete"] = True

# --- 1. CONFIGURATION DES LISTES ---
LISTE_VILLAS = [f"Villa {i}" for i in range(1, 109)]
LISTE_TACHES = [
    "1. Réception des axes",
    "2. Réception fond de fouille",
    "3. Réception coffrage et ferraillage semelles",
    "4. Réception béton des semelles (Labo)"
]

# --- 2. BARRE LATÉRALE ---
st.sidebar.title("🗂️ Navigation")

st.sidebar.divider()
st.sidebar.markdown("### 🔒 Espace Ingénieur")
password = st.sidebar.text_input("Mot de passe Admin", type="password")

if password == "Noria2026": 
    st.sidebar.success("Accès Autorisé ✅")
else:
    st.sidebar.info("Mode Consultation 👀")

st.sidebar.divider()

# Menu simplifié sans le Tableau de Bord
choix_menu = st.sidebar.radio(
    "Aller vers :",
    ["📁 Dossier de démarrage", "📂 Suivi de chaque tâche"]
)

# --- 3. AFFICHAGE PRINCIPAL ---

# OPTION 1 : DOSSIER DE DÉMARRAGE
if choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage")
    st.info("Consultez ici les documents administratifs et techniques globaux du projet.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Documents Administratifs")
        st.write("- Permis de construire")
        st.write("- PV d'installation de chantier")
        st.write("- Assurances RC / Décennale")
    
    with col2:
        st.subheader("📐 Plans Généraux")
        st.write("- Plan de masse")
        st.write("- Plan de situation")
        st.write("- Rapport géotechnique (G2)")

# OPTION 2 : SUIVI PAR TÂCHE / VILLA
elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers")
    st.write("Naviguez dans l'arborescence technique par villa et par étape.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        folder_tache = st.selectbox("Sélectionnez la tâche :", LISTE_TACHES)
    with col_b:
        folder_villa = st.selectbox("Sélectionnez la villa :", LISTE_VILLAS)
    
    st.divider()
    st.markdown(f"### 📍 Emplacement : `{folder_tache}` > `{folder_villa}`")
    
    # Simulation de l'arborescence des fichiers
    st.markdown("#### 📂 Documents disponibles")
    
    if "Réception des axes" in folder_tache:
        st.info("📑 **Sous-dossier Archi** : [Autocontrôle.pdf] | [PV.pdf]")
        st.info("📐 **Sous-dossier Topo** : [Scan_Topo.pdf]")
    elif "semelles" in folder_tache:
        st.info("📄 **Documents Techniques** : [Ferraillage_Approuvé.pdf] | [PV_Reception.pdf]")
        st.info("🧪 **Laboratoire** : [Essai_Béton.pdf]")
    else:
        st.info("📄 **Document** : [Fiche_Controle_Unique.pdf]")

    # Zone de dépôt pour l'admin
    if password == "Noria2026":
        st.divider()
        st.subheader("📤 Ajouter un document")
        st.file_uploader(f"Télécharger un fichier pour {folder_villa}", type=["pdf", "jpg", "png"])