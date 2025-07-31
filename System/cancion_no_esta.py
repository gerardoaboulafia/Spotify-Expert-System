import pandas as pd
from sklearn.neighbors import NearestNeighbors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Configuración de Spotify API
cid = ''
secret = ''

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def buscar_cancion_en_api(nombre_cancion, nombre_artista=None):
    try:
        resultados = sp.search(q=nombre_cancion, type='track', limit=10)
        canciones = []
        
        for item in resultados['tracks']['items']:
            nombre = item['name']
            artista = item['artists'][0]['name']
            album = item['album']['name']
            popularidad = item['popularity']
            audio_features = sp.audio_features(item['id'])[0]
            
            if audio_features:
                canciones.append({
                    'Name': nombre,
                    'Artist': artista,
                    'Album': album,
                    'Popularity': popularidad,
                    'ArtistPopularity': sp.artist(item['artists'][0]['id'])['popularity'],
                    'Danceability': audio_features['danceability'],
                    'Energy': audio_features['energy'],
                    'Key': audio_features['key'],
                    'Loudness': audio_features['loudness'],
                    'Mode': audio_features['mode'],
                    'Speechiness': audio_features['speechiness'],
                    'Acousticness': audio_features['acousticness'],
                    'Instrumentalness': audio_features['instrumentalness'],
                    'Liveness': audio_features['liveness'],
                    'Valence': audio_features['valence'],
                    'Tempo': audio_features['tempo']
                })

        # Crear un DataFrame con los resultados
        df = pd.DataFrame(canciones)
        
        # Filtrar por artista si se proporciona
        if nombre_artista:
            df = df[df['Artist'].str.lower() == nombre_artista.lower()]
        
        return df if not df.empty else None
    except Exception as e:
        print(f"Error al buscar canción: {e}")
        return None

def ejecutar_algoritmo_con_nueva_cancion(df, nueva_cancion_df, song_name, artist_name):
    # Combinar el DataFrame original con la nueva canción
    df = pd.concat([df, nueva_cancion_df], ignore_index=True)

    # Ejecutar el algoritmo k-NN
    features = [
        "Popularity", "Danceability", "Energy", "Key", "Loudness",
        "Mode", "Speechiness", "Acousticness", "Instrumentalness", "Liveness", "Valence", "Tempo"
    ]
    
    # Normalizar los datos
    data_k = df[features]
    data_normalized = (data_k - data_k.min()) / (data_k.max() - data_k.min())
    
    # Configurar k-NN
    knn = NearestNeighbors(n_neighbors=30, metric="euclidean")
    knn.fit(data_normalized)

    # Filtrar canción por nombre y artista
    filtered_df = df[(df['Name'].str.lower() == song_name.lower()) & 
                     (df['Artist'].str.lower() == artist_name.lower())]
    filtered_df = filtered_df.sort_values(by='Popularity', ascending=False)
    
    if not filtered_df.empty:
        chosen_song_index = filtered_df.index[0]
        distances, indices = knn.kneighbors([data_normalized.iloc[chosen_song_index]])
        similar_songs = df.iloc[indices[0]]
        similar_songs["Distance"] = distances[0]
        return similar_songs
    else:
        print("La canción añadida no tiene suficientes datos para el análisis.")
        return None
