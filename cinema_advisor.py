from models import Movie, List, Genre, Keyword, Base, Title
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
PROXY_API_URL = 'http://proxy.tekbreak.com/best/json'
DB_NAME = 'movies.db'
AMOUNT_OF_MOVIES = 1000
CODE_OVERCOME_REQUEST_LIMIT = 25

Session = sessionmaker(autoflush=False)


def fetch_proxy_list() -> list:
    response = requests.get(PROXY_API_URL)
    proxies = [proxy_json['ip'] for proxy_json in response.json()]
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
    response_json = requests.get(url, params=params, proxies=proxy).json()
    return response_json


def get_engine_and_initialize_db(Base) -> Engine:
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)
    return engine


def is_incomplete():
    sess = Session()
    how_many_movies_in_db = sess.query(Movie.movie_id).count()
    sess.close()
    return how_many_movies_in_db < AMOUNT_OF_MOVIES


def persist_data_to_db(movie_json) -> bool:
    sess = Session()
    keys = movie_json.keys()
    if sess.query(Movie).filter(Movie.movie_id == movie_json['id']).count() > 0:
        return False
    movie = Movie(movie_id=movie_json['id'], movie_title=movie_json['title'], vote_average=movie_json['vote_average'])
    movie.titles = [
        Title(title=record['title']) for record in movie_json['titles']
        ] if 'titles' in keys else []
    if len(movie.titles) == 0:
        movie.titles.append(Title(title=movie_json['title']))
        if movie_json['title'] != movie_json['original_title']:
            movie.titles.append(Title(title=movie_json['original_title']))
    sess.add(movie)
    if 'keywords' in keys:
        for record in movie_json['keywords']:
            if sess.query(Keyword).filter(Keyword.keyword_id == record[id]).count() == 0:
                keywrd = Keyword(keyword_id=record['id'], keyword=record['name'])
                keywrd.movies.append(movie)
                sess.add(keywrd)
            else:
                keywrd = sess.query(Keyword).filter(Keyword.keyword_id == record['id']).first()
                keywrd.movies.append(movie)
    if 'results' in keys:
        for record in movie_json['results']:
            if sess.query(List).filter(List.list_id == record['id']).count() == 0:
                movie_list = List(list_id=record['id'], list_title=record['name'])
                movie_list.movies.append(movie)
                sess.add(movie_list)
            else:
                movie_list = sess.query(List).filter(List.list_id == record['id']).first()
                movie_list.movies.append(movie)
    if 'genres' in keys:
        for record in movie_json['genres']:
            if sess.query(Genre).filter(Genre.genre_id == record['id']).count() == 0:
                genre = Genre(genre_id=record['id'], genre=record['name'])
                genre.movies.append(movie)
                sess.add(genre)
            else:
                genre = sess.query(Genre).filter(Genre.genre_id == record['id']).first()
                genre.movies.append(movie)
    sess.commit()
    sess.close()
    return True


def create_random_id_tmdb_list():
    return random.sample(range(2, 500000), k=10000)


def create_movie_json(id_tmdb, proxy_list):
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


def fetch_db():
    sess = Session()
    how_many_movies_in_db = sess.query(Movie).count()
    sess.close()
    ids_tmdb = create_random_id_tmdb_list()
    index = 0
    proxy_list = fetch_proxy_list()
    for _ in tqdm(range(AMOUNT_OF_MOVIES), total=AMOUNT_OF_MOVIES - how_many_movies_in_db, unit='movie'):
        while True:
            movie_json = create_movie_json(ids_tmdb[index], proxy_list)
            index += 1
            if movie_json:
                if persist_data_to_db(movie_json):
                    is_incomplete()
                    break


def get_similar_titles_movies_list(movie_title) -> list:
    sess = Session()
    similar_titles = sess.query(Title).filter(Title.title.like('%{}%'.format(movie_title))).all()
    movies = set(title.movie for title in similar_titles)
    sess.close()
    return list(movies)


def find_the_most_similar_ones(movie_title, similar_movies):
    return [movie.title for movie in similar_movies]

if __name__ == '__main__':
    print("Welcome to SBKubric's Cinema Advisor!")
    engine = get_engine_and_initialize_db(Base)
    Session.configure(bind=engine)
    if is_incomplete():
        print('Fetching the database...')
        fetch_db()
    print('OK')
    movie_title = input('Please, enter the name of the movie that would be a pivot: ')
    print('Searching for similar titles...')
    similar_movies = get_similar_titles_movies_list(movie_title)
    print('Building a recommendations list...')
    recommendations_list = find_the_most_similar_ones(movie_title, similar_movies)
    print('The recommended films:')
    pprint(recommendations_list)
