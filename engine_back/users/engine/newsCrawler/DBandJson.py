'''
Add the new data to the pre-exiting Json files
and
Insert the new data into the DB
'''

import gzip
import pandas as pd
import shutil
import json
import os
import datetime
import pymysql
import MySQLdb
import codecs

def dateTransition(content):
    for one_set in content:
        year = int(one_set['date'][0:4])
        month = int(one_set['date'][4:6])
        day = int(one_set['date'][6:8])
        one_set['date'] = str(datetime.date(year,month,day))
    return content

def getItemsFromFiles():
    path = '../data/news_for_model.json.gz'
    with gzip.open(path, 'rb') as f:
        formodel = f.read()

    path_ = "./data/new_news.json"
    with open(path_,'rb') as g:
        new_news = g.read()
    
    #Open the pre-exisisting News Data
    
    whole_news = pd.read_json(formodel, typ='series', orient='records')
    model_data = pd.Series([news for news in whole_news], index = [news['url'] for news in whole_news])

    #Open the newly updated Data
    new_data =pd.read_json(new_news, typ='series', orient='records')
    newly_updated = pd.Series([news for news in new_data], index = [news['url'] for news in new_data])
    newly_updated = dateTransition(newly_updated) # Date 변환, 크로울링 과정으로 빼야할 필요

    for news in newly_updated:
        string = news['article']
        string.replace("'","`")
        string.replace('"','`')
        news['article']=string

    f.close()
    g.close()

    os.remove('./data/new_url.json')
    return model_data, newly_updated

def InsertIntoDB(original_data,contents):
    # DB에 넣은후 새로 업데이트된 data for model 리턴 
    today =datetime.date.today()

    conn = pymysql.connect(host='localhost', user='root', password='root', db='Crawled_Data', charset='utf8')
    #file updating
    i = 0
    for news in contents:
        if news['url'] not in original_data.keys():
            i+=1
            original_data[news['url']]=news
            title = news['title'].replace("'","\\'").replace('"','\\"')
            article = news['article'].replace("'","\\'").replace('"','\\"')
            with conn.cursor() as cursor:
                sql_query = "INSERT INTO `newArticle` (`id`,`title`,`date`,`url`,`category`,`article`) VALUES("+str(0)+",'"+title+"','"+str(today)+"','"+news['url']+"','"+news['category']+"','"+article+"')"    
                cursor.execute(sql_query)
            conn.commit()
    
    conn.close()
    '''
    with conn.cursor() as cursor:
        sql_query = "INSERT INTO `trans_log` (`id`,`date`,`type`,`number`) VALUES('')"    
        cursor.execute(sql_query)
   '''
    updated_json=[]
    for news in original_data:
        updated_json.append(news)
    
    return updated_json


def savetheDataForModel(updated_json):
    ## updated json file for the making model
    with open('../data/temp.json', 'w', encoding="utf-8") as make_file:
        json.dump(updated_json, make_file, ensure_ascii=False, indent="\t")
        
    with open('../data/temp.json', 'rb') as f_in:
        with gzip.open('../data/news_for_model.json.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    make_file.close()
    f_in.close()
    f_out.close()

    os.remove('../data/temp.json')
    os.remove('./data/new_news.json')
    return    

def DeletetheDBItem():
    conn = pymysql.connect(host='localhost', user='root', password='root', db='Crawled_Data', charset='utf8')
    with conn.cursor() as cursor:
        sql = 'DELETE FROM newArticle'
        cursor.execute(sql)
    conn.commit()
    conn.close()
    return

# 파일로드
original_data, newly_updated = getItemsFromFiles()

# 기존 DB 삭제
DeletetheDBItem()

# json 파일 연결 및 DB 삽입
updated_json =InsertIntoDB(original_data,newly_updated)

# json 파일 저장 및 임시 파일 삭제
savetheDataForModel(updated_json)



