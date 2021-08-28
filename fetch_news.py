from newsapi.newsapi_client import NewsApiClient
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from sqlalchemy import exc
from news_sentinel import db
from news_sentinel.models import News

import joblib
# import pickle
from news_sentinel.feature import *
import json
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
pipeline = joblib.load('news_sentinel/pipeline.sav')


def db_connection():
    con = sqlite3.connect('database.sqlite', timeout=10)
    return con


def get_news():
    news_api = NewsApiClient(api_key='e90a7baafb6a4ee49b6d36d055d62a35')

    today_date = datetime.today().strftime('%Y-%m-%d')
    old_date = datetime.now() - timedelta(days=29)
    old_date = old_date.strftime('%Y-%m-%d')

    # /v2/everything
    all_articles = news_api.get_everything(q='trump biden hillary clinton politics affairs protests ',
                                           sources='al-jazeera-english,ars-technica,axios,bloomberg,'
                                                   'engadget,msnbc,fortune,abc-news,buzzfeed',
                                           domains='http://www.aljazeera.com,http://arstechnica.com,'
                                                   'https://www.axios.com,http://www.bloomberg.com,'
                                                   'https://www.engadget.com,http://www.msnbc.com,'
                                                   'http://fortune.com,https://abcnews.go.com,https://www.buzzfeed.com',
                                           from_param=old_date,
                                           to=today_date,
                                           language='en',
                                           sort_by='relevancy',
                                           page=1)

    df = pd.DataFrame(all_articles['articles'])
    # print(df)
    # df.to_csv('news.csv')

    num_of_rows = 0

    for row in df.itertuples(index=True, name='Pandas'):
        print(row.title)
        author = row.author
        title = row.title
        image = row.urlToImage
        date = row.publishedAt
        date = date[:10]

        query = get_all_query(title, author)
        pred = pipeline.predict(query)
        prediction = pred[0]
        print(prediction)

        news = News(title=title, author=author, image=image, date=date, pred=int(prediction))
        if len(title) > 20:
            db.session.add(news)
            try:
                db.session.commit()
                num_of_rows = num_of_rows + 1
                print('value inserted')
            except exc.SQLAlchemyError as e:
                print(type(e))
                print(e)
                print('Error inserting')
                db.session.rollback()
                continue
        else:
            continue

    return num_of_rows


if __name__ == '__main__':
    rows = get_news()
    print("Number of rows entered")
    print(rows)
