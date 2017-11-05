
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
import multiprocessing
import os
import string
import gzip
import pandas as pd
import re
from gensim import corpora
from nltk.tokenize import word_tokenize

def make_model(sentences):
    whole_news = pd.read_json(content, typ='series', orient='records')

    sentences = pd.Series(re.sub('[!"#%\'()*+,-./:;<=>?@\[\]\\xa0$^_`{|}~1234567890’”“′‘\\\]',' ', news['title']+" "+news['article']) for news in whole_news)

    sentences = sentences.apply(lambda x: str(x).lower())
    sentences = sentences.apply(lambda x: word_tokenize(x))

    dictionary = corpora.Dictionary(sentences)
    corpus = [dictionary.doc2bow(doc) for doc in sentences]

    config = {
        'min_count': 5,  # 등장 횟수가 5 이하인 단어는 무시
        'size': 200,  # 200차원짜리 벡터스페이스에 embedding
        'sg': 1,  # 0이면 CBOW, 1이면 skip-gram을 사용한다
        'batch_words': 10000,  # 사전을 구축할때 한번에 읽을 단어 수
        'iter': 10,  # 보통 딥러닝에서 말하는 epoch과 비슷한, 반복 횟수
        'workers': multiprocessing.cpu_count(),
    }
    model = gensim.models.word2vec.Word2Vec(sentences.values, size=200, window=5, iter=10, min_count=5, workers=multiprocessing.cpu_count())
    model.save('model/word2vec_100mb.model')
    print('Saved')

    return model

if __name__ == '__main__':
    
    path = "./data/NC_100mb.txt.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()
    make_model(content.decode('utf-8'))



    '''
    file = open('./data/NC_100mb.json', 'rt', encoding='utf-8')
    content = file.read()

    f = gzip.open('./data/NC_100mb.txt.gz', 'wb')
    f.write(content.encode('utf-8'))
    f.close()
    '''
