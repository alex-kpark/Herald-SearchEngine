import sys
import json
import string

def read_news(path):
    '''
    웹에서 불러올 때
    url = 'http://~~'
    raw = urllib.urlopen(url)
    json_object = json.loads(raw)
    '''
    file = open(path, 'rt', encoding='utf-8')
    content = file.read()

    whole_news = json.loads(content)

    return whole_news

def assort_only_article(whole_news):

    only_article = ""
    for news in whole_news:
        only_article += news['article']

    #stopwrds = stopwords.words('english')
    #if(similar_word[c][0] not in stopwrds):
    #    query.append(similar_word[c][0])

    return only_article

if __name__ == '__main__':

    path = "./Data2/newsCrawl_s.json"
    whole_news = read_news(path)
    only_article = assort_only_article(whole_news)

    ft = open("./traindata","w+", encoding='utf-8')
    ft.write(only_article)
    ft.close()
