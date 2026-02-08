import streamlit as st
import time
import os

# --- 0. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# CSS Minimaliste pour l'interface
st.markdown("""
    <style>
        .stAlert { margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# Intro
if "intro_complete" not in st.session_state:
    intro_placeholder = st.empty()
    with intro_placeholder.container():
        # Assure-toi que "noria.jpg" est bien dans le dossier du script
        try:
            st.image("noria.jpg", use_container_width=True)
        except:
            st.warning("Image 'noria.jpg' non trouvée.")
    time.sleep(2)
    with st.spinner("Chargement de l'espace documentaire..."):
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

choix_menu = st.sidebar.radio(
    "Accéder à :",
    ["📁 Dossier de démarrage", "📂 Suivi de chaque tâche"]
)

# --- 3. AFFICHAGE PRINCIPAL ---

# --- VUE : DOSSIER DE DÉMARRAGE ---
if choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Documents Administratifs")
        st.write("- [ ] Autorisation de construire")
        st.write("- [ ] PV d'ouverture de chantier")
        st.write("- [ ] Police d'assurance (TRC)")
        
    with col2:
        st.subheader("📐 Plans Généraux")
        st.write("- [ ] Plan de masse")
        st.write("- [ ] Plan d'implantation")
        st.write("- [ ] Rapport Géotechnique")

# --- VUE : EXPLORATEUR DE TÂCHES ---
elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers (Vue Arborescence)")
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        folder_tache = st.selectbox("Sélectionner la tâche :", LISTE_TACHES)
    with col_b:
        folder_villa = st.selectbox("Sélectionner la villa :", LISTE_VILLAS)
    
    st.info(f"📍 Chemin : **{folder_tache}** > **{folder_villa}**")
    
    st.markdown("### 📁 Documents disponibles")
    
    container = st.container(border=True)
    
    if "Réception des axes" in folder_tache:
        container.write("📄 **Sous-dossier Archi** : [Autocontrôle.pdf] | [PV.pdf]")
        container.write("📐 **Sous-dossier Topo** : [Scan_Topo.pdf]")
    elif "semelles" in folder_tache:
        container.write("📄 **Documents Techniques** : [Autocontrôle.pdf] | [PV Ferraillage.pdf] | [Fiche Béton.pdf]")
    else:
        container.write("📄 **Document Unique** : [Doc_Réception.pdf]")

    st.button("🔄 Actualiser les fichiers")