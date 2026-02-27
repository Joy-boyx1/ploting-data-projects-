import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
        # 2. Lecture et nettoyage
        df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
        
        column_name = "Etat"
        if column_name in df_aznag.columns:
            # Nettoyage des lignes vides (None)
            df_aznag = df_aznag.dropna(subset=[column_name])
            df_aznag = df_aznag[df_aznag[column_name].astype(str).str.strip() != ""]
        
        # 3. Affichage du tableau de données principal
        st.write("### 📋 Données complètes")
        st.dataframe(df_aznag, use_container_width=True)

        # --- GESTION DU BOUTON "Etat" ---
        if 'show_analysis' not in st.session_state:
            st.session_state.show_analysis = False

        # Bouton nommé simplement "Etat"
        if st.button("Etat"):
            st.session_state.show_analysis = not st.session_state.show_analysis

        # 4. Bloc d'analyse conditionnel
        if st.session_state.show_analysis:
            if column_name in df_aznag.columns:
                st.write("---")
                st.write(f"### 📈 Analyse de la colonne : {column_name}")
                
                # Calculs
                counts = df_aznag[column_name].value_counts()
                percentages = (df_aznag[column_name].value_counts(normalize=True) * 100)
                
                df_stats = pd.DataFrame({
                    "Nombre": counts,
                    "Pourcentage (%)": percentages.map("{:.2f}%".format)
                })
                
                # Affichage élargi
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Récapitulatif**")
                    st.dataframe(df_stats, use_container_width=True)

                with col2:
                    # Graphique élargi
                    fig, ax = plt.subplots(figsize=(12, 5))
                    sns.countplot(
                        data=df_aznag, 
                        x=column_name, 
                        palette="magma", 
                        order=counts.index,
                        ax=ax
                    )
                    plt.title(f"Répartition par {column_name}")
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
            else:
                st.error(f"❌ La colonne '{column_name}' n'existe pas dans ce fichier.")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
