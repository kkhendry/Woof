from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
import requests
from socket import timeout
from tqdm.notebook import tqdm_notebook
import re
import sys
import time
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk import word_tokenize
import numpy as np
import pandas as pd
import spacy
from spacy import displacy
import json
import matplotlib.pyplot as plt
import os
!python -m spacy download en_core_web_md
import en_core_web_md
nlp_wk = en_core_web_md.load()

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

