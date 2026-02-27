import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Configuration large
st.set_page_config(layout="wide", page_title="Dashboard AZNAG")

st.title("📊 Analyse du Suivi des Affaires - AZNAG")

# --- FONCTIONS DE NETTOYAGE ET CALCUL ---
def clean_financial_value(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    return float(value)

# --- CHARGEMENT ---
uploaded_file_aznag = st.file_uploader("📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", type=["xlsx"])

if uploaded_file_aznag:
    try:
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        # Index colonnes : A=0, C=2, G=6, J=9, N=13
        col_exercice = df_aznag.columns[0]
        col_sites    = df_aznag.columns[2]
        col_etat     = "Etat"
        col_titre    = df_aznag.columns[6]
        col_budget   = df_aznag.columns[9]
        col_adjuge   = df_aznag.columns[13]

        # Nettoyage global
        df_aznag = df_aznag.dropna(subset=[col_exercice, col_titre], how='all')
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # Filtre Exercice
        exercices_dispo = sorted(df_aznag[col_exercice].dropna().unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Sélectionner l'EXERCICE :", options=["Tous"] + exercices_dispo)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        st.write(f"### 📋 Données : {selected_year}")
        st.dataframe(df_filtered, use_container_width=True)

        if 'show_etat' not in st.session_state: st.session_state.show_etat = False
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False

        c_btn1, c_btn2, _ = st.columns([1, 1, 4])
        with c_btn1:
            if st.button("Etat"): st.session_state.show_etat = not st.session_state.show_etat
        with c_btn2:
            if st.button("Ecart budgétaire"): st.session_state.show_budget = not st.session_state.show_budget

        # --- BLOC ETAT ---
        if st.session_state.show_etat:
            st.write("---")
            df_clean_etat = df_filtered.dropna(subset=[col_etat])
            counts = df_clean_etat[col_etat].value_counts()
            df_stats = pd.DataFrame({"Nombre": counts, "Pourcentage": (counts/counts.sum()*100).round(2)})
            c1, c2 = st.columns([1, 2])
            with c1: st.dataframe(df_stats, use_container_width=True)
            with c2:
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", order=counts.index, ax=ax)
                st.pyplot(fig)

        # --- BLOC ECART BUDGÉTAIRE ---
        if st.session_state.show_budget:
            st.write("---")
            sites_dispo = sorted(df_filtered[col_sites].dropna().unique().astype(str))
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites_dispo)
            
            df_b = df_filtered.copy()
            if selected_site != "Tous les sites":
                df_b = df_b[df_b[col_sites].astype(str) == selected_site]

            # Filtrage strict (Budget ET Adjugé > 0)
            df_plot = df_b[(df_b[col_budget] > 0) & (df_b[col_adjuge] > 0)].head(15)

            if not df_plot.empty:
                # Graphique
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig2, ax2 = plt.subplots(figsize=(16, 8))
                barplot = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                
                # Échelle tous les 500 000
                ax2.yaxis.set_major_locator(ticker.MultipleLocator(500000))
                ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                
                # AFFICHAGE DES MONTANTS SUR LES BARRES
                for p in barplot.patches:
                    if p.get_height() > 0:
                        barplot.annotate(format(int(p.get_height()), ','), 
                                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                                       ha = 'center', va = 'center', 
                                       xytext = (0, 9), 
                                       textcoords = 'offset points',
                                       fontsize=9, fontweight='bold')

                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', linestyle='--', alpha=0.3)
                st.pyplot(fig2)
                
                # CALCUL INDICATEUR % ECART
                # Formule : (Adjugé / Budget) * 100
                df_plot['% d’Écart'] = ((df_plot[col_adjuge] / df_plot[col_budget]) * 100).round(2)
                df_plot['Écart (DH)'] = (df_plot[col_budget] - df_plot[col_adjuge]).round(2)
                
                st.write(f"**Analyse détaillée - Site : {selected_site}**")
                st.dataframe(df_plot[[col_titre, col_budget, col_adjuge, 'Écart (DH)', '% d’Écart']], use_container_width=True)
            else:
                st.warning("⚠️ Aucune donnée complète (Budget + Adjugé) pour ce site.")

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
