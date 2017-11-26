import sys
import gzip
import pandas as pd
import datetime
import classifier
import engine_doc2vec
from gensim.models.doc2vec import Doc2Vec

def get_argument():
    input_argument = []
    for i in range(len(sys.argv) - 1):
        input_argument.append(sys.argv[i + 1].lower())
    return input_argument

def read_JSON(path):
    with gzip.open(path, 'rb') as f:
        content = f.read()
    return content.decode('utf-8')

def dateTransition(content):
    for one_set in content:
        year = int(one_set['date'][0:4])
        month = int(one_set['date'][4:6])
        day = int(one_set['date'][6:8])
        one_set['date'] = datetime.date(year,month,day)
    return content

if __name__ == '__main__':
    input_query = get_argument()

    path = './data/news.json.gz'
    with gzip.open(path, 'rb') as f:
        content = f.read()
    whole_news = pd.read_json(content, typ='series', orient='records')
    json_content = pd.Series([news for news in whole_news], index = [news['url'] for news in whole_news])
    json_content = dateTransition(json_content) # Date 변환, 크로울링 과정으로 빼야할 필요

    path2 = './data/news_s.json.gz'
    with gzip.open(path2, 'rb') as f2:
        new_content = f2.read()
    whole_news_newest = pd.read_json(new_content.decode('utf-8'), typ='series', orient='records')
    new_json_content = pd.Series([news for news in whole_news_newest], index = [news['url'] for news in whole_news_newest])
    new_json_content = dateTransition(new_json_content) # Date 변환, 크로울링 과정으로 빼야할 필요

    model = Doc2Vec.load('model/doc2vec.model')

    sorted_docs_weight = engine_doc2vec.search(model, json_content, new_json_content, input_query)


    for idx, news_weight in enumerate(sorted_docs_weight[:20]):
        news = news_weight.getNews()
        print("%d." % (idx+1)," %s" % news['title']," %s" % news['category'], " weight: %f" % news_weight.getWeight())
