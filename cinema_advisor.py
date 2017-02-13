from models import Movie, List, Genre, Keyword, Base,
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select
from sqlalchemy.orm.session import sessionmaker
import json
from pprint import pprint
from sqlite3 import Connection, DatabaseError

import random
import requests
from tqdm import tqdm

from models import Movie

API_KEY_V3 = 'ea49129df62d63a56dc7324f7186f7fc'
PROXY_API_URL = 'http://www.freeproxy-list.ru/api/proxy'
DB_NAME = 'movies.db'
AMOUNT_OF_MOVIES = 10

Session = sessionmaker(autoflush=False)


def fetch_proxy_list() -> list:
    params = {'anonymity': 'false',
              'token': 'demo'}
    response = requests.get(PROXY_API_URL, params=params).text
    proxies = response.split('\n')
    return proxies


def make_tmdb_api_request(method, api_key, proxy_list, *, extra_params=None) -> dict:
    extra_params = extra_params or {}
    url = 'https://api.themoviedb.org/3{}'.format(method)
    params = {
        'api_key': api_key,
        'language': 'ru',
    }
    params.update(extra_params)
    proxy = {"http": random.choice(proxy_list)}
    response = requests.get(url, params=params, proxies=proxy)
    return response.json()


def get_engine_and_initialize_db(Base) -> Engine:
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)
    return engine


def is_incomplete():
    sess = Session()
    movies = sess.query(Movie).order_by(Movie.movie_id)
    return len(movies) < AMOUNT_OF_MOVIES


def persist_data_to_db(movie_object, db_connection) -> bool:
    pass

def create_random_id_tmdb_list():
    return random.sample(range(2, 500000), k=10000)


def create_movie_json(id_tmdb):
    proxy_list = fetch_proxy_list()
    movie_json = make_tmdb_api_request(
        method='/movie/{}'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    keywords = make_tmdb_api_request(
        method='/movies/{}/keywords'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    movie_json.update(keywords)
    lists = make_tmdb_api_request(
        method='/movies/{}/lists'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    movie_json.update(lists)
    alternative_titles = make_tmdb_api_request(
        method='/movies/{}/alternative_titles'.format(id_tmdb),
        api_key=API_KEY_V3, proxy_list=proxy_list
    )
    movie_json.update(alternative_titles)
    if 'id' in movie_json.keys():
        return movie_json
    return None


def fetch_db(Base, engine):
    sess = Session()
    movies = sess.query(Movie).order_by(Movie.movie_id)
    ids_tmdb = create_random_id_tmdb_list()
    index = 0
    for _ in tqdm(range(AMOUNT_OF_MOVIES), total=AMOUNT_OF_MOVIES - len(movies), unit='movie'):
        while True:
            json_movie = create_movie_json(ids_tmdb[index])
            index += 1
            if json_movie:
                persist_data_to_db(json_movie)
                break
    return db_connection


def fetch_movie_values_frm_db(table_movie_id, db_connection) -> dict:
    cursor = db_connection.cursor()
    cursor.execute('SELECT * FROM movie WHERE movie.id=?', (table_movie_id,))
    return  cursor.fetchone()



def get_similar_titles_ids_list(movie_title, db_connection) -> list:
    cursor = db_connection.cursor()
    cursor.execute(
        'SELECT movie_id FROM titles WHERE movie_title LIKE ?;', ('%{}%'.format(movie_title),)
    )
    return cursor.fetchall()


def fetch_movie_frm_db(pivot_id, db_connection) -> Movie:
    values = fetch_movie_values_frm_db(pivot_id, db_connection)
    movie_model = Movie()
    movie_model.movie_id, = values[0]
    movie_model.title_id = values[1]








def create_json_list_frm_db_entries(similar_titles_ids_list):
    pass


def get_recommendations_list_frm_db(pivot_json, movies_json_list):
    pass




if __name__ == '__main__':
    # proxy_list = fetch_proxy_list()
    # json_300_spartan_details = make_tmdb_api_request(method='/movie/69892', api_key=API_KEY_V3, proxy_list=proxy_list)
    # pprint(json_300_spartan_details)
    # print('\n\n')
    # json_300_spartan_keywords = make_tmdb_api_request(method='/movie/69892/keywords', api_key=API_KEY_V3, proxy_list=proxy_list)
    # json_300_spartan_details.update(json_300_spartan_keywords)
    # json_300_spartan_alternative_titles = make_tmdb_api_request(method='/movie/69892/alternative_titles', api_key=API_KEY_V3, proxy_list=proxy_list)
    # json_300_spartan_details.update(json_300_spartan_alternative_titles)
    # json_300_spartan_user_lists = make_tmdb_api_request(method='/movie/69892/lists', api_key=API_KEY_V3, proxy_list=proxy_list)
    # json_300_spartan_details.update(json_300_spartan_user_lists)
    # pprint(json_300_spartan_details)

    print("Welcome to SBKubric's Cinema Advisor!")
    engine = get_engine_and_initialize_db(Base)
    Session.configure(bind=engine)
    if is_incomplete():
        print('Fetching the database...')
        fetch_db()
    print('OK')
    # movie_title = input('Please, enter the name of the movie that would be a pivot: ')
    # print('Searching for similar titles...')
    # similar_titles_ids_list = get_similar_titles_ids_list(movie_title, db_connection)
    # print('Fetching the data of similar titles...')
    # movies_json_list = create_json_list_frm_db_entries(similar_titles_ids_list)
    # print('Building a recommendations list...')
    # recommendations_list = get_recommendations_list_frm_db(pivot_json, movies_json_list)
    # db_connection.close()
    # print('The recommended films:')
    # pprint(recommendations_list)
    # print(similar_titles_ids_list)
