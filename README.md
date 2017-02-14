# The movie recomendation system
## Description
This tiny script will fetch for you films from [TMDB](https://www.themoviedb.org)
and build a recommendation list upon my foxy-wisey algorithm and your input.
Don't forget to remove all data after you're done, or you will violate the EULA.


## Installation
```
git clone git@github.com:SBKubric/cinema_advisor.git
```

Oh, you probably don't want to collect garbage in your pip, so you should install a [virtual environment](docs.python-guide.org/en/latest/dev/virtualenvs/)!

Nevertheless, after cloning a repo you should install requirements:

```
pip install -r requirements
```

After that you a free to use my unbelievably magnificent recommendation system.

## Example

INPUT:
```
python cinema_advisor.py
```

OUTPUT:
```
Welcome to SBKubric's Cinema Advisor!
Checking the db state...
Fetching the database...
100%|██████████| 1/1 [00:02<00:00,  2.44s/movie]
Please, enter the part of the movie title that should be a pivot: nan

Found a movie named "The Sleeping Beauty: Fernando Bujones"
Searching for similar films...
Building a recommendations list...

The recommended films:
1. Veim Naniach Lerega Sheelohim Kayam
```

# Disclaimer
All code is written for educational pupouses ONLY.
