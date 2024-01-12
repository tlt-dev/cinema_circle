from bson import ObjectId
from neo4j import GraphDatabase
import pymongo

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")


class Movie:

    def __init__(self, movie=None,
                 title=None,
                 genre=None,
                 overview=None,
                 poster_path=None,
                 release_date=None,
                 runtime=None,
                 cast=None, directors=None,
                 comments=None,
                 id=None):
        if movie is not None:
            self.id = str(movie['_id']) if "_id" in movie.keys() else str(movie['id'])
            self.title = movie["title"]
            self.genre = movie['genre']
            self.overview = movie["overview"]
            self.poster_path = movie["poster_path"]
            self.release_date = movie["release_date"]
            self.runtime = movie["runtime"]
            self.cast = movie["cast"]
            self.directors = movie["directors"]
            self.comments = movie["comments"]
        else:
            self.id = str(id)
            self.title = title
            self.genre = genre
            self.overview = overview
            self.poster_path = poster_path
            self.release_date = release_date
            self.runtime = runtime
            self.cast = cast
            self.directors = directors
            self.comments = comments

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'overview': self.overview,
            'poster_path': self.poster_path,
            'release_date': self.release_date,
            'runtime': self.runtime,
            'cast': self.cast,
            'directors': self.directors,
            'comments': self.comments,
        }

    def movie_exist(self):
        if movie_collection.find_one({'title': self.title}) is not None:
            return True
        return False

    def create(self):
        try:
            result = movie_collection.insert_one({
                'title': self.title,
                'overview': self.overview,
                'genre': self.genre,
                'poster_path': self.poster_path,
                'release_date': self.release_date,
                'runtime': self.runtime,
                'cast': self.cast,
                'directors': self.directors,
                'comments': self.comments,
            })
        except Exception as e:
            print("Error while creating movie. Error : ", e)
        else:
            graph_driver.execute_query("CREATE (Movie {id: $id, title: $title, poster_path: ''})", id=str(result.inserted_id), title=self.title)
            return str(result.inserted_id)

    def delete(self):
        try:
            movie_collection.delete_one({'_id': ObjectId(self.id)})
        except Exception as e:
            print("Error while deleting movie. Error : ", e)
        else:
            graph_driver.execute_query("MATCH (m:Movie {id: $id})-[r:SEEN|LIKED|REVIEWED|TYPE_OF]-() DELETE r, m", id=self.id)

    def get_by_id(self):
        if self.id is not None:
            try:
                movie = movie_collection.find_one({'_id': ObjectId(self.id)})
            except Exception as e:
                print("Movie does not exist. Error : ", e)
            else:
                return movie
        else:
            raise Exception("Movie id not provided")

    def get_by_title(self):
        if self.title is not None:
            try:
                movie = movie_collection.find({'title': self.title})
                if movie.count() > 1:
                    raise Exception("More than one movie found. Please get movie by id")
            except Exception as e:
                print('Movie does not exist. Error : ', e)
            else:
                return movie

    def update_multiple_fields(self, title=None,
                               overview=None,
                               genre=None,
                               poster_path=None,
                               release_date=None,
                               runtime=None,
                               cast=None, directors=None,
                               comments=None):
        fields = {}
        if title:
            fields['title'] = title
            print(title)
        if genre:
            fields['genre'] = genre
        if overview:
            fields['overview'] = overview
        if poster_path:
            fields['poster_path'] = poster_path
        if release_date:
            fields['release_date'] = release_date
        if runtime:
            fields['runtime'] = runtime
        if cast:
            fields['cast'] = cast
        if directors:
            fields['directors'] = directors
        if comments:
            fields['comments'] = comments

        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': fields})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            if title:
                graph_driver.execute_query("MATCH (m:Movie {id: $id}) SET m.title = $title", id=self.id, title=title)

    def set_id(self, id):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'_id': id}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.id = id

    def set_title(self, title):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'title': title}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.title = title

    def set_genre(self, genre):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'genre': genre}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.genre = genre

    def set_overview(self, overview):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'overview': overview}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.overview = overview

    def set_poster_path(self, poster_path):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'poster_path': poster_path}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.poster_path = poster_path

    def set_release_date(self, release_date):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'release_date': release_date}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.release_date = release_date

    def set_runtime(self, runtime):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'runtime': runtime}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.runtime = runtime

    def set_cast(self, cast):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'cast': cast}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.cast = cast

    def set_directors(self, directors):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'directors': directors}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.directors = directors

    def set_comments(self, comments):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'comments': comments}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.comments = comments
