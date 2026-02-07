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
    
    time.sleep(2)
    with st.spinner("Chargement du tableau de bord..."):
        time.sleep(1.5)
    intro_placeholder.empty()
    st.toast("Bienvenue sur le projet Noria !", icon="🏗️")
    st.session_state["intro_complete"] = True

# --- 1. CONFIGURATION DES DONNÉES ---
FICHIER_DONNEES = "mon_suivi_general.csv"

# Création automatique des 108 Villas
LISTE_VILLAS = [f"Villa {i}" for i in range(1, 109)]

# Tes tâches exactes
LISTE_TACHES = [
    "1. Réception des axes",
    "2. Réception fond de fouille",
    "3. Réception coffrage et ferraillage semelles",
    "4. Réception béton des semelles (Labo)"
]

# --- 2. FONCTIONS (Le Cerveau) ---
def charger_donnees():
    """Charge un grand tableau : Lignes=Tâches, Colonnes=Villas"""
    if os.path.exists(FICHIER_DONNEES):
        df = pd.read_csv(FICHIER_DONNEES, index_col=0)
    else:
        # Création de la matrice vide (Tâches x Villas)
        df = pd.DataFrame(index=LISTE_TACHES, columns=LISTE_VILLAS)
        df = df.fillna("À faire") # On remplit tout avec "À faire"
        df.to_csv(FICHIER_DONNEES)
    return df

def sauvegarder(df):
    df.to_csv(FICHIER_DONNEES)

# --- 3. BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.title("🗂️ Navigation")
choix_menu = st.sidebar.radio(
    "Aller vers :",
    ["📊 Tableau de Suivi Général", "📁 Dossier de démarrage", "📂 Suivi de chaque tâche"]
)

# --- 4. AFFICHAGE PRINCIPAL ---

# ==========================================
# VUE 1 : TABLEAU DE SUIVI GÉNÉRAL (LE COEUR)
# ==========================================
if choix_menu == "📊 Tableau de Suivi Général":
    st.title("📊 Tableau de Bord - Suivi 108 Villas")
    
    # Chargement du grand tableau
    df = charger_donnees()

    # --- A. L'INSPECTEUR INTELLIGENT (La zone d'action) ---
    st.markdown("### 🔎 Inspecteur de Tâche")
    st.info("Sélectionnez une Villa et une Tâche pour voir les preuves et valider.")

    c1, c2 = st.columns(2)
    with c1:
        # Sélecteur de Villa
        villa_select = st.selectbox("Choisir la Villa :", LISTE_VILLAS)
    with c2:
        # Sélecteur de Tâche
        tache_select = st.selectbox("Choisir la Tâche :", LISTE_TACHES)

    # Récupération du statut actuel
    statut_actuel = df.at[tache_select, villa_select]
    
    st.divider()

    # --- B. LOGIQUE INTELLIGENTE (Selon la tâche choisie) ---
    # C'est ici que le site décide quels boutons afficher
    
    col_action, col_statut = st.columns([2, 1])

    with col_action:
        st.markdown(f"**Documents pour : {tache_select} / {villa_select}**")
        
        # CAS 1 : Réception des AXES (Archi ou Topo)
        if "Réception des axes" in tache_select:
            type_doc = st.radio("Type de document :", ["Archi", "Topo"], horizontal=True)
            
            if type_doc == "Archi":
                c_a, c_b = st.columns(2)
                c_a.button(f"📂 Voir Autocontrôle ({villa_select})")
                c_b.button(f"📄 Voir PV Archi ({villa_select})")
            else:
                st.button(f"📐 Voir Scan Topo ({villa_select})")

        # CAS 2 : Fond de fouille (Document unique)
        elif "fond de fouille" in tache_select:
             st.button(f"📄 Voir le Document Unique ({villa_select})")

        # CAS 3 & 4 : Semelles (Coffrage/Ferraillage OU Béton) -> Auto + PV
        elif "semelles" in tache_select:
            c_a, c_b = st.columns(2)
            c_a.button(f"📂 Voir Autocontrôle ({villa_select})")
            c_b.button(f"📄 Voir PV Réception ({villa_select})")
        
        else:
            st.write("Pas de documents configurés pour cette étape.")

    with col_statut:
        st.markdown("**Validation**")
        # Changement de couleur/statut
        options_statut = ["À faire", "OK", "Non Conforme"]
        # On gère le cas où le statut n'est pas dans la liste
        index_statut = 0
        if statut_actuel in options_statut:
            index_statut = options_statut.index(statut_actuel)
            
        nouveau_statut = st.radio("Statut :", options_statut, index=index_statut, key="statut_radio")
        
        if nouveau_statut != statut_actuel:
            df.at[tache_select, villa_select] = nouveau_statut
            sauvegarder(df)
            st.success("Enregistré !")
            time.sleep(0.5)
            st.rerun()

    st.divider()

    # --- C. LE GRAND TABLEAU VISUEL ---
    st.markdown("### 👁️ Vue Globale")
    # On affiche le tableau. On colore les cases "OK" en vert automatiquement via Pandas style
    def colorer_cellules(val):
        color = 'white'
        if val == 'OK':
            color = '#d4edda' # Vert clair
        elif val == 'Non Conforme':
            color = '#f8d7da' # Rouge clair
        return f'background-color: {color}'

    st.dataframe(df.style.applymap(colorer_cellules), use_container_width=True, height=400)


# ==========================================
# VUE 2 : DOSSIER DÉMARRAGE
# ==========================================
elif choix_menu == "📁 Dossier de démarrage":
    st.title("📁 Dossier de Démarrage Chantier")
    st.write("Ici, tu mettras tes plans généraux, autorisations, etc.")
    # Exemple de structure
    st.file_uploader("Ajouter un document au dossier démarrage")
    st.markdown("- 📄 Plan de masse.pdf")
    st.markdown("- 📄 Autorisation de construire.pdf")


# ==========================================
# VUE 3 : SUIVI DE CHAQUE TÂCHE (VUE DOSSIER)
# ==========================================
elif choix_menu == "📂 Suivi de chaque tâche":
    st.title("📂 Explorateur de Dossiers")
    st.write("C'est ici que tu navigues manuellement dans les dossiers si besoin.")
    
    tache_folder = st.selectbox("Choisir le dossier Tâche :", LISTE_TACHES)
    villa_folder = st.selectbox("Choisir la Villa :", LISTE_VILLAS)
    
    st.markdown(f"### 📂 Contenu de : {tache_folder} > {villa_folder}")
    
    # Ici, on simulera l'affichage des fichiers
    st.info("Les fichiers validés dans le Tableau Général apparaissent ici.")