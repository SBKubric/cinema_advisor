from models import Movie, List, Genre, Keyword, Base, Title
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import sessionmaker
from collections import  OrderedDict
import time
from pprint import pprint

import random
import requests
from tqdm import tqdm


API_KEY_V3 = 'ea49129df62d63a56dc7324f7186f7fc'
PROXY_API_URL = 'http://proxy.tekbreak.com/best/json'
DB_NAME = 'movies.db'
AMOUNT_OF_MOVIES = 1000
CODE_OVERCOME_REQUEST_LIMIT = 25
RECOMMENDATIONS_LIST_SIZE = 10
PREFERRED_LANGUAGE = 'RU'

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


def is_incomplete(sess):
    how_many_movies_in_db = sess.query(Movie.movie_id).count()
    return how_many_movies_in_db < AMOUNT_OF_MOVIES


def get_movie_frm_json_if_not_in_db(movie_json, sess) -> (Movie, Session):
    if sess.query(Movie).filter(Movie.movie_id == movie_json['id']).count() == 0:
        movie_title = movie_json['title']
        for title in movie_json['titles']:
            if PREFERRED_LANGUAGE in title.values():
                movie_title = title['title']
                break
        movie = Movie(movie_id=movie_json['id'],
                      vote_average=movie_json['vote_average'],
                      movie_title=movie_title,
                      is_adult=movie_json['adult'])

        if not movie.titles:
            movie.titles = [Title(title=record['title']) for record in movie_json['titles']]
        return movie, sess
    else:
        return None, sess


def get_session_with_keywords(movie_json, movie, sess) -> Session:
    for record in movie_json['keywords']:
        if sess.query(Keyword).filter(Keyword.keyword_id == record['id']).count() == 0:
            keywrd = Keyword(keyword_id=record['id'], keyword=record['name'])
            keywrd.movies.append(movie)
            sess.add(keywrd)
        else:
            keywrd = sess.query(Keyword).filter(Keyword.keyword_id == record['id']).first()
            keywrd.movies.append(movie)
    return session


def get_session_with_user_lists(movie_json, movie, sess) -> Session:
    for record in movie_json['results']:
        if sess.query(List).filter(List.list_id == record['id']).count() == 0:
            movie_list = List(list_id=record['id'], list_title=record['name'])
            movie_list.movies.append(movie)
            sess.add(movie_list)
        else:
            movie_list = sess.query(List).filter(List.list_id == record['id']).first()
            movie_list.movies.append(movie)
    return sess


def get_session_with_genres(movie_json, movie, sess) -> Session:
    for record in movie_json['genres']:
        if sess.query(Genre).filter(Genre.genre_id == record['id']).count() == 0:
            genre = Genre(genre_id=record['id'], genre=record['name'])
            genre.movies.append(movie)
            sess.add(genre)
        else:
            genre = sess.query(Genre).filter(Genre.genre_id == record['id']).first()
            genre.movies.append(movie)
    return sess


def persist_data_to_db(movie_json, sess) -> bool:
    movie, sess = get_movie_frm_json_if_not_in_db(movie_json, sess)
    if not movie:
        return False
    sess = get_session_with_keywords(movie_json, movie, sess)
    sess = get_session_with_user_lists(movie_json, movie, sess)
    sess = get_session_with_genres(movie_json, movie, sess)
    sess.add(movie)
    sess.commit()
    return True


def is_valid_json_movie(movie_json):
    keys = movie_json.keys()
    has_id = 'id' in keys
    has_titles = 'titles' in keys
    has_keywords = 'keywords' in keys
    has_genres = 'genres' in keys
    return has_id and has_titles and has_genres and has_keywords


def fetch_movie_json(id_tmdb, proxy_list) -> dict:
    movie_json = make_tmdb_api_request(
        method='/movie/{}'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    keywords = make_tmdb_api_request(
        method='/movie/{}/keywords'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    movie_json.update(keywords)
    lists = make_tmdb_api_request(
        method='/movie/{}/lists'.format(id_tmdb),
        api_key=API_KEY_V3,
        proxy_list=proxy_list
    )
    movie_json.update(lists)
    alternative_titles = make_tmdb_api_request(
        method='/movie/{}/alternative_titles'.format(id_tmdb),
        api_key=API_KEY_V3, proxy_list=proxy_list
    )
    movie_json.update(alternative_titles)
    if is_valid_json_movie(movie_json):
        return movie_json
    return {}


def fetch_db(sess):
    how_many_movies_in_db = sess.query(Movie).count()
    index = 1
    proxy_list = fetch_proxy_list()
    for _ in tqdm(range(AMOUNT_OF_MOVIES - how_many_movies_in_db), total=AMOUNT_OF_MOVIES - how_many_movies_in_db,
                  unit='movie'):
        timestamp = time.time()
        while True:
            new_timestamp = time.time()
            if new_timestamp - timestamp > 30:
                index += 100
            movie_json = fetch_movie_json(index, proxy_list)
            index += 1
            if movie_json:
                has_persisted = persist_data_to_db(movie_json, sess)
                if has_persisted:
                    break


def locate_similar_genre_movies(movie) -> set:
    result = set()
    for genre in movie.genres:
        result = result.union(set(genre.movies))
    return result


def locate_similar_lists_movies(movie) -> set:
    result = set()
    for a_list in movie.lists:
        result = result.union(set(a_list.movies))
    return result


def locate_similar_keyword_movies(movie) -> set:
    result = set()
    for keyword in movie.keywords:
        for other_keyword in movie.keywords:
            if keyword != other_keyword:
                result = result.union(set(keyword.movies).intersection(set(other_keyword.movies)))
    return result


def get_similar_movies_list_sorted_by_vote(movie) -> list:
    similar_genre_movies = locate_similar_genre_movies(movie)
    similar_keywords_movies = locate_similar_keyword_movies(movie)
    similar_lists_movies = locate_similar_lists_movies(movie)
    similar_keywords_and_genres = similar_genre_movies.intersection(similar_keywords_movies)
    if not similar_keywords_and_genres:
        return []
    similar_keywords_lists_genres = similar_keywords_and_genres.intersection(similar_lists_movies)
    if not similar_keywords_lists_genres:
        return sorted(similar_keywords_and_genres, key=lambda movie: -movie.vote_average)
    if len(similar_keywords_lists_genres) < RECOMMENDATIONS_LIST_SIZE:
        similar_keywords_and_genres = sorted(similar_keywords_and_genres, key=lambda movie: -movie.vote_average)\
                                      + sorted(similar_keywords_and_genres, key=lambda movie: -movie.vote_average)[:RECOMMENDATIONS_LIST_SIZE - len(similar_keywords_lists_genres)]
    return sorted(similar_keywords_and_genres, key=lambda movie: -movie.vote_average)


def get_rank(movie, the_movie, phrase) -> float:
    genre_factor = 1 if len(set(movie.genres).intersection(set(the_movie.genres))) > 0 else 0
    keywords_factor = 1 if len(set(movie.keywords).intersection(set(the_movie.keywords))) > 0 else 0
    lists_factor = 1 if len(set(movie.lists).intersection(the_movie.lists)) > 0 else 0
    return genre_factor + keywords_factor + lists_factor + movie.vote_average


def get_the_most_similar_title(movie_title, sess) -> Title:
    similar_titles = sess.query(Title).filter(Title.title.like('%{}%'.format(movie_title))).all()
    if not similar_titles:
        return None
    similar_titles = sorted(similar_titles, key=lambda x: -x.movie.vote_average)
    the_most_similar = similar_titles[0]
    for title in similar_titles:
        if len(title.title.replace(movie_title, '')) < len(the_most_similar.title.replace(movie_title, '')):
            the_most_similar = title
    return the_most_similar


def get_titles_of_movie_list(similar_movies) -> list:
    title_list = [movie.titles[0].title for movie in similar_movies]
    return list(OrderedDict.fromkeys(title_list))[:RECOMMENDATIONS_LIST_SIZE]


if __name__ == '__main__':
    print("Welcome to SBKubric's Cinema Advisor!")
    engine = get_engine_and_initialize_db(Base)
    Session.configure(bind=engine)
    session = Session()
    print('Checking the db state...')
    if is_incomplete(session):
        print('Fetching the database...')
        fetch_db(session)
    phrase = input('Please, enter the part of the movie title that should be a pivot: ')
    desired_title = get_the_most_similar_title(phrase, session)
    while not desired_title:
        phrase = input('Failed to find a movie with such title >_<. Lets try another! ^_^ : ')
        desired_title = get_the_most_similar_title(phrase, session)
    print('\nFound a movie named "{}"'.format(desired_title.title))
    print('Searching for similar films...')
    similar_movies = get_similar_movies_list_sorted_by_vote(desired_title.movie)
    for film in similar_movies:
        if film == desired_title.movie:
            similar_movies.remove(film)
            break
    if not similar_movies:
        print('Unfortunately, nothing is found!')
    else:
        print('Building a recommendations list...')
        print('\nThe recommended films:')
        for num, title in enumerate(similar_movies[:RECOMMENDATIONS_LIST_SIZE], start=1):
            print('{}. {}'.format(num, title.title))
    session.close()
