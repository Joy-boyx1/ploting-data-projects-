import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration large
st.set_page_config(layout="wide")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

uploaded_file_aznag = st.file_uploader(
    "📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", 
    type=["xlsx"]
)

if uploaded_file_aznag:
    try:
        # 1. Lecture du fichier
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Définition des colonnes
        col_exercice = df_aznag.columns[0] # Colonne A
        col_etat = "Etat"
        col_titre = df_aznag.columns[6]   # Colonne G
        col_budget = df_aznag.columns[9]  # Colonne J
        col_adjuge = df_aznag.columns[13] # Colonne N

        # Nettoyage global
        df_aznag = df_aznag.dropna(how='all')

        # --- SECTION FILTRE PAR EXERCICE ---
        exercices_disponibles = sorted(df_aznag[col_exercice].dropna().unique().astype(str), reverse=True)
        options_filtre = ["Tous"] + exercices_disponibles
        selected_year = st.selectbox("📅 Sélectionner l'EXERCICE (Colonne A) :", options=options_filtre)

        if selected_year != "Tous":
            df_filtered = df_aznag[df_aznag[col_exercice].astype(str) == selected_year]
        else:
            df_filtered = df_aznag

        # 2. Affichage du tableau de données
        st.write(f"### 📋 Données : {selected_year}")
        st.dataframe(df_filtered, use_container_width=True)

        # --- INITIALISATION SESSION STATE ---
        if 'show_etat' not in st.session_state:
            st.session_state.show_etat = False
        if 'show_budget' not in st.session_state:
            st.session_state.show_budget = False

        # --- BARRE DE BOUTONS ---
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        with col_btn1:
            if st.button("Etat"):
                st.session_state.show_etat = not st.session_state.show_etat
        with col_btn2:
            if st.button("Ecart budgétaire"):
                st.session_state.show_budget = not st.session_state.show_budget

        # ---------------------------------------------------------
        # 3. ANALYSE : ETAT (Montants en chiffres uniquement)
        # ---------------------------------------------------------
        if st.session_state.show_etat:
            if col_etat in df_filtered.columns:
                st.write("---")
                st.write(f"### 📈 Répartition par Etat ({selected_year})")
                df_clean_etat = df_filtered.dropna(subset=[col_etat])
                counts = df_clean_etat[col_etat].value_counts()
                percentages = (df_clean_etat[col_etat].value_counts(normalize=True) * 100)
                
                # ICI : On garde uniquement les chiffres arrondis
                df_stats = pd.DataFrame({
                    "Nombre": counts, 
                    "Pourcentage": percentages.round(2)  # Juste le chiffre
                })
                
                c1, c2 = st.columns([1, 2])
                with c1: 
                    st.dataframe(df_stats, use_container_width=True)
                with c2:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", order=counts.index, ax=ax)
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

        # ---------------------------------------------------------
        # 4. ANALYSE : ECART BUDGÉTAIRE
        # ---------------------------------------------------------
        if st.session_state.show_budget:
            st.write("---")
            st.write(f"### 💰 Budget vs Adjugé ({selected_year})")
            
            df_fin = df_filtered.copy()
            df_fin[col_budget] = pd.to_numeric(df_fin[col_budget], errors='coerce').fillna(0)
            df_fin[col_adjuge] = pd.to_numeric(df_fin[col_adjuge], errors='coerce').fillna(0)
            
            df_plot_data = df_fin[(df_fin[col_budget] > 0) | (df_fin[col_adjuge] > 0)].head(20)

            if not df_plot_data.empty:
                df_melt = df_plot_data.melt(
                    id_vars=[col_titre], 
                    value_vars=[col_budget, col_adjuge],
                    var_name='Type', value_name='Montant'
                )

                fig2, ax2 = plt.subplots(figsize=(15, 6))
                sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig2)
                
                # Écart en chiffres
                df_plot_data['Écart'] = (df_plot_data[col_budget] - df_plot_data[col_adjuge]).round(2)
                st.write("**Détails des montants (chiffres) :**")
                st.dataframe(df_plot_data[[col_titre, col_budget, col_adjuge, 'Écart']], use_container_width=True)
            else:
                st.warning("Aucune donnée budgétaire disponible.")

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
