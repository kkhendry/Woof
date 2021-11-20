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
import en_core_web_md
nlp_wk = en_core_web_md.load()

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

def pathText(path):
    stmr = PorterStemmer()
    text = open(path, "r").read()
    text = re.sub("[^a-zA-z]"," ", text)

    return text

def textStemmer(text):
    stmr = PorterStemmer()
    tokens = word_tokenize(text)

    stems = []
    [stems.append(stmr.stem(word)) for word in tokens]
    stems = np.unique(tokens)

    return stems

def urlText(url):
    html = urlopen(url, timeout=10).read()
    soup = BeautifulSoup(html, features="html.parser")
 
    for script in soup(["script", "style"]):
        script.extract()
 
    text = soup.get_text()
    text = re.sub("[^a-zA-z]"," ", text)
    tokens = word_tokenize(text)
    text = " ".join(tokens)
    
    stmr = PorterStemmer()
    stems = []
    [stems.append(stmr.stem(word)) for word in tokens]
    stems = np.unique(stems)
    return text, stems
  
def isValid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
 
def linksBuilder(url, searcher, bar, internal_urls, external_urls):
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).content, "html.parser")
    urlf = set()
    domain_name = urlparse(url).netloc
    for link in soup.findAll('a'):
        href = link.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if isValid(href):
            if domain_name not in href:
                if href not in external_urls:
                    external_urls.add(href)
                    if searcher == "iei" and isValid(href):
                        try: 
                            urlopen(href)
                            external_urls.update(linksBuilder(href, "i", bar, internal_urls, external_urls))
                        except:
                            pass
            else:
                if href not in internal_urls:
                    internal_urls.add(href)
        bar.update(1)
    urlf.update(internal_urls)
    if searcher == "e" or searcher =="ie":
        urlf.update(external_urls)
    urlf.update(url)
    return urlf

def dbDict(db_dict, text, link, domain, profile, url_domain):
  if domain != "N/A":
    if domain not in db_dict.keys():
      db_dict[domain] = {'url': url_domain, 'profile': profile, 'links': [link], 'text': [text]} 
    else:
      db_dict[domain]['links'].append(link)
      db_dict[domain]['text'].append(text)
  else:
    if domain not in db_dict.keys():
      db_dict[link] = {'url': url_domain, 'profile': profile, 'links': [link], 'text': [text]}
    else:
      db_dict[link]['links'].append(link)
      db_dict[link]['text'].append(text)

  return db_dict

def dbBuilder(url,profile, internal_urls, external_urls, url_domain):
    start_time = time.time()
    bar = tqdm_notebook(total=200, desc = "Building Links...")
    links = list(linksBuilder(url, "iei", bar, internal_urls, external_urls))

    db_dict = {}
    for link in tqdm_notebook(links, desc = "Extracting Text..."):
        try:
          domain = re.sub(r'www.', "", link)
          domain = re.search('\//(.*?)\.', domain).group(1)
        except:
          domain = "N/A"

        if domain == url_domain:
          profile = "investor"
        else:
          profile = "innovator"

        try:
          text, stems = urlText(link)
          db_dict = dbDict(db_dict, text, link, domain, profile, url_domain)
        except:
          db_dict = dbDict(db_dict, "N/A - Webpage Inaccessible", "N/A - Webpage Inaccessible", domain, profile, url_domain)
          pass

    for db_key in db_dict.keys():
      for key in db_dict[db_key].keys():
        if key == "links" or key == "text":
          db_dict[db_key][key] = ",".join(np.unique(db_dict[db_key][key]))
    
    run_time = time.time() - start_time
    
    print("Finished, Running Time: ", run_time)

    return db_dict

def dbUpdate(db, urls, profiles):
    for i, url in tqdm_notebook(enumerate(urls), desc="Searching Inputs..."):
        internal_urls = set()
        external_urls = set()
        try:
            url_domain = re.sub(r'www.', "", url)
            url_domain = re.search('\//(.*?)\.', url_domain).group(1)
        except:
            url_domain = "N/A"

        db_urls = [db[k]['url'] for k in db.keys()]
        if url_domain in db_urls:
            action = input (url_domain + " exists in database, would you like to skip? (y/n): ")
            if action == "y":
                continue

        db_dict = dbBuilder(urls[i],profiles[i], internal_urls, external_urls, url_domain)
        db.update(db_dict)

    return db