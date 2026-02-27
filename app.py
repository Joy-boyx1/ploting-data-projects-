import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuration de la page en mode large
st.set_page_config(layout="wide")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

# 1. Upload du fichier
uploaded_file_aznag = st.file_uploader(
    "📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", 
    type=["xlsx"]
)

if uploaded_file_aznag:
    try:
        # 2. Lecture et nettoyage global
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Noms des colonnes cibles
        col_etat = "Etat"
        col_titre = "Intitulé affaire"
        col_budget = "Montant Budgetisé"
        col_adjuge = "Montant Adjugé"

        # Nettoyage de base (on retire les lignes totalement vides)
        df_aznag = df_aznag.dropna(how='all')
        
        # 3. Affichage du tableau de données principal
        st.write("### 📋 Données complètes")
        st.dataframe(df_aznag, use_container_width=True)

        # --- INITIALISATION DES ÉTATS (SESSION STATE) ---
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
        # 4. ANALYSE : ETAT
        # ---------------------------------------------------------
        if st.session_state.show_etat:
            if col_etat in df_aznag.columns:
                st.write("---")
                st.write(f"### 📈 Analyse par {col_etat}")
                
                df_clean_etat = df_aznag.dropna(subset=[col_etat])
                counts = df_clean_etat[col_etat].value_counts()
                percentages = (df_clean_etat[col_etat].value_counts(normalize=True) * 100)
                
                df_stats = pd.DataFrame({
                    "Nombre": counts,
                    "Pourcentage (%)": percentages.map("{:.2f}%".format)
                })
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.dataframe(df_stats, use_container_width=True)
                with c2:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", order=counts.index, ax=ax)
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
            else:
                st.error(f"❌ Colonne '{col_etat}' introuvable.")

        # ---------------------------------------------------------
        # 5. ANALYSE : ECART BUDGÉTAIRE
        # ---------------------------------------------------------
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💰 Comparaison Budget vs Adjugé")
            
            # Vérification des colonnes nécessaires
            needed = [col_titre, col_budget, col_adjuge]
            if all(c in df_aznag.columns for c in needed):
                
                # Filtrer pour n'avoir que les lignes avec des montants (non nuls et non vides)
                df_finance = df_aznag.dropna(subset=[col_budget, col_adjuge])
                df_finance = df_finance[(df_finance[col_budget] > 0) | (df_finance[col_adjuge] > 0)]
                
                if not df_finance.empty:
                    # Préparation des données pour le format "long" (nécessaire pour seaborn barplot groupé)
                    # On ne garde que les 15 premières pour la lisibilité si le tableau est trop grand
                    df_plot = df_finance.head(20).melt(
                        id_vars=[col_titre], 
                        value_vars=[col_budget, col_adjuge],
                        var_name='Type de Montant', 
                        value_name='Valeur'
                    )

                    fig2, ax2 = plt.subplots(figsize=(15, 6))
                    sns.barplot(data=df_plot, x=col_titre, y='Valeur', hue='Type de Montant', ax=ax2, palette=["#3498db", "#e74c3c"])
                    
                    plt.title("Comparaison par Affaire (Top 20 lignes)")
                    plt.xticks(rotation=45, ha='right')
                    plt.ylabel("Montant (DH)")
                    plt.xlabel("Affaires")
                    plt.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    st.pyplot(fig2)
                    
                    # Petit tableau des écarts
                    df_finance['Ecart'] = df_finance[col_budget] - df_finance[col_adjuge]
                    st.write("**Détails des montants :**")
                    st.dataframe(df_finance[[col_titre, col_budget, col_adjuge, 'Ecart']], use_container_width=True)
                else:
                    st.warning("⚠️ Aucune donnée chiffrée n'a été trouvée pour comparer les budgets.")
            else:
                st.error("❌ Les colonnes budgétaires sont manquantes (Vérifiez les noms : 'Intitulé affaire', 'Montant Budgetisé', 'Montant Adjugé')")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
