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

def makeUpdatedDateNewsList(content,query,weight,topnumber):
    import tfidf
    #Tf-Idf 연산
    docs,doc_names= tfidf.read_doc(content)
    index, inverted_index = tfidf.index_doc(docs,doc_names)
    word_dictionary = tfidf.build_dictionary(inverted_index)
    doc_dictionary = tfidf.build_dictionary(index)
    tfidf_matrix = tfidf.compute_tfidf(index,word_dictionary,doc_dictionary)
    
    score_matrix = tfidf.score(tfidf_matrix,word_dictionary,doc_dictionary,query)

    #새로 입력된 데이터 기반 뉴스 리스트
    news_weight_list = []
    for news in content:
        doc_num = doc_dictionary[news['url']]
        weighted_score = score_matrix[doc_num][1]
        news_weight_list.append(NewsAndWeights(news, weighted_score))

    return news_weight_list[:topnumber]

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

    news_weight_list = makeListAndAddWeightSimilarity(content, similar_docs, WEIGHT_SIMILARITY)
    
    # 가중치 부여
    addWeightTermFrequency(news_weight_list, query, WEIGHT_TERM_FREQUENCY) #input_query: Tokenized 된 쿼리여야 함 ex. ['Trump', 'economy', 'polices']
    addWeightCategory(news_weight_list, content, query, WEIGHT_CATEGORY) #input_query: string 형태 ex. "Trump economy polices"
    addWeightLatest(news_weight_list, content, WEIGHT_LATEST)

    news_weight_list_updated= makeUpdatedDateNewsList(new_content,query,WEIGHT_ADDNEWEST,5) # 새로운 뉴스 기반 데이터
    sorted_docs_weight = sorted(news_weight_list, key=attrgetter('_weight'), reverse=True)

    return sorted_docs_weight,news_weight_list_updated

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
