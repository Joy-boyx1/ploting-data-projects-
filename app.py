import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Configuration large
st.set_page_config(layout="wide", page_title="Dashboard AZNAG")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

# --- FONCTION DE NETTOYAGE DES MONTANTS ---
def clean_financial_value(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        # Retire 'DH', les espaces et remplace la virgule par un point
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    return float(value)

uploaded_file = st.file_uploader("📂 Importez le fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        # IMPORTANT : keep_default_na=False permet de lire "NA" comme un texte et non une valeur vide
        df_aznag = pd.read_excel(uploaded_file, engine='openpyxl', keep_default_na=False)
        
        # Mapping des colonnes (A=0, C=2, G=6, J=9, N=13)
        col_exercice = df_aznag.columns[0]
        col_sites    = df_aznag.columns[2]
        col_etat     = "Etat"
        col_titre    = df_aznag.columns[6]
        col_budget   = df_aznag.columns[9]
        col_adjuge   = df_aznag.columns[13]

        # 1. Nettoyage des lignes fantômes (None/vides)
        # On convertit en string pour éviter les erreurs de comparaison
        df_aznag = df_aznag[df_aznag[col_exercice].astype(str).str.strip() != ""]
        df_aznag = df_aznag[df_aznag[col_exercice].astype(str).lower() != "none"]

        # 2. Nettoyage des montants (Généralisé)
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # --- FILTRE EXERCICE ---
        exercices = sorted(df_aznag[col_exercice].unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Exercice :", options=["Tous"] + exercices)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        st.dataframe(df_filtered, use_container_width=True)

        # --- BOUTONS D'ANALYSE ---
        col1, col2, _ = st.columns([1, 1, 4])
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False
        
        with col2:
            if st.button("Ecart budgétaire"):
                st.session_state.show_budget = not st.session_state.show_budget

        # --- BLOC ÉCART BUDGÉTAIRE ---
        if st.session_state.show_budget:
            st.write("---")
            # Extraction des sites incluant désormais "NA"
            sites = sorted([str(s) for s in df_filtered[col_sites].unique() if str(s).strip() != ""])
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites)
            
            df_b = df_filtered.copy()
            if selected_site != "Tous les sites":
                df_b = df_b[df_b[col_sites].astype(str) == selected_site]

            # Filtrage strict : Budget ET Adjugé remplis
            df_plot = df_b[(df_b[col_budget] > 0) & (df_b[col_adjuge] > 0)].head(15)

            if not df_plot.empty:
                # Graphique avec étiquettes et échelle à 500k
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig, ax = plt.subplots(figsize=(16, 7))
                barplot = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax, palette=["#3498db", "#e67e22"])
                
                ax.yaxis.set_major_locator(ticker.MultipleLocator(500000))
                ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                
                # Annotations sur les barres
                for p in barplot.patches:
                    if p.get_height() > 0:
                        barplot.annotate(format(int(p.get_height()), ','), 
                                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                                       ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=8)

                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)
                
                # Indicateur % d'écart
                df_plot['% d’Écart'] = ((df_plot[col_adjuge] / df_plot[col_budget]) * 100).round(2)
                st.write(f"**Analyse détaillée - Site : {selected_site}**")
                st.dataframe(df_plot[[col_titre, col_budget, col_adjuge, '% d’Écart']], use_container_width=True)
            else:
                st.warning("Aucune donnée budgétaire complète pour cette sélection.")

    except Exception as e:
        st.error(f"Erreur : {e}")
