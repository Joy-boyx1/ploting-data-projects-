import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.subheader("📊 Analyse du Suivi des Affaires - AZNAG")

# 1. Upload spécifique du fichier
uploaded_file_aznag = st.file_uploader(
    "📂 Importez le fichier : SUIVI AFFAIRES GLOBALE - AZNAG.xlsx", 
    type=["xlsx"]
)

if uploaded_file_aznag:
    if "SUIVI AFFAIRES GLOBALE - AZNAG" in uploaded_file_aznag.name:
        try:
            # 2. Lecture du fichier
            df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
            
            # Affichage de l'ENSEMBLE des données
            st.write("### Données complètes")
            st.dataframe(df_aznag, use_container_width=True)

            # 3. Vérification de la colonne 'Etat' (Correction du nom)
            column_name = "Etat" 
            
            if column_name in df_aznag.columns:
                st.write("---")
                st.write("### 📈 Répartition par État")
                
                # Calcul des statistiques
                counts = df_aznag[column_name].value_counts()
                percentages = df_aznag[column_name].value_counts(normalize=True) * 100
                
                # Création du tableau récapitulatif
                df_stats_etat = pd.DataFrame({
                    "Nombre": counts,
                    "Pourcentage (%)": percentages.map("{:.2f}%".format) # Formatage propre
                })
                
                # Affichage côte à côte
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Statistiques détaillées**")
                    st.table(df_stats_etat)

                with col2:
                    # 4. Visualisation
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.countplot(
                        data=df_aznag, 
                        x=column_name, 
                        palette="viridis", 
                        order=counts.index,
                        ax=ax
                    )
                    
                    plt.title(f"Répartition des Affaires par {column_name}", fontsize=14)
                    plt.xlabel("État", fontsize=12)
                    plt.ylabel("Nombre d'affaires", fontsize=12)
                    plt.xticks(rotation=45)
                    
                    st.pyplot(fig)
            else:
                st.error(f"❌ La colonne '{column_name}' est introuvable. Colonnes détectées : {list(df_aznag.columns)}")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture : {e}")
    else:
        st.warning("⚠️ Nom de fichier incorrect.")
