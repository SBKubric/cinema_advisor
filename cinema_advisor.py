import requests
import urllib.parse
from pprint import pprint

API_KEY_V3 = 'ea49129df62d63a56dc7324f7186f7fc'


def load_json_data_from_url(base_url, url_params):
    url = '{}?{}'.format(base_url, urllib.parse.urlencode(url_params))
    response = requests.get(url)
    return response.json()


def make_tmdb_api_request(method, api_key, extra_params=None):
    extra_params = extra_params or {}
    url = 'https://api.themoviedb.org/3{}'.format(method)
    params = {
        'api_key': api_key,
        'language': 'ru',
    }
    params.update(extra_params)
    return load_json_data_from_url(url, params)


def get_local_instance_db():
    pass


def create_db():
    pass


def json_to_db_table(json_movie):
    pass


def table_to_json(table_movie_id, db):
    pass


def get_similar_titles_ids_list(movie_title, db):
    pass


def find_id_by_title(movie_title):
    pass


def create_json_frm_db_entry(pivot_id):
    pass


def create_json_list_frm_db_entries(similar_titles_ids_list):
    pass


def get_recommendations_list_frm_db(pivot_json, movies_json_list):
    pass


if __name__ == '__main__':
    # json_300_spartan_details = make_tmdb_api_request(method='/movie/1271', api_key=API_KEY_V3)
    # pprint(json_300_spartan_details)
    # print('\n\n')
    # json_300_spartan_keywords = make_tmdb_api_request(method='/movie/1271/keywords', api_key=API_KEY_V3)
    # pprint(json_300_spartan_keywords)
    # print('\n\n')
    # json_300_spartan_alternative_titles = make_tmdb_api_request(method='/movie/1271/alternative_titles', api_key=API_KEY_V3)
    # pprint(json_300_spartan_alternative_titles)
    # print('\n\n')
    # json_300_spartan_user_lists = make_tmdb_api_request(method='/movie/1271/lists', api_key=API_KEY_V3)
    # pprint(json_300_spartan_user_lists)
    print("Welcome to SBKubric's Cinema Advisor!")
    print('Checking the film database...')
    db = get_local_instance_db()
    if not db:
        print('Creating database...')
        db = create_db()
        print('OK')
    else:
        print('OK')
    movie_title = input('Please, enter the name of the movie that would be a pivot: ')
    print('Searching for similar titles...')
    similar_titles_ids_list = get_similar_titles_ids_list(movie_title, db)
    print('Fetching the data of the pivot movie...')
    pivot_id = find_id_by_title(movie_title)
    pivot_json = create_json_frm_db_entry(pivot_id)
    print('Fetching the data of similar titles...')
    movies_json_list = create_json_list_frm_db_entries(similar_titles_ids_list)
    print('Building a recommendations list...')
    recommendations_list = get_recommendations_list_frm_db(pivot_json, movies_json_list)