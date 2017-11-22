import sys
import pandas as pd
import re
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import gzip
import time
import gensim

def get_argument():
    input_argument=[]
    for i in range(len(sys.argv)-1):
        input_argument.append(sys.argv[i+1].lower())
    return input_argument

def read_JSON(path):
    with gzip.open(path, 'rb') as f:
        content = f.read()
    return content.decode('utf-8')

def search(input_query):
    # Word2Vec을 이용해 관련도높은 단어 추출 (Hidden Query 생성)
    # -> 정확도측면에서 효과 미비하여 Deprecated
    #similar_word = similar_words_as_word2vec(input_query)
    #input_query.extend(sw[0] for sw in similar_word[:1])

    path = "./data/NC_70mb.json.gz"
    content = read_JSON(path)

    #Series
    whole_news = pd.read_json(content, typ='series', orient='records')
    original_data = pd.Series([{'title':news['title'], 'article':news['article']} for news in whole_news]
                                , index = [news['url'] for news in whole_news])

    #저장되어있는 모델 로드
    model = Doc2Vec.load('model/doc2vec_NC_70mb.model')
    #end2=time.clock()
    #print("Load Doc2Vec Model Time: %s"%(end2-end1))

    #입력된 쿼리와 유사도높은 문서 추출
    infer_vector = model.infer_vector(input_query)
    similar_docs = model.docvecs.most_similar([infer_vector], topn = 10)

    # most similar Top10 documents
    print('\nMost similar with \'%s\''%input_query)
    for idx, news in enumerate(similar_docs[:10]):
        key = news[0] #key: URL of news
        article = original_data.loc[key]
        print("%d."%idx," %s"%article['title'],"  /  Similarity: %f"%news[1])

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

    search(input_query)
