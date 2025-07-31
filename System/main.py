import pandas as pd
from pyswip import Prolog
from cancion_esta import buscar_canciones_similares
from cancion_no_esta import buscar_cancion_en_api, ejecutar_algoritmo_con_nueva_cancion
import pygame
import warnings
import sys
import os
import contextlib
warnings.simplefilter(action='ignore', category=Warning)

# Funciones para suprimir y restaurar stderr
def suppress_prolog_errors():
    # Guardar el file descriptor original de stderr
    stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(stderr_fd)
    # Redirigir stderr a /dev/null
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    os.close(devnull)
    return saved_stderr_fd

def restore_prolog_errors(saved_stderr_fd):
    # Restaurar stderr al file descriptor original
    stderr_fd = sys.stderr.fileno()
    os.dup2(saved_stderr_fd, stderr_fd)
    os.close(saved_stderr_fd)

# Configurar Prolog
prolog = Prolog()

# Suprimir mensajes de error al cargar la base de conocimiento
saved_stderr_fd = suppress_prolog_errors()
knowledge_base_path = "/Users/gerardoaboulafia/Library/Mobile Documents/com~apple~CloudDocs/UCA/Documentos/Cuatrimestre 4/Algoritmia/Sistema Experto/Sistema/music_knowledge_base_safe.pl"
prolog.consult(knowledge_base_path)
restore_prolog_errors(saved_stderr_fd)

# Consultar Prolog y cargar DataFrame inicial
def cargar_dataframe_desde_prolog(genero):
    """
    Cargar las canciones de la base de conocimiento filtrando por género.
    """
    # Construimos la consulta en una sola línea y sin el punto final
    query = f"song(genre('{genero}'), name(Name), artist(Artist), album(Album), popularity(Popularity), " \
            "artist_popularity(ArtistPopularity), danceability(Danceability), energy(Energy), " \
            "key(Key), loudness(Loudness), mode(Mode), speechiness(Speechiness), " \
            "acousticness(Acousticness), instrumentalness(Instrumentalness), " \
            "liveness(Liveness), valence(Valence), tempo(Tempo))"

    try:
        results = list(prolog.query(query))
        if results:
            print(f"Se encontraron {len(results)} canciones para el género '{genero}'.")
            return pd.DataFrame(results)
        else:
            print(f"No se encontraron canciones para el género '{genero}'.")
            return pd.DataFrame()  # Retorna un DataFrame vacío si no hay resultados
    except Exception as e:
        print(f"Error al consultar Prolog: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

# Mostrar canciones en bloques
def mostrar_canciones_en_bloques(canciones_similares, bloque_actual=0, bloque_tamano=10):
    """
    Muestra las canciones en bloques de tamaño fijo.
    """
    inicio = bloque_actual * bloque_tamano
    fin = inicio + bloque_tamano
    canciones_a_mostrar = canciones_similares.iloc[inicio:fin][['Name', 'Artist', 'Album']]
    if canciones_a_mostrar.empty:
        print("No hay más canciones para mostrar.")
        return None
    else:
        print("Mostrando canciones:")
        print(canciones_a_mostrar)
        return canciones_a_mostrar

# Pantalla inicial con grilla de botones sobre el banner
def mostrar_pantalla_inicial():
    pygame.init()

    # Definir colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Configuración de la pantalla
    window_width, window_height = 1000, 700
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Bienvenido")

    # Banner
    banner_image = pygame.image.load("banner.png")
    banner_width, banner_height = banner_image.get_size()
    scale_factor = window_width / banner_width
    scaled_banner = pygame.transform.scale(banner_image, (window_width, window_height))  # Ajustar al tamaño total

    # Géneros y configuración de botones
    generos = ["pop", "rap", "rock", "reggaeton", "salsa", "jazz", "r&b", "soul", "indie", "electro"]
    botones = []
    button_width = 150
    button_height = 50
    margin_x = 50
    margin_y = 20
    start_x = (window_width - (button_width * 5 + margin_x * 4)) // 2

    # Posicionar los botones más abajo en el banner
    start_y = int(window_height * 0.6)

    # Crear rectángulos para los botones
    for i, genero in enumerate(generos):
        col = i % 5
        row = i // 5
        x = start_x + col * (button_width + margin_x)
        y = start_y + row * (button_height + margin_y)
        botones.append({"rect": pygame.Rect(x, y, button_width, button_height), "genero": genero})

    # Fuente
    font = pygame.font.SysFont(None, 30)

    # Bucle principal
    running = True
    while running:
        # Dibujar el banner como fondo
        screen.blit(scaled_banner, (0, 0))

        # Dibujar botones sobre el banner
        for boton in botones:
            pygame.draw.rect(screen, BLACK, boton["rect"])
            text = font.render(boton["genero"], True, WHITE)
            text_rect = text.get_rect(center=boton["rect"].center)
            screen.blit(text, text_rect)

        # Detectar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones:
                    if boton["rect"].collidepoint(event.pos):
                        return boton["genero"]  # Retornar el género seleccionado

        # Actualizar pantalla
        pygame.display.flip()

# Main logic
def main():
    genero = mostrar_pantalla_inicial()
    if not genero:
        print("No se seleccionó ningún género. Saliendo del programa.")
        return

    print(f"Género seleccionado: {genero}")

    # Normalizar el género para Prolog (en caso de que haya discrepancias)
    genero = genero.lower().strip()

    # Cargar canciones del género
    df = cargar_dataframe_desde_prolog(genero)

    if df.empty:
        print(f"No se encontraron canciones para el género '{genero}'. Terminando el programa.")
        return

    nombre_cancion = input("Ingresa el nombre de la canción: ")
    nombre_artista = input("Ingresa el nombre del artista: ")

    # Verificar si la canción está en el DataFrame
    filtered_df = df[(df['Name'].str.lower() == nombre_cancion.lower()) & 
                     (df['Artist'].str.lower() == nombre_artista.lower())]

    if not filtered_df.empty:
        print("La canción está en el sistema. Buscando canciones similares...")
        canciones_similares = buscar_canciones_similares(df, nombre_cancion, nombre_artista)
    else:
        print("La canción no está en el sistema. Buscando en Spotify...")
        nueva_cancion_df = buscar_cancion_en_api(nombre_cancion, nombre_artista)
        if nueva_cancion_df is not None:
            print("Ejecutando algoritmo para generar canciones similares...")
            canciones_similares = ejecutar_algoritmo_con_nueva_cancion(df, nueva_cancion_df, nombre_cancion, nombre_artista)
        else:
            print("No se encontraron resultados en Spotify.")
            return

    # Mostrar canciones en bloques de 10
    bloque_actual = 0
    while True:
        canciones = mostrar_canciones_en_bloques(canciones_similares, bloque_actual)
        if canciones is None:
            break
        respuesta = input("¿Quieres ver más canciones? (sí/no): ").strip().lower()
        if respuesta == "sí":
            bloque_actual += 1
        elif respuesta == "no":
            print("Gracias por usar el programa. Adiós.")
            break
        else:
            print("Por favor, responde 'sí' o 'no'.")

if __name__ == "__main__":
    main()