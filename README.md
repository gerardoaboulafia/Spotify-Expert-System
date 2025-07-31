# Spotify-Expert-System
# Spotify-Expert-System
An academic project that fuses *symbolic reasoning* (Prolog) with *data-driven similarity search* (K-NN) to recommend new music.  
The workflow:

1.⁠ ⁠*Playlist harvesting* – pull up to 3 300 tracks from 12 personal playlists via the Spotify Web API.  
2.⁠ ⁠*Feature enrichment* – fetch audio features in 100-track batches to stay within API limits.  
3.⁠ ⁠*Knowledge-base generation* – transform every track into a ⁠ song/17 ⁠ fact and write them to ⁠ knowledge_base.pl ⁠.  
4.⁠ ⁠*K-NN model* – normalise 20 numerical features and index them with ⁠ scikit-learn.NearestNeighbors ⁠ to find the k closest songs.  
5.⁠ ⁠*CLI loop (finite automaton)* – guide the user through genre → song → artist, then output a 10-song radio; deterministic states q0–q7 guarantee a predictable dialogue.

---

## Folder layout
└── notebooks/

     └── Base_Conocimiento_API.ipynb   # ETL + EDA

└── system/

    └── main.py                           # CLI: genre → song → recommendations

    └── cancion_esta.py                   # utilities when seed song is in KB

    └── cancion_no_esta.py                # utilities when seed song is missing

    └── knowledge_base.pl                 # ~3 300 song

└── Sistema_Experto.pdf               # full technical report

## Quick start

⁠ bash
# 1) Create environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # pandas, spotipy, scikit-learn, swiplserver …

# 2) Build (or refresh) KB and model from playlists
python notebooks/Base_Conocimiento_API.ipynb   # or run `make kb`

# 3) Ask for a radio
python main.py --genre "pop" \
               --song  "Peaches" \
               --artist "Justin Bieber" \
               --k 10
 ⁠
*Note:* To use the system with songs that are not in the knowledge base, you need to provide your own API Keys.