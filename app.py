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
        clean_val = value.replace('DH', '').replace(' ', '').replace('\xa0', '').replace(',', '.')
        try:
            return float(clean_val)
        except:
            return 0.0
    return float(value)

uploaded_file = st.file_uploader("📂 Importez le fichier Excel", type=["xlsx"])

if uploaded_file:
    try:
        df_aznag = pd.read_excel(uploaded_file, engine='openpyxl', keep_default_na=False)
        
        # Mapping des colonnes
        col_exercice = df_aznag.columns[0]
        col_sites    = df_aznag.columns[2]
        col_etat     = "Etat" 
        col_titre    = df_aznag.columns[6]
        col_budget   = df_aznag.columns[9]
        col_adjuge   = df_aznag.columns[13]

        # Nettoyage de base
        df_aznag = df_aznag[df_aznag[col_exercice].astype(str).str.strip() != ""]
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # Filtre Exercice
        exercices = sorted(df_aznag[col_exercice].unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Exercice :", options=["Tous"] + exercices)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # Session State pour les boutons
        if 'show_etat' not in st.session_state: st.session_state.show_etat = False
        if 'show_budget' not in st.session_state: st.session_state.show_budget = False
        if 'show_site_analysis' not in st.session_state: st.session_state.show_site_analysis = False
        
        col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1.5, 1.5, 3])
        with col_btn1:
            if st.button("📊 Etat"): st.session_state.show_etat = not st.session_state.show_etat
        with col_btn2:
            if st.button("💰 Ecart budgétaire"): st.session_state.show_budget = not st.session_state.show_budget
        with col_btn3:
            if st.button("🏢 Etat par Site"): st.session_state.show_site_analysis = not st.session_state.show_site_analysis

        # 1. BLOC ETAT
        if st.session_state.show_etat:
            st.write("---")
            df_clean_etat = df_filtered[df_filtered[col_etat].astype(str).str.lower() != "none"]
            counts = df_clean_etat[col_etat].value_counts()
            c1, c2 = st.columns([1, 2])
            with c1: st.dataframe(counts, use_container_width=True)
            with c2:
                fig1, ax1 = plt.subplots(figsize=(10, 4))
                sns.countplot(data=df_clean_etat, x=col_etat, palette="viridis", ax=ax1)
                st.pyplot(fig1)

        # 2. BLOC ECART BUDGÉTAIRE (Filtrage strict appliqué)
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💸 Comparaison Budget vs Adjugé (Par Affaire)")
            
            # ELIMINATION DES LIGNES SI L'UNE DES VALEURS EST VIDE (0.0)
            df_b = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            
            sites = sorted([str(s) for s in df_b[col_sites].unique()])
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites)
            if selected_site != "Tous les sites":
                df_b = df_b[df_b[col_sites].astype(str) == selected_site]

            df_plot = df_b.head(15)

            if not df_plot.empty:
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig2, ax2 = plt.subplots(figsize=(16, 7))
                barplot = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig2)
            else:
                st.warning("⚠️ Aucune affaire n'a les deux montants (Budget et Adjugé) renseignés.")

        # 3. BLOC ETAT PAR SITE (Filtrage strict appliqué)
        if st.session_state.show_site_analysis:
            st.write("---")
            st.write("### 🏢 Analyse Cumulative par Site")

            # On ne prend que les lignes où Budget ET Adjugé sont remplis avant de grouper
            df_site_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            
            df_site_group = df_site_strict.groupby(col_sites)[[col_budget, col_adjuge]].sum().reset_index()

            if not df_site_group.empty:
                df_site_melt = df_site_group.melt(id_vars=[col_sites], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant Total')
                fig3, ax3 = plt.subplots(figsize=(14, 6))
                sns.barplot(data=df_site_melt, x=col_sites, y='Montant Total', hue='Type', ax=ax3, palette=["#3498db", "#e67e22"])
                ax3.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45)
                st.pyplot(fig3)
                st.dataframe(df_site_group, use_container_width=True)
            else:
                st.info("ℹ️ Aucun site ne possède de données complètes (Budget + Adjugé).")

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
