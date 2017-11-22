
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')


import multiprocessing
import os
import string
import gzip
import pandas as pd
import re
from gensim import corpora
from nltk.tokenize import word_tokenize
import re
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import time

def make_model(sentences):
    whole_news = pd.read_json(content, typ='series', orient='records')

    docs = []
    start = time.clock()
    for news in whole_news:
        id = news['url']
        value = re.sub('[!"#%\'()*+,./:;<=>?@\[\]\\xa0$^_`{|}~’”“′‘\\\]',' ', news['title'].lower()+". "+news['article'].lower())
        value = word_tokenize(value)
        T = TaggedDocument(value, [id])
        docs.append(T)

    end1 = time.clock()
    print("데이터 전처리: %s"%(end1-start))

    #print(docs[:4])

    # initialize a model
    model = Doc2Vec(size=100, window=1, alpha=0.025, min_alpha=0.025, min_count=0, dm=0, workers=multiprocessing.cpu_count())

    # build vocabulary
    model.build_vocab(docs)
    end2 = time.clock()
    print("Doc2Vec Model 만드는데 걸린 시간: %s"%(end2-end1))

    # get the initial document vector, and most similar articles
    # (before training, the results should be wrong)
    docvec1 = model.docvecs[0]
    docvecsyn1 = model.docvecs.doctag_syn0[0]
    docsim1 = model.docvecs.most_similar(whole_news.keys()[0])

    # train this model
    model.train(docs, total_examples=len(docs), epochs=20)
    end3 = time.clock()
    print("트레이닝 반복 20번 하는데 걸린 시간: %s"%(end3-end2))

    # get the trained document vector, and most similar articles
    # (after training, the results should be correct)
    docvec2 = model.docvecs[0]
    docvecsyn2 = model.docvecs.doctag_syn0[0]
    docsim2 = model.docvecs.most_similar(whole_news.keys()[0])

    # print results
    # document vector
    print('Document vector:')

    # before training
    print('(Before training)')
    print(docvec1[:5])
    print(docvecsyn1[:5])

    # we can see that, the document vectors do not change after the training.
    print('(After training, exactly the same.)')
    print(docvec2[:5])
    print(docvecsyn2[:5])

    # most similar documents
    print('\nMost similar with \'%s\''%whole_news[0]['title'])

    # before training, the result is wrong. after training, correct. good.
    print('(Before training)')
    print(docsim1[:5])

    print('(After training, significantly changed)')
    print(docsim2[:5])


    model.save('model/doc2vec_NC_70mb_size100.model')

    return model

if __name__ == '__main__':

    path = "./data/NC_70mb.json.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()
    make_model(content.decode('utf-8'))
