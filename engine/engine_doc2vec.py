import sys
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import gzip
import time
import gensim
import numpy as np
import pickle 
import operator

def get_argument():
    input_argument=[]
    for i in range(len(sys.argv)-1):
        input_argument.append(sys.argv[i+1].lower())
    return input_argument

def search(input_query):
    start = time.clock()
    
    #다큐먼트의 크기가 매우 크므로, 원본은 압축상태로 저장해놓고 파일을 오픈하면서 압축을 푼다.
    path = "./data/NC_70mb.txt.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()

    #Series
    whole_news = pd.read_json(content.decode('utf-8'), typ='series', orient='records')
    original_data = pd.Series([{'title':news['title'], 'article':news['article'], 'category':news['category'], 'url':news['url']} for news in whole_news]
                                , index = [news['url'] for news in whole_news])
    
    query_docfied={'key':len(whole_news),'title':"",'article':input_query[0],"url":"","date":""}

    end1=time.clock()
    print("Read news(JSON) & Pandas Series Time: %s"%(end1-start))

    #저장되어있는 모델 로드
    model = Doc2Vec.load('model/doc2vec_70mb.model')
    end2=time.clock()
    print("Load Doc2Vec Model Time: %s"%(end2-end1))
    
    #Word2Vec 모델 로드
    model_word = gensim.models.Word2Vec.load("model/word2vec_70mb.model")
    end3 = time.clock()
    print("Load Word2Vec Model Time: %s"%(end3-end2))
  
    '''
    target_query=[]

    for word in input_query:
        if word in model_word.wv.vocab:
            target_query.append(word)

    related_words=model_word.most_similar(positive=target_query, topn=5)
    for new_word in related_words:
        input_query.append(new_word[0])                
    '''    
  
    #새로운 쿼리 or 기존 쿼리로 가장유사도높은 문서 검색하기
    print("New Query : %s"%input_query)
    print()
    infer_vector = model.infer_vector(input_query)
    docsim2 = model.docvecs.most_similar([infer_vector], topn = 200)
    
    end4=time.clock()
    print("Get most_similar Time: %s"%(end4-end3))

    # print results
    # most similar documents
    print('\nMost similar with \'%s\''%input_query)
    print()

    top = docsim2[:200]
    i=0
    docs={}
    docs_weight={}
    
    for news in top:
        i += 1
        value = original_data.loc[news[0]]
        docs[value['url']] = value['article']
        docs_weight[value['url']]=0
    
    for terms in input_query:
        for doc in docs:
            number=0
            docs_weight[doc] += docs[doc].count(terms)
    sorted_docs_weight=sorted(docs_weight.items(), key=operator.itemgetter(1),reverse=True)

    i=0
    for news in sorted_docs_weight:
        i += 1
        value = original_data.loc[news[0]]
        print("%d."%i," %s"%value['title']," %s"%value['category'])

    final=time.clock()
    print("Total Time: %s"%(final-start))

if __name__ == "__main__":
    input_query = get_argument()
    print('Input query : ', input_query)

    search(input_query)
    #classification(input_query)


