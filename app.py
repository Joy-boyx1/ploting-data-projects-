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
        # Lecture du fichier
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Définition des colonnes selon vos indications (Index 0-based)
        # G=6, J=9, N=13
        col_etat = "Etat"
        col_titre = df_aznag.columns[6]   # Colonne G
        col_budget = df_aznag.columns[9]  # Colonne J
        col_adjuge = df_aznag.columns[13] # Colonne N

        # Nettoyage global
        df_aznag = df_aznag.dropna(how='all')
        
        st.write("### 📋 Données complètes")
        st.dataframe(df_aznag, use_container_width=True)

        # Initialisation Session State
        if 'show_etat' not in st.session_state:
            st.session_state.show_etat = False
        if 'show_budget' not in st.session_state:
            st.session_state.show_budget = False

        # Boutons
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        with col_btn1:
            if st.button("Etat"):
                st.session_state.show_etat = not st.session_state.show_etat
        with col_btn2:
            if st.button("Ecart budgétaire"):
                st.session_state.show_budget = not st.session_state.show_budget

        # 1. ANALYSE ETAT
        if st.session_state.show_etat:
            if col_etat in df_aznag.columns:
                st.write("---")
                st.write(f"### 📈 Répartition par {col_etat}")
                df_clean_etat = df_aznag.dropna(subset=[col_etat])
                counts = df_clean_etat[col_etat].value_counts()
                percentages = (df_clean_etat[col_etat].value_counts(normalize=True) * 100)
                
                df_stats = pd.DataFrame({"Nombre": counts, "Pourcentage (%)": percentages.map("{:.2f}%".format)})
                
                c1, c2 = st.columns([1, 2])
                with c1: st.dataframe(df_stats, use_container_width=True)
                with c2:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", order=counts.index, ax=ax)
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

        # 2. ANALYSE ECART BUDGÉTAIRE (G, J, N)
        if st.session_state.show_budget:
            st.write("---")
            st.write(f"### 💰 Comparaison Budget ({col_budget}) vs Adjugé ({col_adjuge})")
            
            # Nettoyage : on garde les lignes où le titre existe et au moins un montant est > 0
            df_finance = df_aznag.dropna(subset=[col_titre])
            df_finance[col_budget] = pd.to_numeric(df_finance[col_budget], errors='coerce').fillna(0)
            df_finance[col_adjuge] = pd.to_numeric(df_finance[col_adjuge], errors='coerce').fillna(0)
            
            df_plot_data = df_finance[(df_finance[col_budget] > 0) | (df_finance[col_adjuge] > 0)].head(20)

            if not df_plot_data.empty:
                # Format long pour Seaborn
                df_melt = df_plot_data.melt(
                    id_vars=[col_titre], 
                    value_vars=[col_budget, col_adjuge],
                    var_name='Type', value_name='Montant'
                )

                fig2, ax2 = plt.subplots(figsize=(15, 6))
                sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                plt.xticks(rotation=45, ha='right')
                plt.title("Comparaison des montants par affaire (Top 20)")
                st.pyplot(fig2)
                
                # Affichage de l'écart calculé
                df_plot_data['Écart (J - N)'] = df_plot_data[col_budget] - df_plot_data[col_adjuge]
                st.dataframe(df_plot_data[[col_titre, col_budget, col_adjuge, 'Écart (J - N)']], use_container_width=True)
            else:
                st.warning("Aucune donnée financière valide trouvée dans les colonnes J et N.")

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
