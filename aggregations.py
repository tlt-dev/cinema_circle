import pymongo

client = pymongo.MongoClient("mongodb://localhost:27018,localhost:27019,localhost:27020/test?replicaSet=rs0&w=1")
document_db = client['cinema_circle']
movie_collection = document_db['movie']


def get_all_years():
    years_group = movie_collection.aggregate(
        [{"$project": {"cast": {'$year': "$release_date"}}}, {
            "$group": {"_id": "$year", }},
         {"$sort": {"_id": -1}}])

    return [year['_id'] for year in years_group]

def get_actors(search):
    actors_group = movie_collection.aggregate(
        [{"$unwind": "$cast"}, {
            "$group": {"_id": "$cast.name",
                       "numberOfMovies": {"$sum": 1}}},
         {"$sort": {"numberOfMovies": -1}}])

    return [actor['_id'] for actor in actors_group if search.lower() in actor['_id'].lower()]


def aggreg_movies_by_year(filter):
    movies_by_year = movie_collection.aggregate(
        [{"$project": {"year": {'$year': "$release_date"}, "title": 1, "poster_path": "$poster_path", "_id": 1}}, {
            "$group": {"_id": "$year", "numberOfMovies": {"$sum": 1},
                       "movies": {"$push": {"title": "$title", "poster_path": "$poster_path", "id": "$_id"}}}},
         {"$sort": {"_id": -1}}])
    movies = {}
    for year in movies_by_year:
        if year['_id'] == int(filter):
            movies["nb_movies"] = year['numberOfMovies']
            movies['movies'] = year['movies']
            for index, movie in enumerate(movies['movies']):
                movies['movies'][index]['id'] = str(movie['id'])
    return movies


def aggreg_movies_by_actor(actors):
    movies_by_actor = movie_collection.aggregate([{"$unwind": "$cast"}, {
        "$group": {"_id": "$cast.name", "movies": {"$push": {"title": "$title", "poster_path": "$poster_path", "id": "$_id"}}, "numberOfMovies": {"$sum": 1}}},
                                                  {"$sort": {"numberOfMovies": -1}}])

    actors_movies = []
    for actor in movies_by_actor:
        if actor['_id'] in actors:

            movies = actor['movies']
            for index, movie in enumerate(movies):
                movies[index]['id'] = str(movie['id'])

            actors_movies.append({
                'name': actor['_id'],
                'nb_movies': actor['numberOfMovies'],
                'movies': movies
            })

    return actors_movies
