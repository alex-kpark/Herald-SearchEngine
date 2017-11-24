import sys
import pandas as pd
import re
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from datetime import date
import numpy as np
import gzip
import time
import gensim
from gensim import corpora, models, similarities
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter, attrgetter
import math

def get_argument():
    input_argument = []
    for i in range(len(sys.argv) - 1):
        input_argument.append(sys.argv[i + 1].lower())
    return input_argument

def read_JSON(path):
    with gzip.open(path, 'rb') as f:
        content = f.read()
    return content.decode('utf-8')

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
        return '{}: {} {} {}'.format(self.__class__.__name__,
                                  self.news['title'],
                                  self.news['date'],
                                  self._weight)
    def __cmp__(self, other):
        if hasattr(other, 'getKey'):
            return self.getKey().__cmp__(other.getKey())

def dateTransition(content):    
    for one_set in content:
        year = int(one_set['date'][0:4])
        month = int(one_set['date'][4:6])
        day = int(one_set['date'][6:8])
        one_set['date'] = datetime.date(year,month,day)
    return content

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

def search(content, new_content, query):
    # Series
    whole_news = pd.read_json(content, typ='series', orient='records')
    original_data = pd.Series([news for news in whole_news], index = [news['url'] for news in whole_news])
    original_data = dateTransition(original_data) # Date 변환, 크로울링 과정으로 빼야할 필요
    
    whole_news_newest = pd.read_json(new_content, typ='series', orient='records')
    original_data_newest = pd.Series([news for news in whole_news_newest], index = [news['url'] for news in whole_news_newest])
    original_data_newest = dateTransition(original_data_newest) # Date 변환, 크로울링 과정으로 빼야할 필요

    merged_data = original_data_newest.append(original_data)
    
    # Word2Vec을 이용해 관련도높은 단어 추출 (Hidden Query 생성)
    # -> 정확도측면에서 효과 미비하여 Deprecated
    # similar_word = similar_words_as_word2vec(input_query)
    # input_query.extend(sw[0] for sw in similar_word[:1])

    # Load Doc2Vec model
    model = Doc2Vec.load('model/doc2vec_NC_70mb.model')

    infer_vector = model.infer_vector(query)
    similar_docs = model.docvecs.most_similar([infer_vector], topn = 200)

    # TODO: 상수값 조정
    WEIGHT_SIMILARITY = 1.0
    WEIGHT_ADDNEWEST = 1.0
    WEIGHT_TERM_FREQUENCY = 0.05
    WEIGHT_LATEST = 0.4
    WEIGHT_CATEGORY = 0.3
    WEIGHT_TF_IDF=0.4 # TFIDF WEIGHT
    
    news_weight_list = makeListAndAddWeightSimilarity(original_data, similar_docs, WEIGHT_SIMILARITY)
    news_weight_list = addNewsToWeightList(original_data_newest,news_weight_list, WEIGHT_ADDNEWEST)
   
    news_weight_list = TF_IDF_News(merged_data,news_weight_list,query,WEIGHT_TF_IDF)
    #ADD New newslist to the list

    addWeightTermFrequency(news_weight_list, query, WEIGHT_TERM_FREQUENCY) #input_query: Tokenized 된 쿼리여야 함 ex. ['Trump', 'economy', 'polices']
    addWeightCategory(news_weight_list, content, query, WEIGHT_CATEGORY) #input_query: string 형태 ex. "Trump economy polices"
    addWeightLatest(news_weight_list, original_data, WEIGHT_LATEST)
    
    sorted_docs_weight = sorted(news_weight_list, key=attrgetter('_weight'), reverse=True)

    return sorted_docs_weight

def makeListAndAddWeightSimilarity(original_data, similar_docs, weight):
    news_weight_list = []
    for idx, s in enumerate(similar_docs):
        similarity = s[1] #similarity
        news = original_data.loc[s[0]] #key of dict: URL of news
        news_weight_list.append(NewsAndWeights(news, similarity * weight))
    
    return news_weight_list

def addNewsToWeightList(original_data,givenlist,weight):
    news_weight_list = givenlist
    for url in original_data.keys():
        news=original_data.loc[url]
        news_weight_list.append(NewsAndWeights(news,weight))
    return news_weight_list

def addWeightTermFrequency(newsAndWeights, input_query, weight):
    for terms in input_query:
        for nw in newsAndWeights:
            count = nw.news['title'].count(terms) + nw.news['article'].count(terms)
            nw.addWeight(count * weight)
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

def addWeightLatest(newsAndWeights, original_data, weight): 
    today = datetime.date.today()
    for nw in newsAndWeights:
        delta = 1/math.log((today-nw.news['date']).days)*weight*10
        nw.addWeight(delta)
    return

def similar_words_as_word2vec(input_query):
    #저장되어있는 모델 로드
    word2VecModel = gensim.models.Word2Vec.load('model/word2vec_100mb.model')

    #모델 내에 존재하는 Voca.인지 확인
    exist_in_model_query = [q for q in input_query if q in word2VecModel.wv.vocab.keys()]

    #유사도높은 단어 30개를 뽑아서, Stopwords가 아닌 것을 걸러내고 상위 2개를 추출
    stopwrds = stopwords.words('english')
    stopwrds.extend(['us','also'])
    similar_word = word2VecModel.most_similar(positive=exist_in_model_query,topn=20)
    similar_word = [ sw for sw in similar_word if sw[0] is not None and sw[0] not in stopwrds]
    #new_query = exist_in_model_query[:]
    #new_query.extend(sw[0] for sw in similar_word[:1])
    return similar_word

if __name__ == "__main__":
    input_query = get_argument()
    print('Input query : ', input_query)

    content = read_JSON('./data/NC_70mb.json.gz')
    new_content = read_JSON('./data/NC_s.txt.gz')

    search(content, new_content, input_query)

