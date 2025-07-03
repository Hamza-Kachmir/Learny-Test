import os
import sqlite3
import pandas as pd
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# La clé API est lue depuis les secrets de GitHub (variable d'environnement)
API_KEY = os.environ.get("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("La clé API YouTube n'est pas configurée dans les secrets GitHub !")

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DB_FILE = "learny.db"

# Liste des sujets à rechercher
SEARCH_QUERIES = [
    "Python pour débutants",
    "Apprendre SQL",
    "Projet Data Engineering",
    "Tutoriel Streamlit",
    "API explication simple",
    "Machine Learning projet",
    "Cours Data Science",
    "Power BI tutoriel français"
]

def create_database():
    """Crée la base de données SQLite et la table si elles n'existent pas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        publish_date TEXT,
        channel_title TEXT,
        thumbnail_url TEXT,
        query_term TEXT
    )
    """)
    conn.commit()
    conn.close()
    print(f"Base de données '{DB_FILE}' prête.")

def fetch_youtube_data(query):
    """Interroge l'API YouTube et retourne une liste de vidéos."""
    # La variable s'appelle 'youtube' (minuscule)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    
    # Ligne corrigée : on utilise la variable 'youtube' (minuscule) et .search()
    search_response = Youtube().list(
        q=query,
        part="snippet",
        maxResults=25,
        type="video",
        relevanceLanguage="fr"
    ).execute()
    
    videos = []
    for item in search_response.get("items", []):
        video_data = {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "publish_date": item["snippet"]["publishTime"],
            "channel_title": item["snippet"]["channelTitle"],
            "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
            "query_term": query
        }
        videos.append(video_data)
        
    print(f"Trouvé {len(videos)} vidéos pour la recherche '{query}'.")
    return videos

def update_database(videos):
    """Met à jour la base de données avec de nouvelles vidéos, en évitant les doublons."""
    if not videos:
        return
        
    conn = sqlite3.connect(DB_FILE)
    df = pd.DataFrame(videos)
    
    # Construit une clause pour ne pas insérer les IDs qui existent déjà
    existing_ids = pd.read_sql_query("SELECT video_id FROM videos", conn)
    df = df[~df['video_id'].isin(existing_ids['video_id'])]

    if not df.empty:
        df.to_sql('videos', conn, if_exists='append', index=False)
        print(f"{len(df)} nouvelles vidéos insérées dans la base de données.")
    else:
        print("Aucune nouvelle vidéo à ajouter.")
    
    conn.close()

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    create_database()
    for query in SEARCH_QUERIES:
        videos = fetch_youtube_data(query)
        update_database(videos)
    
    print("Ingestion des données terminée !")