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
    return float(value)import streamlit as st
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

        # Nettoyage initial
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # Filtre Exercice
        exercices = sorted(df_aznag[col_exercice].unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Exercice :", options=["Tous"] + exercices)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # --- SESSION STATE ---
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

        # 1. BLOC ETAT (TRIÉ + DÉGRADÉ ORANGE + COLONNE %)
        if st.session_state.show_etat:
            st.write("---")
            st.write(f"### 📈 Répartition par Etat")
            
            df_clean_etat = df_filtered[df_filtered[col_etat].astype(str).str.lower() != "none"]
            counts = df_clean_etat[col_etat].value_counts().reset_index()
            counts.columns = [col_etat, 'Nombre']
            
            # AJOUT DE LA COLONNE POURCENTAGE
            counts['Pourcentage (%)'] = ((counts['Nombre'] / counts['Nombre'].sum()) * 100).round(2)
            
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

        # 2. BLOC ECART BUDGÉTAIRE
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💸 Comparaison Budget vs Adjugé (Par Affaire)")
            df_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            sites = sorted([str(s) for s in df_strict[col_sites].unique()])
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites)
            df_plot = df_strict.copy()
            if selected_site != "Tous les sites":
                df_plot = df_plot[df_plot[col_sites].astype(str) == selected_site]

            if not df_plot.empty:
                df_plot = df_plot.head(15)
                # Ajout pourcentage d'écart dans le tableau des affaires
                df_plot['Pourcentage (%)'] = ((df_plot[col_adjuge] / df_plot[col_budget]) * 100).round(2)
                
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig2, ax2 = plt.subplots(figsize=(16, 8))
                barplot2 = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                
                for p in barplot2.patches:
                    if p.get_height() > 0:
                        barplot2.annotate(format(int(p.get_height()), ','), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=8, fontweight='bold')
                
                ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45, ha='right')
                plt.ylim(0, df_plot[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig2)
                st.dataframe(df_plot[[col_titre, col_budget, col_adjuge, 'Pourcentage (%)']], use_container_width=True)

        # 3. BLOC ETAT PAR SITE (DÉTAILLÉ + COLONNE %)
        if st.session_state.show_site_analysis:
            st.write("---")
            st.write("### 🏢 Analyse Cumulative par Site")
            
            df_site_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            df_site_group = df_site_strict.groupby(col_sites)[[col_budget, col_adjuge]].sum().reset_index()
            
            if not df_site_group.empty:
                # AJOUT DE LA COLONNE POURCENTAGE (Consommation du budget)
                df_site_group['Consommation (%)'] = ((df_site_group[col_adjuge] / df_site_group[col_budget]) * 100).round(2)
                
                df_site_melt = df_site_group.melt(id_vars=[col_sites], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant Total')
                fig3, ax3 = plt.subplots(figsize=(14, 7))
                barplot3 = sns.barplot(data=df_site_melt, x=col_sites, y='Montant Total', hue='Type', ax=ax3, palette=["#3498db", "#e67e22"])
                
                for p in barplot3.patches:
                    if p.get_height() > 0:
                        barplot3.annotate(format(int(p.get_height()), ','), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=9, fontweight='bold')
                
                ax3.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45)
                plt.ylim(0, df_site_group[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig3)
                
                # Affichage du tableau trié par consommation
                st.dataframe(df_site_group.sort_values(by='Consommation (%)', ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")

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

        # Nettoyage initial
        df_aznag[col_budget] = df_aznag[col_budget].apply(clean_financial_value)
        df_aznag[col_adjuge] = df_aznag[col_adjuge].apply(clean_financial_value)

        # Filtre Exercice
        exercices = sorted(df_aznag[col_exercice].unique().astype(str), reverse=True)
        selected_year = st.selectbox("📅 Exercice :", options=["Tous"] + exercices)
        df_filtered = df_aznag if selected_year == "Tous" else df_aznag[df_aznag[col_exercice].astype(str) == selected_year]

        # --- SESSION STATE ---
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

        # 1. BLOC ETAT (TRIÉ + DÉGRADÉ ORANGE)
        if st.session_state.show_etat:
            st.write("---")
            st.write(f"### 📈 Répartition par Etat (Ordre décroissant)")
            
            df_clean_etat = df_filtered[df_filtered[col_etat].astype(str).str.lower() != "none"]
            counts = df_clean_etat[col_etat].value_counts().reset_index()
            counts.columns = [col_etat, 'Nombre']
            
            if not counts.empty:
                fig1, ax1 = plt.subplots(figsize=(12, 5))
                # Utilisation de la palette "Oranges_r" (r pour reverse, du plus foncé au plus clair)
                barplot1 = sns.barplot(data=counts, x=col_etat, y='Nombre', palette="Oranges_r", ax=ax1)
                
                for p in barplot1.patches:
                    ax1.annotate(format(int(p.get_height()), 'd'), 
                                (p.get_x() + p.get_width() / 2., p.get_height()), 
                                ha='center', va='center', xytext=(0, 9), 
                                textcoords='offset points', fontweight='bold', color="#444444")
                
                plt.xticks(rotation=45)
                plt.ylabel("Nombre d'affaires")
                st.pyplot(fig1)
                st.dataframe(counts, use_container_width=True)

        # 2. BLOC ECART BUDGÉTAIRE
        if st.session_state.show_budget:
            st.write("---")
            st.write("### 💸 Comparaison Budget vs Adjugé (Affaires complètes)")
            df_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            sites = sorted([str(s) for s in df_strict[col_sites].unique()])
            selected_site = st.selectbox("📍 Filtrer par Site :", options=["Tous les sites"] + sites)
            df_plot = df_strict.copy()
            if selected_site != "Tous les sites":
                df_plot = df_plot[df_plot[col_sites].astype(str) == selected_site]

            if not df_plot.empty:
                df_plot = df_plot.head(15)
                df_melt = df_plot.melt(id_vars=[col_titre], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant')
                fig2, ax2 = plt.subplots(figsize=(16, 8))
                barplot2 = sns.barplot(data=df_melt, x=col_titre, y='Montant', hue='Type', ax=ax2, palette=["#3498db", "#e67e22"])
                for p in barplot2.patches:
                    if p.get_height() > 0:
                        barplot2.annotate(format(int(p.get_height()), ','), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=8, fontweight='bold')
                ax2.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45, ha='right')
                plt.ylim(0, df_plot[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig2)

        # 3. BLOC ETAT PAR SITE
        if st.session_state.show_site_analysis:
            st.write("---")
            st.write("### 🏢 Analyse Cumulative par Site")
            df_site_strict = df_filtered[(df_filtered[col_budget] > 0) & (df_filtered[col_adjuge] > 0)]
            df_site_group = df_site_strict.groupby(col_sites)[[col_budget, col_adjuge]].sum().reset_index()
            if not df_site_group.empty:
                df_site_melt = df_site_group.melt(id_vars=[col_sites], value_vars=[col_budget, col_adjuge], var_name='Type', value_name='Montant Total')
                fig3, ax3 = plt.subplots(figsize=(14, 7))
                barplot3 = sns.barplot(data=df_site_melt, x=col_sites, y='Montant Total', hue='Type', ax=ax3, palette=["#3498db", "#e67e22"])
                for p in barplot3.patches:
                    if p.get_height() > 0:
                        barplot3.annotate(format(int(p.get_height()), ','), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=9, fontweight='bold')
                ax3.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                plt.xticks(rotation=45)
                plt.ylim(0, df_site_group[[col_budget, col_adjuge]].max().max() * 1.15)
                st.pyplot(fig3)
                st.dataframe(df_site_group, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
