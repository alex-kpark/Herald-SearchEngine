
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

import gensim
import multiprocessing
import os
import json
import string
from nltk.corpus import stopwords


def make_model():

    sentences_vocab = gensim.models.word2vec.Text8Corpus('./traindata')
    #print(sentences_vocab)
    #sentences_vocab = SentenceReader('./docs')
    #sentences_train = SentenceReader('./docs')

    config = {
        'min_count': 5,  # 등장 횟수가 5 이하인 단어는 무시
        'size': 200,  # 200차원짜리 벡터스페이스에 embedding
        'sg': 1,  # 0이면 CBOW, 1이면 skip-gram을 사용한다
        'batch_words': 10000,  # 사전을 구축할때 한번에 읽을 단어 수
        'iter': 10,  # 보통 딥러닝에서 말하는 epoch과 비슷한, 반복 횟수
        'workers': multiprocessing.cpu_count(),
    }
    model = gensim.models.word2vec.Word2Vec(sentences_vocab)
    #model.build_vocab(sentences_vocab)
    #model.train(sentences_train)

    model.save('model/word2vec.model')
    print('Saved')

    return model

if __name__ == '__main__':

    model = make_model()
