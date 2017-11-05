import sys
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import gzip
import time
import gensim

def get_argument():
    input_argument=[]
    for i in range(len(sys.argv)-1):
        input_argument.append(sys.argv[i+1].lower())
    return input_argument

def search(input_query):
    start = time.clock()
    
    #다큐먼트의 크기가 매우 크므로, 원본은 압축상태로 저장해놓고 파일을 오픈하면서 압축을 푼다.
    path = "./data/NC_s.txt.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()

    #Series
    whole_news = pd.read_json(content.decode('utf-8'), typ='series', orient='records')
    original_data = pd.Series([{'title':news['title'], 'article':news['article']} for news in whole_news]
                                , index = [news['url'] for news in whole_news])
    
    query_docfied={'key':len(whole_news),'title':"",'article':input_query[0],"url":"","date":""}

    end1=time.clock()
    print("Read news(JSON) & Pandas Series Time: %s"%(end1-start))

    #저장되어있는 모델 로드
    model = Doc2Vec.load('model/doc2vec_s.model')
    end2=time.clock()
    print("Load Doc2Vec Model Time: %s"%(end2-end1))
    
    #입력된쿼리로 가장유사도높은 문서 검색하기
    infer_vector = model.infer_vector(input_query)
    docsim2 = model.docvecs.most_similar([infer_vector], topn = 10)
    
    end3=time.clock()
    print("Get most_similar Time: %s"%(end3-end2))

    # print results
    # most similar documents
    print('\nMost similar with \'%s\''%input_query)

    top10 = docsim2[:10]
    i=0
    for news in top10:
        i += 1
        value = original_data.loc[news[0]]
        print("%d."%i," %s"%value['title'])



if __name__ == "__main__":
    input_query = get_argument()
    print('Input query : ', input_query)

    search(input_query)
