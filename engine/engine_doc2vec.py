import sys
import pandas as pd
import re
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from datetime import date
import numpy as np
import gzip
import time
import gensim
from gensim import corpora, models, similarities

from operator import attrgetter
import math

class NewsAndWeights(object):
    def __init__(self,news,weight=0):
        self.news = news
        self._weight = weight
    def addWeight(self, weight):
        self._weight += weight
    def getNews(self):
        return self.news
    def getWeight(self):
        return self._weight
    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__,
                                  self._weight)
    def __cmp__(self, other):
        if hasattr(other, 'getKey'):
            return self.getKey().__cmp__(other.getKey())

def TF_IDF_News(original_data,givenlist,query,weight):
    import tfidf
    selected_data = pd.Series([original_data[news.news['url']] for news in givenlist], index = [news.news['url'] for news in givenlist])

    docs,doc_names= tfidf.read_doc(selected_data)
    index, inverted_index = tfidf.index_doc(docs,doc_names)
    word_dictionary = tfidf.build_dictionary(inverted_index)
    doc_dictionary = tfidf.build_dictionary(index)
    tfidf_matrix = tfidf.compute_tfidf(index,word_dictionary,doc_dictionary)
    score_matrix = tfidf.score(tfidf_matrix,word_dictionary,doc_dictionary,query)

    for news in givenlist:
        doc_num = doc_dictionary[news.news['url']]
        weighted_score = score_matrix[doc_num][1]
        news.addWeight(weighted_score)
    return givenlist

def search(model, content, new_content, query):
    #merged_data = original_data_newest.append(original_data)

    infer_vector = model.infer_vector(query)
    similar_docs = model.docvecs.most_similar([infer_vector], topn = 200)

    # TODO: 상수값 조정
    WEIGHT_SIMILARITY = 2.0
    WEIGHT_ADDNEWEST = 1.0
    WEIGHT_TERM_FREQUENCY = 0.05
    WEIGHT_LATEST = 0.4
    WEIGHT_CATEGORY = 0.3
    WEIGHT_TF_IDF=0.4 # TFIDF WEIGHT

    news_weight_list = makeListAndAddWeightSimilarity(content, similar_docs, WEIGHT_SIMILARITY)
    addWeightTermFrequency(news_weight_list, query, WEIGHT_TERM_FREQUENCY) #input_query: Tokenized 된 쿼리여야 함 ex. ['Trump', 'economy', 'polices']
    addWeightCategory(news_weight_list, content, query, WEIGHT_CATEGORY) #input_query: string 형태 ex. "Trump economy polices"
    addWeightLatest(news_weight_list, content, WEIGHT_LATEST)

    #news_weight_list = addNewsToWeightList(new_content,news_weight_list, WEIGHT_ADDNEWEST)
    #news_weight_list = TF_IDF_News(merged_data,news_weight_list,query,WEIGHT_TF_IDF)
    #ADD New newslist to the list

    sorted_docs_weight = sorted(news_weight_list, key=attrgetter('_weight'), reverse=True)

    return sorted_docs_weight

def makeListAndAddWeightSimilarity(original_data, similar_docs, weight):
    news_weight_list = []
    for idx, s in enumerate(similar_docs):
        similarity = s[1] #similarity
        news = original_data.loc[s[0]] #key of dict: URL of news
        news_weight_list.append(NewsAndWeights(news, similarity * weight))

    return news_weight_list

def addWeightLatest(newsAndWeights, original_data, weight):
    today = date.today()
    for nw in newsAndWeights:
        delta = 1/math.log((today-nw.news['date']).days)*weight*10
        nw.addWeight(delta)
    return

def addWeightCategory(newsAndWeights, content, input_query, weight):
    import classifier
    string_query = ""
    for query in input_query:
        text = re.sub('[!"#%\'()*+,./:;<=>?@\[\]\\xa0$^_`{|}~’”“′‘\\\]',' ', query.lower())
        string_query += query + " "
    predicted_category = classifier.predict_category(content, [string_query])
    for nw in newsAndWeights:
        if nw.news['category'] == predicted_category[0]:
            nw.addWeight(weight)
    return

def addWeightTermFrequency(newsAndWeights, input_query, weight):
    for terms in input_query:
        for nw in newsAndWeights:
            count = nw.news['title'].count(terms) + nw.news['article'].count(terms)
            nw.addWeight(count * weight)
    return

# TODO:
def addNewsToWeightList(original_data,givenlist,weight):
    news_weight_list = givenlist
    for url in original_data.keys():
        news=original_data.loc[url]
        news_weight_list.append(NewsAndWeights(news,weight))
    return news_weight_list

'''
if __name__ == "__main__":
    input_query = get_argument()
    print('Input query : ', input_query)

    content = read_JSON('./data/NC_70mb.json.gz')
    new_content = read_JSON('./data/NC_s.txt.gz')
    search(content, new_content, input_query)
'''
