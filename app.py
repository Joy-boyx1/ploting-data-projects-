import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page pour utiliser toute la largeur
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
        
        # 2. Nettoyage
        column_name = "Etat"
        if column_name in df_aznag.columns:
            df_aznag = df_aznag.dropna(subset=[column_name])
            df_aznag = df_aznag[df_aznag[column_name].astype(str).str.strip() != ""]
        
        # 3. Affichage du tableau complet (Largeur maximale)
        st.write("### 📋 Données complètes")
        st.dataframe(df_aznag, use_container_width=True)

        # --- GESTION DU BOUTON AFFICHAGE/MASQUAGE ---
        if 'show_stats' not in st.session_state:
            st.session_state.show_stats = False

        def toggle_stats():
            st.session_state.show_stats = not st.session_state.show_stats

        st.write("---")
        label = "❌ Masquer l'analyse graphique" if st.session_state.show_stats else "📈 Afficher l'analyse graphique"
        st.button(label, on_click=toggle_stats)

        # 4. Bloc d'analyse (S'affiche uniquement si show_stats est True)
        if st.session_state.show_stats:
            if column_name in df_aznag.columns:
                st.write("### 📈 Répartition par État")
                
                counts = df_aznag[column_name].value_counts()
                percentages = df_aznag[column_name].value_counts(normalize=True) * 100
                
                df_stats_etat = pd.DataFrame({
                    "Nombre": counts,
                    "Pourcentage (%)": percentages.map("{:.2f}%".format)
                })
                
                # Utilisation de colonnes larges
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Tableau récapitulatif**")
                    # On utilise dataframe au lieu de table pour avoir plus de contrôle sur la largeur
                    st.dataframe(df_stats_etat, use_container_width=True)

                with col2:
                    # Création du graphique en version plus large
                    fig, ax = plt.subplots(figsize=(12, 5)) 
                    sns.countplot(
                        data=df_aznag, 
                        x=column_name, 
                        palette="viridis", 
                        order=counts.index,
                        ax=ax
                    )
                    plt.title(f"Nombre d'affaires par {column_name}")
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
            else:
                st.error(f"❌ Colonne '{column_name}' introuvable.")
                
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
