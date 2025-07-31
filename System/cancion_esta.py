import pandas as pd
from sklearn.neighbors import NearestNeighbors

def buscar_canciones_similares(df, song_name, artist_name):
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
        return None