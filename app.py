import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Configuration large
st.set_page_config(layout="wide", page_title="Dashboard AZNAG")

st.title("📊 Suivi des Affaires - AZNAG")

# --- FONCTION DE NETTOYAGE DES MONTANTS ---
def clean_financial_value(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, str):
        # Nettoyage des caractères parasites
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    try:
        return float(value)
    except:
        return 0.0

uploaded_file = st.file_uploader("📂 Importez le fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        # keep_default_na=False pour ne pas ignorer le site "NA"
        df_aznag = pd.read_excel(uploaded_file, engine='openpyxl', keep_default_na=False)
        
        # Mapping des colonnes (A=0, C=2, G=6, J=9, N=13)
        col_exercice = df_aznag.columns[0]
        col_sites    = df_aznag.columns[2]
        col_etat     = "Etat" 
        col_titre    = df_aznag.columns[6]
        col_budget   = df_aznag.columns[9]
        col_adjuge   = df_aznag.columns[13]

        # Nettoyage généralisé des montants
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # --- FILTRE EXERCICE ---
        exercices = sorted(df_aznag[col_exercice].astype(str).unique(), reverse=True)
        selected_year = st.selectbox("📅 Exercice :", options=["Tous"] + exercices)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # --- ÉTATS DES BOUTONS (SESSION STATE) ---
        if 'show_etat' not in st.session_state: st.session_state.show_etat = False
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False
        if 'show_site_analysis' not in st.session_state: st.session_state.show_site_analysis = False
        
        col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1.5, 1.5, 3])
        
        with col_btn1:
            if st.button("📊 Etat"):
                st.session_state.show_etat = not st.session_state.show_etat
        
        with col_btn2:
            if st.button("💰 Ecart budgétaire"):
                st.session_state.show_budget = not st.session_state.show_budget

        with col_btn3:
            if st.button("🏢 Etat par Site"):
                st.session_state.show_site_analysis = not st.session_state.show_site_analysis

        # ---------------------------------------------------------
        # 1. BLOC ANALYSE : ETAT (Trié + Dégradé Orange + %)
        # ---------------------------------------------------------
        if st.session_state.show_etat:
            st.write("---")
            st.write("### 📈 Répartition par Etat")
            
            df_clean_etat = df_filtered[df_filtered[col_etat].astype(str).str.lower() != "none"].copy()
            counts = df_clean_etat[col_etat].value_counts().reset_index()
            counts.columns = [col_etat, 'Nombre']
            
            # Calcul du pourcentage
            total_count = counts['Nombre'].sum()
            counts['Pourcentage (%)'] = ((counts['Nombre'] / total_count) * 100).round(2)
            
            if not counts.empty:
                fig1, ax1 = plt.subplots(figsize=(12, 5))
                barplot1 = sns.barplot(data=counts, x=col_etat, y='Nombre', palette="Oranges_r", ax=ax1)
                
                for p in barplot1.patches:
                    ax1.annotate(format(int(p.get_height()), 'd'), 
                                (p.get_x() + p.get_width() / 2., p.get_height()), 
                                ha='center', va='center', xytext=(0, 9), 
                                textcoords='offset points', fontweight='bold')
                
                plt.xticks(rotation=45)
                st.pyplot(fig1)
                st.dataframe(counts, use_container_width=True)

        # ---------------------------------------------------------
        # 2. BLOC ANALYSE : ECART BUDGÉTAIRE (Filtrage strict)
        # ---------------------------------------------------------
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💸 Comparaison Budget vs Adjugé (Par Affaire)")
            
            # Filtre strict : Budget ET Adjugé remplis (supérieurs à 0)
            df_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)].copy()
            
            sites = sorted([str(s) for s in df_strict[col_sites].unique()])
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites)
            
            df_plot = df_strict
            if selected_site != "Tous les sites":
                df_plot = df_plot[df_plot[col_sites].astype(str) == selected_site]

            if not df_plot.empty:
                df_plot = df_plot.head(15)
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                
                fig2, ax2 = plt.subplots(figsize=(16, 8))
                barplot2 = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                
                for p in barplot2.patches:
                    if p.get_height() > 0:
                        barplot2.annotate(format(int(p.get_height()), ','), 
                                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                                         ha='center', va='center', xytext=(0, 10), 
                                         textcoords='offset points', fontsize=8, fontweight='bold')

                ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45, ha='right')
                plt.ylim(0, df_plot[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig2)
                st.dataframe(df_plot[[col_titre, col_budget, col_adjuge]], use_container_width=True)
            else:
                st.warning("⚠️ Aucune affaire complète (Budget + Adjugé) à afficher.")

        # ---------------------------------------------------------
        # 3. BLOC ANALYSE : ETAT PAR SITE (Mêmes couleurs)
        # ---------------------------------------------------------
        if st.session_state.show_site_analysis:
            st.write("---")
            st.write("### 🏢 Analyse Cumulative par Site")

            # Filtrage strict avant groupement
            df_site_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)].copy()
            df_site_group = df_site_strict.groupby(col_sites)[[col_budget, col_adjuge]].sum().reset_index()

            if not df_site_group.empty:
                df_site_melt = df_site_group.melt(id_vars=[col_sites], value_vars=[col_budget, col_adjuge], 
                                                var_name='Type', value_name='Montant Total')
                
                fig3, ax3 = plt.subplots(figsize=(14, 7))
                barplot3 = sns.barplot(data=df_site_melt, x=col_sites, y='Montant Total', hue='Type', ax=ax3, palette=["#3498db", "#e67e22"])
                
                for p in barplot3.patches:
                    if p.get_height() > 0:
                        ax3.annotate(format(int(p.get_height()), ','), 
                                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                                    ha='center', va='center', xytext=(0, 10), 
                                    textcoords='offset points', fontsize=9, fontweight='bold')

                ax3.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45)
                plt.ylim(0, df_site_group[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig3)
                st.dataframe(df_site_group, use_container_width=True)
            else:
                st.info("ℹ️ Aucun site n'a de données complètes (Budget + Adjugé).")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
