import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import time
import datetime
from operator import itemgetter, attrgetter
import math
import re

def index_doc(docs,doc_names):
    index = {}
    inverse_index = {}
    for doc,doc_name in zip(docs,doc_names):
        word_count={}
        for word in doc:
            if word in word_count.keys():
                word_count[word]+=1
            else:
                word_count[word]=1
        index[doc_name] = word_count
        #index[doc_name]=nltk.Text(doc).vocab()
    for doc in index.keys():
        doc_index = index[doc]
        for word in doc_index.keys():
            if word in inverse_index.keys():
                inverse_index[word].append(doc)
            else:
                inverse_index[word] = [doc]
    return index, inverse_index

def build_dictionary(index):
    dictionary = {}
    for word in index.keys():
        dictionary[word]=len(dictionary)
    return dictionary

def compute_tfidf(index,word_dictionary,doc_dictionary):
    vocab_size = len(word_dictionary)
    doc_size = len(doc_dictionary)
    tf = np.zeros((doc_size,vocab_size))
    for doc in index:
        index_per_doc = index[doc]
        vector = np.zeros(vocab_size)
        for word in index_per_doc:
            vector[word_dictionary[word]] = index_per_doc[word]
        vector = np.log(vector+1)
        tf[doc_dictionary[doc]] = vector
    idf_numerator = doc_size
    idf_denominator = np.sum(np.sign(tf),0)
    idf = np.log(idf_numerator/idf_denominator)
    tfidf = tf*idf
    return tfidf

def query_matching(inverse_dictionary,query):
    set_list = [set(inverse_dictionary[word]) for word in query]
    return set.intersection(*set_list)

def dictionary_vector(vector,doc_dictionary):
    dictionary={}
    result={}

    doc_size=len(doc_dictionary)

    for a in range(doc_size):
        for key in doc_dictionary.keys():
            if doc_dictionary[key]==a:
                dictionary[key] = vector[a]
    vector = sorted(dictionary.items(), key=itemgetter(1), reverse = True)
    
    for news in vector:
        result[news[0]]=news[1]    
    print(result)
    return result 

def read_doc(original_data):
    stopwrds = stopwords.words('english')

    docs=[]
    doc_names=[]

    for news in original_data:
        doc = word_tokenize(re.sub('[!"#%\'()*+,./:;<=>?\[\]\\xa0^_`{|}~’”“′‘\\\]',' ', news['title'].lower()+" "+news['article'].lower()))
        doc = [token for token in doc if token not in stopwrds]
        docs.append( doc)
        doc_names.append(news['url'])
    return docs,doc_names

def cosine_similarity(x,y):
    normalizing_factor_x = np.sqrt(np.sum(np.square(x)))
    normalizing_factor_y = np.sqrt(np.sum(np.square(y)))
    return np.matmul(x,np.transpose(y))/(normalizing_factor_x*normalizing_factor_y)

def query_dot(query,word_dictionary,doc_dictionary):
    vocab_size = len(word_dictionary)
    doc_size=len(doc_dictionary)
    vector = np.zeros(vocab_size)
    for word in query:
        if(word in word_dictionary):
            vector[word_dictionary[word]] = 1  
    vector = np.log(vector+1)
    idf_numerator = doc_size
    idf_denominator = np.sum(np.sign(vector),0)
    idf = np.log(idf_numerator/idf_denominator)
    tfidf = vector*idf
    return tfidf 

def score(tfidf,word_dictionary,doc_dictionary,query):
    result={}
    result2=[]
    i=0
    for doc_score in tfidf:
        score=0
        for word in query:
            if(word in word_dictionary):
                wordnum = word_dictionary[word]
                score += doc_score[wordnum]
        result[i]=score
        i+=1
    result = sorted(result.items(), key=itemgetter(1),reverse=True)
    return result
