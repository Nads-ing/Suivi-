import streamlit as st
import pandas as pd
import time
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Suivi Chantier Noria", layout="wide")

# --- INTRO ---
if "intro_complete" not in st.session_state:
    intro_placeholder = st.empty()
    with intro_placeholder.container():
        if os.path.exists("noria.jpg"):
            st.image("noria.jpg", use_container_width=True)
    time.sleep(2)
    with st.spinner("Chargement de l'espace projet..."):
        time.sleep(1.0)
    intro_placeholder.empty()
    st.toast("Bienvenue sur le projet Noria !", icon="🏗️")
    st.session_state["intro_complete"] = True

# --- INITIALISATION DES DONNÉES ---
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "Tableau de suivi général"

if "statuts" not in st.session_state:
    # Statuts pour chaque tâche × villa (par défaut : "Pas encore")
    taches = [
        "Réception des axes",
        "Réception ferraillage fond de fouille",
        "Réception coffrage et ferraillage des semelles",
        "Réception béton des semelles par le labo"
    ]
    villas = [f"Villa {i}" for i in range(1, 109)]
    st.session_state.statuts = {
        tache: {villa: "Pas encore" for villa in villas} for tache in taches
    }

if "documents" not in st.session_state:
    # Stockage des documents uploadés
    st.session_state.documents = {}

if "selected_cell" not in st.session_state:
    st.session_state.selected_cell = None

# --- DÉFINITIONS ---
TACHES = [
    "Réception des axes",
    "Réception ferraillage fond de fouille",
    "Réception coffrage et ferraillage des semelles",
    "Réception béton des semelles par le labo"
]

VILLAS = [f"Villa {i}" for i in range(1, 109)]

STRUCTURES = ["Dallage", "Longrines", "Poteaux", "Semelles"]

# --- SIDEBAR (MENU GAUCHE) ---
with st.sidebar:
    st.title("📋 Navigation")
    
    if st.button("📊 Tableau de suivi général", use_container_width=True, type="primary" if st.session_state.selected_menu == "Tableau de suivi général" else "secondary"):
        st.session_state.selected_menu = "Tableau de suivi général"
        st.rerun()
    
    if st.button("🚀 Dossier de démarrage de chantier", use_container_width=True, type="primary" if st.session_state.selected_menu == "Dossier de démarrage de chantier" else "secondary"):
        st.session_state.selected_menu = "Dossier de démarrage de chantier"
        st.rerun()
    
    if st.button("📁 Suivi de chaque tâche", use_container_width=True, type="primary" if st.session_state.selected_menu == "Suivi de chaque tâche" else "secondary"):
        st.session_state.selected_menu = "Suivi de chaque tâche"
        st.rerun()

# --- ZONE PRINCIPALE (DROITE) ---
st.title(st.session_state.selected_menu)

# ============================================
# === 1. TABLEAU DE SUIVI GÉNÉRAL ===
# ============================================
if st.session_state.selected_menu == "Tableau de suivi général":
    
    st.markdown("### 📊 Tableau de suivi général - Cliquez sur une cellule pour gérer les documents")
    
    # Créer le dataframe
    df_data = []
    for tache in TACHES:
        row = [tache]
        for villa in VILLAS:
            statut = st.session_state.statuts[tache][villa]
            row.append(statut)
        df_data.append(row)
    
    df = pd.DataFrame(df_data, columns=["Tâche"] + VILLAS)
    
    # Afficher le tableau avec styling
    st.dataframe(
        df.style.applymap(
            lambda x: 'background-color: #90EE90' if x == "OK" else 'background-color: #FFB6C1' if x == "Pas encore" else '',
            subset=VILLAS
        ),
        use_container_width=True,
        height=300
    )
    
    st.markdown("---")
    
    # === SÉLECTION CELLULE ===
    st.markdown("### 🔍 Gestion d'une cellule")
    
    col1, col2 = st.columns(2)
    with col1:
        tache_selectionnee = st.selectbox("📌 Sélectionner une tâche :", TACHES)
    with col2:
        villa_selectionnee = st.selectbox("🏠 Sélectionner une villa :", VILLAS)
    
    # Clé unique pour cette cellule
    cell_key = f"{tache_selectionnee}|||{villa_selectionnee}"
    
    st.markdown(f"#### 📋 **{tache_selectionnee}** - **{villa_selectionnee}**")
    
    # Afficher le statut actuel
    statut_actuel = st.session_state.statuts[tache_selectionnee][villa_selectionnee]
    
    col_stat, col_btn = st.columns([3, 1])
    with col_stat:
        st.info(f"**Statut actuel :** {statut_actuel}")
    with col_btn:
        if st.button("🔄 Changer statut"):
            if statut_actuel == "OK":
                st.session_state.statuts[tache_selectionnee][villa_selectionnee] = "Pas encore"
            else:
                st.session_state.statuts[tache_selectionnee][villa_selectionnee] = "OK"
            st.rerun()
    
    st.markdown("---")
    
    # === DOCUMENTS SELON LA TÂCHE ===
    st.markdown("### 📄 Documents associés")
    
    # Initialiser le stockage pour cette cellule
    if cell_key not in st.session_state.documents:
        st.session_state.documents[cell_key] = {}
    
    # === TÂCHE 1 : Réception des axes ===
    if tache_selectionnee == "Réception des axes":
        tab1, tab2 = st.tabs(["📐 ARCHI", "📏 TOPO"])
        
        with tab1:
            st.markdown("#### Archi - Choisir le type")
            doc_type_archi = st.radio("", ["Autocontrôle", "PV"], key="radio_archi_axes")
            
            doc_key = f"archi_{doc_type_archi}"
            
            uploaded = st.file_uploader(
                f"📤 Uploader {doc_type_archi}", 
                type=["pdf", "png", "jpg", "jpeg"],
                key=f"upload_{cell_key}_archi_{doc_type_archi}"
            )
            
            if uploaded:
                st.session_state.documents[cell_key][doc_key] = uploaded
                st.success(f"✅ {doc_type_archi} uploadé : {uploaded.name}")
            
            if doc_key in st.session_state.documents[cell_key]:
                st.download_button(
                    f"⬇️ Télécharger {doc_type_archi}",
                    data=st.session_state.documents[cell_key][doc_key],
                    file_name=st.session_state.documents[cell_key][doc_key].name
                )
        
        with tab2:
            st.markdown("#### Topo - Scan")
            
            uploaded_topo = st.file_uploader(
                "📤 Uploader scan Topo", 
                type=["pdf", "png", "jpg", "jpeg"],
                key=f"upload_{cell_key}_topo"
            )
            
            if uploaded_topo:
                st.session_state.documents[cell_key]["topo"] = uploaded_topo
                st.success(f"✅ Topo uploadé : {uploaded_topo.name}")
            
            if "topo" in st.session_state.documents[cell_key]:
                st.download_button(
                    "⬇️ Télécharger Topo",
                    data=st.session_state.documents[cell_key]["topo"],
                    file_name=st.session_state.documents[cell_key]["topo"].name
                )
    
    # === TÂCHE 2 : Réception ferraillage fond de fouille ===
    elif tache_selectionnee == "Réception ferraillage fond de fouille":
        st.markdown("#### Document unique")
        
        uploaded = st.file_uploader(
            "📤 Uploader le document", 
            type=["pdf", "png", "jpg", "jpeg"],
            key=f"upload_{cell_key}_doc"
        )
        
        if uploaded:
            st.session_state.documents[cell_key]["document"] = uploaded
            st.success(f"✅ Document uploadé : {uploaded.name}")
        
        if "document" in st.session_state.documents[cell_key]:
            st.download_button(
                "⬇️ Télécharger Document",
                data=st.session_state.documents[cell_key]["document"],
                file_name=st.session_state.documents[cell_key]["document"].name
            )
    
    # === TÂCHE 3 : Réception coffrage et ferraillage des semelles ===
    elif tache_selectionnee == "Réception coffrage et ferraillage des semelles":
        st.markdown("#### Choisir la structure puis le type de document")
        
        structure = st.selectbox("🏗️ Sélectionner la structure :", STRUCTURES, key="struct_tache3")
        
        doc_type = st.radio("Type de document :", ["Autocontrôle", "PV"], key="radio_tache3")
        
        doc_key = f"{structure}_{doc_type}"
        
        uploaded = st.file_uploader(
            f"📤 Uploader {doc_type} - {structure}", 
            type=["pdf", "png", "jpg", "jpeg"],
            key=f"upload_{cell_key}_{structure}_{doc_type}"
        )
        
        if uploaded:
            st.session_state.documents[cell_key][doc_key] = uploaded
            st.success(f"✅ {doc_type} - {structure} uploadé : {uploaded.name}")
        
        if doc_key in st.session_state.documents[cell_key]:
            st.download_button(
                f"⬇️ Télécharger {doc_type} - {structure}",
                data=st.session_state.documents[cell_key][doc_key],
                file_name=st.session_state.documents[cell_key][doc_key].name
            )
        
        # Afficher tous les documents uploadés pour cette cellule
        if st.session_state.documents[cell_key]:
            st.markdown("##### 📚 Documents uploadés pour cette cellule :")
            for key in st.session_state.documents[cell_key]:
                st.text(f"✓ {key}")
    
    # === TÂCHE 4 : Réception béton des semelles par le labo ===
    elif tache_selectionnee == "Réception béton des semelles par le labo":
        st.markdown("#### Choisir la structure puis le type de document")
        
        structure = st.selectbox("🏗️ Sélectionner la structure :", STRUCTURES, key="struct_tache4")
        
        doc_type = st.radio("Type de document :", ["Autocontrôle", "PV"], key="radio_tache4")
        
        doc_key = f"{structure}_{doc_type}"
        
        uploaded = st.file_uploader(
            f"📤 Uploader {doc_type} - {structure}", 
            type=["pdf", "png", "jpg", "jpeg"],
            key=f"upload_{cell_key}_{structure}_{doc_type}"
        )
        
        if uploaded:
            st.session_state.documents[cell_key][doc_key] = uploaded
            st.success(f"✅ {doc_type} - {structure} uploadé : {uploaded.name}")
        
        if doc_key in st.session_state.documents[cell_key]:
            st.download_button(
                f"⬇️ Télécharger {doc_type} - {structure}",
                data=st.session_state.documents[cell_key][doc_key],
                file_name=st.session_state.documents[cell_key][doc_key].name
            )
        
        # Afficher tous les documents uploadés pour cette cellule
        if st.session_state.documents[cell_key]:
            st.markdown("##### 📚 Documents uploadés pour cette cellule :")
            for key in st.session_state.documents[cell_key]:
                st.text(f"✓ {key}")

# ============================================
# === 2. DOSSIER DE DÉMARRAGE ===
# ============================================
elif st.session_state.selected_menu == "Dossier de démarrage de chantier":
    st.info("🚀 Section en cours de développement")
    st.write("Cette section contiendra les documents de démarrage du chantier (non liée au tableau).")
    
    st.markdown("### 📤 Upload de documents de démarrage")
    uploaded_demarrage = st.file_uploader(
        "Uploader des documents de démarrage", 
        type=["pdf", "png", "jpg", "jpeg", "docx"],
        accept_multiple_files=True
    )
    
    if uploaded_demarrage:
        st.success(f"✅ {len(uploaded_demarrage)} document(s) uploadé(s)")
        for doc in uploaded_demarrage:
            st.write(f"- {doc.name}")

# ============================================
# === 3. SUIVI DE CHAQUE TÂCHE (ARBORESCENCE) ===
# ============================================
elif st.session_state.selected_menu == "Suivi de chaque tâche":
    st.markdown("### 📁 Arborescence des dossiers (même contenu que le tableau)")
    
    # Sélection de la tâche
    tache = st.selectbox("📌 Sélectionner une tâche :", TACHES)
    
    st.markdown(f"#### 📂 {tache}")
    
    # Sélection de la villa
    villa = st.selectbox("🏠 Sélectionner une villa :", VILLAS)
    
    st.markdown(f"#### 🏘️ {villa}")
    
    # Clé de la cellule
    cell_key = f"{tache}|||{villa}"
    
    # Afficher les documents selon la tâche
    st.markdown("---")
    st.markdown("### 📄 Documents disponibles")
    
    if cell_key in st.session_state.documents and st.session_state.documents[cell_key]:
        st.success(f"✅ Documents disponibles pour {tache} - {villa}")
        
        for doc_key, doc_file in st.session_state.documents[cell_key].items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 **{doc_key}** : {doc_file.name}")
            with col2:
                st.download_button(
                    "⬇️",
                    data=doc_file,
                    file_name=doc_file.name,
                    key=f"dl_{cell_key}_{doc_key}"
                )
    else:
        st.warning("⚠️ Aucun document uploadé pour cette combinaison tâche-villa")
        st.info("💡 Allez dans 'Tableau de suivi général' pour uploader des documents")
    
    # Afficher la structure pour tâches 3 et 4
    if tache in ["Réception coffrage et ferraillage des semelles", "Réception béton des semelles par le labo"]:
        st.markdown("---")
        st.markdown("#### 🏗️ Documents par structure")
        
        for structure in STRUCTURES:
            with st.expander(f"📁 {structure}"):
                docs_found = False
                if cell_key in st.session_state.documents:
                    for doc_key in st.session_state.documents[cell_key]:
                        if structure in doc_key:
                            docs_found = True
                            st.write(f"✓ {doc_key}")
                
                if not docs_found:
                    st.info("Aucun document pour cette structure")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)