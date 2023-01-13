# --- Imports libs ---
import gradio as gr
import pandas as pd
import configparser


# --- Imports modules ---
from modules.model_embbeding import Embedding
from modules.module_vocabulary import Vocabulary
from modules.module_languageModel import LanguageModel


# --- Imports interfaces ---
from interfaces.interface_WordExplorer import interface as interface_wordExplorer
from interfaces.interface_BiasWordExplorer import interface as interface_biasWordExplorer
from interfaces.interface_data import interface as interface_data
from interfaces.interface_biasPhrase import interface as interface_biasPhrase
from interfaces.interface_crowsPairs import interface as interface_crowsPairs


# --- Tool config ---
cfg = configparser.ConfigParser()
cfg.read('config/tool.cfg')

LANGUAGE            = cfg['INTERFACE']['language']

if cfg['WORD_EXPLORER']['embeddings_path']:
    EMBEDDINGS_PATH = "data_custom/" + cfg['WORD_EXPLORER']['embeddings_path']
else:
    EMBEDDINGS_PATH = "data/100k_es_embedding.vec" if LANGUAGE == 'es' else "data/100k_en_embedding.vec"

NN_METHOD           = cfg['WORD_EXPLORER']['nn_method']
MAX_NEIGHBORS       = int(cfg['WORD_EXPLORER']['max_neighbors'])
CONTEXTS_DATASET    = "vialibre/splittedspanish3bwc"
VOCABULARY_SUBSET   = cfg['DATA']['vocabulary_subset']
AVAILABLE_WORDCLOUD = cfg['DATA'].getboolean('available_wordcloud')
LANGUAGE_MODEL      = "dccuchile/bert-base-spanish-wwm-uncased" if LANGUAGE == 'es' else "bert-base-uncased"
AVAILABLE_LOGS      = cfg['LOGS'].getboolean('available_logs')


# --- Init classes ---
embedding = Embedding(
    path=EMBEDDINGS_PATH,
    limit=100000,
    randomizedPCA=False,
    max_neighbors=MAX_NEIGHBORS,
    nn_method=NN_METHOD
)
vocabulary = Vocabulary(
    subset_name=VOCABULARY_SUBSET
)
beto_lm = LanguageModel(
    model_name=LANGUAGE_MODEL
)
labels = pd.read_json(f"language/{LANGUAGE}.json")["app"]


# --- Main App ---
INTERFACE_LIST = [
    interface_biasWordExplorer(
        embedding=embedding,
        available_logs=AVAILABLE_LOGS,
        lang=LANGUAGE),
    interface_wordExplorer(
        embedding=embedding,
        available_logs=AVAILABLE_LOGS,
        max_neighbors=MAX_NEIGHBORS,
        lang=LANGUAGE),
    interface_data(
        vocabulary=vocabulary,
        contexts=CONTEXTS_DATASET,
        available_logs=AVAILABLE_LOGS,
        available_wordcloud=AVAILABLE_WORDCLOUD,
        lang=LANGUAGE),
    interface_biasPhrase(
        language_model=beto_lm,
        available_logs=AVAILABLE_LOGS,
        lang=LANGUAGE),
    interface_crowsPairs(
        language_model=beto_lm,
        available_logs=AVAILABLE_LOGS,
        lang=LANGUAGE),
]

TAB_NAMES = [
    labels["biasWordExplorer"],
    labels["wordExplorer"],
    labels["dataExplorer"],
    labels["phraseExplorer"],
    labels["crowsPairsExplorer"]
]

if LANGUAGE != 'es':
    # Skip data tab when using other than spanish language
    INTERFACE_LIST = INTERFACE_LIST[:2] + INTERFACE_LIST[3:]
    TAB_NAMES = TAB_NAMES[:2] + TAB_NAMES[3:]


iface = gr.TabbedInterface(
    interface_list= INTERFACE_LIST,
    tab_names=TAB_NAMES
)

iface.queue(concurrency_count=8)
iface.launch(
    debug=False,
    server_name="0.0.0.0",
    server_port=8080
)
