import streamlit as st
import pandas as pd
import sqlite3
import os

DB_FILE = "learny.db"

def check_db_exists():
    """Vérifie si le fichier de la base de données existe."""
    return os.path.exists(DB_FILE)

def search_videos(search_term):
    """Recherche des vidéos dans la base de données locale."""
    conn = sqlite3.connect(DB_FILE)
    query = f"SELECT * FROM videos WHERE title LIKE ? OR query_term LIKE ?"
    search_pattern = f"%{search_term}%"
    
    df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern))
    conn.close()
    return df

# --- Interface Utilisateur ---
st.set_page_config(page_title="Learny", layout="wide")

# Affiche le logo dans la barre latérale
st.sidebar.image("assets/learny.png")
st.sidebar.title("Learny 🎓")

st.header("Ton Moteur de Contenu Éducatif")

if not check_db_exists():
    st.warning("La base de données n'est pas encore prête. Il faut la générer.")
    st.info("Le propriétaire du projet doit lancer l'action 'Ingest YouTube Data' sur GitHub pour créer la base de données initiale.")
else:
    search_query = st.text_input("Que veux-tu apprendre aujourd'hui ?", placeholder="Python, SQL, Data Science...")

    if search_query:
        results_df = search_videos(search_query)
        
        if not results_df.empty:
            st.success(f"{len(results_df)} ressources trouvées pour '{search_query}'")
            
            for index, row in results_df.iterrows():
                st.divider()
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(row['thumbnail_url'])
                with col2:
                    st.subheader(row['title'])
                    st.caption(f"Chaîne : {row['channel_title']}")
                    st.link_button("Voir la vidéo sur YouTube", f"https://www.youtube.com/watch?v={row['video_id']}")
        else:
            st.info(f"Aucune ressource trouvée pour '{search_query}' dans notre base de données.")