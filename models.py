from sqlalchemy import Column, Integer, String, REAL, ForeignKey, Table, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
movie_genres = Table('movie_genres', Base.metadata,
                     Column('genre_id', ForeignKey('genres.genre_id'), primary_key=True),
                     Column('movie_id', ForeignKey('movies.movie_id'), primary_key=True)
)
movie_lists = Table('movie_lists', Base.metadata,
                     Column('list_id', ForeignKey('lists.list_id'), primary_key=True),
                     Column('movie_id', ForeignKey('movies.movie_id'), primary_key=True)
)
movie_keywords = Table('movie_keywords', Base.metadata,
                       Column('keyword_id', ForeignKey('keywords.keyword_id'), primary_key=True),
                       Column('movie_id', ForeignKey('movies.movie_id'), primary_key=True)
)


class Movie (Base):
    __tablename__ = 'movies'

    movie_id = Column(Integer, primary_key=True)
    title = Column(String)
    vote_average = Column(REAL)
    is_adult = Column(Boolean)

    titles = relationship('Title', back_populates='movie')

    genres = relationship('Genre',
                          secondary=movie_genres,
                          back_populates='movies')
    keywords = relationship('Keyword',
                            secondary=movie_keywords,
                            back_populates='movies')
    lists = relationship('List',
                         secondary=movie_lists,
                         back_populates='movies')

    def __init__(self, movie_id, movie_title, vote_average, is_adult):
        self.movie_id = movie_id
        self.title = movie_title
        self.vote_average = vote_average
        self.is_adult = is_adult

    def __repr__(self):
        return "<Movie(movie_id={}, title='{}', vote_average={}, is_adult='{}', titles='{}', genres='{}', keywords='{}', lists='{}')>".format(
            self.movie_id, self.title, self.vote_average, self.is_adult, self.titles, self.genres, self.keywords, self.lists
        )


class Title (Base):
    __tablename__ = 'titles'

    title_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'))

    movie = relationship('Movie', back_populates='titles')

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Title(title_id={}, title='{}', movie_id={})>".format(
            self.title_id, self.title, self.movie_id
        )


class Keyword (Base):
    __tablename__ = 'keywords'

    keyword_id = Column(Integer, primary_key=True)
    keyword = Column(String)

    movies = relationship('Movie', secondary=movie_keywords, back_populates='keywords')

    def __init__(self, keyword_id, keyword):
        self.keyword_id = keyword_id
        self.keyword = keyword

    def __repr__(self):
        return "<Keyword(keyword_id={}, keyword='{}'>".format(
            self.keyword_id, self.keyword
        )


class Genre (Base):
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True)
    genre = Column(String)

    movies = relationship('Movie', secondary=movie_genres, back_populates='genres')

    def __init__(self, genre_id, genre):
        self.genre_id = genre_id
        self.genre = genre

    def __repr__(self):
        return "<Genre(genre_id={}, genre='{}')>".format(
            self.genre_id, self.genre
        )


class List (Base):
    __tablename__ = 'lists'

    list_id = Column(Integer, primary_key=True)
    list_title = Column(String)

    movies = relationship('Movie', secondary=movie_lists, back_populates='lists')

    def __init__(self, list_id, list_title):
        self.list_id = list_id
        self.list_title = list_title

    def __repr__(self):
        return "<List(id={}, list_title='{}')>".format(
            self.list_id, self.list_title
        )
