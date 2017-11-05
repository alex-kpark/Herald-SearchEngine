import sys
import os
import numpy as np
import operator
import string
from gensim import models, corpora, similarities
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import gzip
import re
import time

def get_argument():
    input_argument=[]
    for i in range(len(sys.argv)-1):
        input_argument.append(sys.argv[i+1].lower())
    return input_argument

def search(input_query):
    start = time.clock()

    #다큐먼트의 크기가 매우 크므로, 원본은 압축상태로 저장해놓고 파일을 오픈하면서 압축을 푼다.
    path = "./data/NC_100mb.txt.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()

    #저장되어있는 모델 로드
    model = models.Word2Vec.load('model/word2vec_100mb.model')
    end1=time.clock()
    print("Load Word2Vec Model Time: %s"%(end1-start))

    #모델 내에 존재하는 Voca.인지 확인
    exist_in_model_query = [q for q in input_query if q in model.wv.vocab.keys()]
    print('Exist voca : ', exist_in_model_query)

    #유사도높은 단어 30개를 뽑아서, Stopwords가 아닌 것을 걸러내고 상위 2개를 추출
    stopwrds = stopwords.words('english')
    stopwrds.extend(['us','also'])
    similar_word = model.most_similar(positive=exist_in_model_query,topn=20)
    similar_word = [ sw for sw in similar_word if sw[0] is not None and sw[0] not in stopwrds]
    new_query = exist_in_model_query[:]
    new_query.extend(sw[0] for sw in similar_word[:2])
    print('New query : ', new_query)
    end2=time.clock()
    print("Get most_similar Time: %s"%(end2-end1))

    #Series
    #key: url / value: title, article
    whole_news = pd.read_json(content.decode('utf-8'), typ='series', orient='records')
    original_data = pd.Series((re.sub('[!"#%\'()*+,-./:;<=>?@\[\]\\xa0$^_`{|}~1234567890’”“′‘\\\]',' ', news['title']+" "+news['article']) for news in whole_news)
                                , index = [news['url'] for news in whole_news])
    end3=time.clock()
    print("Read news(JSON) & Pandas Series Time: %s"%(end3-end2))

    #Lower & Tokenizing
    processed_data = original_data.apply(lambda x: str(x).lower())
    processed_data = processed_data.apply(lambda x: word_tokenize(x))
    dictionary = corpora.Dictionary(processed_data.values)
    end4=time.clock()
    print("Lower & Tokenizing & Dictionary Time: %s"%(end4-end3))
    print(dictionary)
    corpus = [dictionary.doc2bow(doc) for doc in processed_data.values]

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    #vec_bow = dictionary.doc2bow(input_query)
    #vec_tfidf = tfidf[vec_bow]

    #print(vec_bow)
    #print(tfidf[vec_bow])
    #print(dictionary.items())

if __name__ == "__main__":
    input_query = get_argument()
    print('Input query : ', input_query)

    search(input_query)
