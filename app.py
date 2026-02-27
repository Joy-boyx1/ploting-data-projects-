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
    # Vérification du nom du fichier (optionnel mais recommandé)
    if "SUIVI AFFAIRES GLOBALE - AZNAG" in uploaded_file_aznag.name:
        try:
            # 2. Lecture du fichier
            df_aznag = pd.read_excel(uploaded_file_aznag, engine='openpyxl')
            
            # Affichage de l'aperçu
            st.write("### Aperçu des données")
            st.dataframe(df_aznag.head(), use_container_width=True)

            # 3. Vérification de la colonne 'ETAT'
            if "ETAT" in df_aznag.columns:
                st.write("### Répartition par État")
                
                # Calcul des statistiques (Nombre et Pourcentage)
                counts = df_aznag["ETAT"].value_counts()
                percentages = df_aznag["ETAT"].value_counts(normalize=True) * 100
                
                # Création du tableau récapitulatif
                df_stats_etat = pd.DataFrame({
                    "Nombre": counts,
                    "Pourcentage (%)": percentages.round(2)
                })
                
                # Affichage du tableau
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.table(df_stats_etat)

                # 4. Visualisation avec Seaborn / Matplotlib
                with col2:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.countplot(
                        data=df_aznag, 
                        x="ETAT", 
                        palette="viridis", 
                        order=counts.index,
                        ax=ax
                    )
                    
                    # Ajout des labels
                    plt.title("Répartition des Affaires par État", fontsize=14)
                    plt.xlabel("État", fontsize=12)
                    plt.ylabel("Nombre d'affaires", fontsize=12)
                    plt.xticks(rotation=45)
                    
                    # Affichage du graphique
                    st.pyplot(fig)
            else:
                st.error("❌ La colonne 'ETAT' est introuvable dans le fichier.")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture : {e}")
    else:
        st.warning("⚠️ Le fichier importé ne semble pas être le bon (Nom attendu : SUIVI AFFAIRES GLOBALE - AZNAG)")
