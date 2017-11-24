import sys
import gzip

import classifier
import engine_doc2vec

i=1

def get_argument():
    input_argument = []
    for i in range(len(sys.argv) - 1):
        input_argument.append(sys.argv[i + 1].lower())
    return input_argument

if __name__ == '__main__':
    input_query = get_argument()

    path = "./data/NC_70mb.json.gz"
    with gzip.open(path, 'rb') as f:
        content = f.read()
    
    sorted_docs_weight = engine_doc2vec.search(content.decode('utf-8'), input_query)

    for idx, news_weight in enumerate(sorted_docs_weight[:20]):
        news = news_weight.getNews()
        print("%d." % (idx+1)," %s" % news['title']," %s" % news['category'], " weight: %f" % news_weight.getWeight())
