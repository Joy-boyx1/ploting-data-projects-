import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration large
st.set_page_config(layout="wide")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

# Fonction de nettoyage universelle pour les montants
def clean_financial_value(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        # Retire DH, les espaces normaux et les espaces insécables (\xa0)
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    return float(value)

uploaded_file_aznag = st.file_uploader(
    "📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", 
    type=["xlsx"]
)

if uploaded_file_aznag:
    try:
        # 1. Lecture du fichier
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Définition des colonnes (A=0, G=6, J=9, N=13)
        col_exercice = df_aznag.columns[0]
        col_etat = "Etat"
        col_titre = df_aznag.columns[6]   # G
        col_budget = df_aznag.columns[9]  # J
        col_adjuge = df_aznag.columns[13] # N

        # 2. NETTOYAGE DES LIGNES VIDES (Image 1)
        # Supprime les lignes où l'exercice ou le titre est vide
        df_aznag = df_aznag.dropna(subset=[col_exercice, col_titre], how='all')

        # 3. GÉNÉRALISATION DU NETTOYAGE DES MONTANTS (Image 2)
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # --- SECTION FILTRE PAR EXERCICE ---
        exercices_disponibles = sorted(df_aznag[col_exercice].dropna().unique().astype(str), reverse=True)
        options_filtre = ["Tous"] + exercices_disponibles
        selected_year = st.selectbox("📅 Sélectionner l'EXERCICE :", options=options_filtre)

        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # Affichage des données
        st.write(f"### 📋 Données : {selected_year}")
        st.dataframe(df_filtered, use_container_width=True)

        # --- GESTION DES BOUTONS ---
        if 'show_etat' not in st.session_state: st.session_state.show_etat = False
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False

        c_btn1, c_btn2, _ = st.columns([1, 1, 4])
        with c_btn1:
            if st.button("Etat"): st.session_state.show_etat = not st.session_state.show_etat
        with c_btn2:
            if st.button("Ecart budgétaire"): st.session_state.show_budget = not st.session_state.show_budget

        # 4. ANALYSE ETAT
        if st.session_state.show_etat:
            st.write("---")
            df_clean_etat = df_filtered.dropna(subset=[col_etat])
            counts = df_clean_etat[col_etat].value_counts()
            df_stats = pd.DataFrame({"Nombre": counts, "Pourcentage": (counts/counts.sum()*100).round(2)})
            
            c1, c2 = st.columns([1, 2])
            with c1: st.dataframe(df_stats, use_container_width=True)
            with c2:
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", ax=ax)
                st.pyplot(fig)

        # 5. ANALYSE ECART BUDGÉTAIRE
        if st.session_state.show_budget:
            st.write("---")
            # On ne garde que les lignes avec des montants significatifs
            df_plot_data = df_filtered[(df_filtered[col_budget] > 0) | (df_filtered[col_adjuge] > 0)].head(20)

            if not df_plot_data.empty:
                df_melt = df_plot_data.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig2, ax2 = plt.subplots(figsize=(15, 6))
                sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig2)
                
                df_plot_data['Écart'] = (df_plot_data[col_budget] - df_plot_data[col_adjuge]).round(2)
                st.write("**Détails financiers (Chiffres uniquement) :**")
                st.dataframe(df_plot_data[[col_titre, col_budget, col_adjuge, 'Écart']], use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
