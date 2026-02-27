import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page en mode large pour utiliser tout l'espace horizontal
st.set_page_config(layout="wide", page_title="Dashboard AZNAG")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

# --- FONCTION DE NETTOYAGE GÉNÉRALISÉE ---
def clean_financial_value(value):
    """Nettoie les montants : retire 'DH', les espaces et convertit en nombre."""
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        # Nettoyage des caractères parasites (DH, espaces, espaces insécables)
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    return float(value)

# --- CHARGEMENT DU FICHIER ---
uploaded_file_aznag = st.file_uploader(
    "📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", 
    type=["xlsx"]
)

if uploaded_file_aznag:
    try:
        # 1. Lecture initiale
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Définition des colonnes cibles par index
        col_exercice = df_aznag.columns[0]  # A (Exercice)
        col_sites    = df_aznag.columns[2]  # C (Sites)
        col_etat     = "Etat"               # Colonne nommée "Etat"
        col_titre    = df_aznag.columns[6]  # G (Intitulé affaire)
        col_budget   = df_aznag.columns[9]  # J (Montant Budgetisé)
        col_adjuge   = df_aznag.columns[13] # N (Montant Adjugé)

        # 2. NETTOYAGE DES LIGNES (Supprime les lignes "None" visibles sur vos captures)
        # On garde les lignes où l'exercice et l'intitulé ne sont pas vides
        df_aznag = df_aznag.dropna(subset=[col_exercice, col_titre], how='all')

        # 3. NETTOYAGE DES MONTANTS (Généralisé J et N)
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # --- FILTRE GÉNÉRAL : EXERCICE (Colonne A) ---
        exercices_dispo = sorted(df_aznag[col_exercice].dropna().unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Sélectionner l'EXERCICE :", options=["Tous"] + exercices_dispo)

        # Application du filtre exercice
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # Affichage du tableau de données principal (Largeur complète)
        st.write(f"### 📋 Données : {selected_year}")
        st.dataframe(df_filtered, use_container_width=True)

        # --- GESTION DES BOUTONS (Session State) ---
        if 'show_etat' not in st.session_state: st.session_state.show_etat = False
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False

        c_btn1, c_btn2, _ = st.columns([1, 1, 4])
        with c_btn1:
            if st.button("Etat"):
                st.session_state.show_etat = not st.session_state.show_etat
        with c_btn2:
            if st.button("Ecart budgétaire"):
                st.session_state.show_budget = not st.session_state.show_budget

        # ---------------------------------------------------------
        # 4. BLOC ANALYSE : ETAT
        # ---------------------------------------------------------
        if st.session_state.show_etat:
            st.write("---")
            st.write(f"### 📈 Répartition par Etat ({selected_year})")
            
            df_clean_etat = df_filtered.dropna(subset=[col_etat])
            counts = df_clean_etat[col_etat].value_counts()
            
            # Tableau des statistiques (chiffres uniquement)
            df_stats = pd.DataFrame({
                "Nombre": counts, 
                "Pourcentage": (counts / counts.sum() * 100).round(2)
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
        # 5. BLOC ANALYSE : ECART BUDGÉTAIRE + FILTRE SITE
        # ---------------------------------------------------------
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💰 Comparaison Budget vs Adjugé")
            
            # Sous-filtre par Site (Colonne C)
            sites_dispo = sorted(df_filtered[col_sites].dropna().unique().astype(str))
            selected_site = st.selectbox("📍 Filtrer par Site (Colonne C) :", options=["Tous les sites"] + sites_dispo)
            
            df_budget_base = df_filtered.copy()
            if selected_site != "Tous les sites":
                df_budget_base = df_budget_base[df_budget_base[col_sites].astype(str) == selected_site]

            # FILTRAGE STRICT : Il faut les deux valeurs (Budget ET Adjugé)
            df_plot_data = df_budget_base[(df_budget_base[col_budget] > 0) & (df_budget_base[col_adjuge] > 0)].head(20)

            if not df_plot_data.empty:
                # Préparation du graphique barplot groupé
                df_melt = df_plot_data.melt(
                    id_vars=[col_titre], 
                    value_vars=[col_budget, col_adjuge], 
                    var_name='Type', 
                    value_name='Montant'
                )
                
                fig2, ax2 = plt.subplots(figsize=(15, 6))
                sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                plt.xticks(rotation=45, ha='right')
                plt.ylabel("Montant (DH)")
                st.pyplot(fig2)
                
                # Tableau récapitulatif avec Écart
                df_plot_data['Écart'] = (df_plot_data[col_budget] - df_plot_data[col_adjuge]).round(2)
                st.write(f"**Détails - Site : {selected_site} (Top 20 affaires)**")
                st.dataframe(df_plot_data[[col_titre, col_sites, col_budget, col_adjuge, 'Écart']], use_container_width=True)
            else:
                st.warning("⚠️ Aucune affaire trouvée avec un Budget ET un Montant Adjugé remplis pour cette sélection.")

    except Exception as e:
        st.error(f"❌ Une erreur est survenue : {e}")

else:
    st.info("💡 Veuillez uploader le fichier Excel pour commencer l'analyse.")
