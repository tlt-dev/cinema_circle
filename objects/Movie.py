from bson import ObjectId
from neo4j import GraphDatabase
import pymongo


client = pymongo.MongoClient(host="localhost", port=27018, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")

class Movie:

    def __init__(self, movie=None, 
                 title=None, 
                 overview=None, 
                 poster_path=None, 
                 backdrop_path=None, 
                 release_date=None, 
                 runtime=None, 
                 tagline=None, 
                 production_countries=None, 
                 cast=None, directors=None, 
                 comments=None, 
                 id=None):
        if movie is not None:
            self.id = str(movie['_id']) if "_id" in movie.keys() else str(movie['id'])
            self.title = movie["title"]
            self.overview = movie["overview"]
            self.poster_path = movie["poster_path"]
            self.backdrop_path = movie["backdrop_path"]
            self.release_date = movie["release_date"]
            self.runtime = movie["runtime"]
            self.tagline = movie["tagline"]
            self.production_countries = movie["production_countries"]
            self.cast = movie["cast"]
            self.directors = movie["directors"]
            self.comments = movie["comments"]
        else:
            self.id = str(id)
            self.title = title
            self.overview = overview
            self.poster_path = poster_path
            self.backdrop_path = backdrop_path
            self.release_date = release_date
            self.runtime = runtime
            self.tagline = tagline
            self.production_countries = production_countries
            self.cast = cast
            self.directors = directors
            self.comments = comments
    
    def to_json(self):
        return {
            'id' :self.id,
            'title':self.title,
            'overview':self.overview ,
            'poster_path':self.poster_path ,
            'backdrop_path': self.backdrop_path ,
            'release_date':self.release_date ,
            'runtime':self.runtime,
            'tagline':self.tagline,
            'production_countries':self.production_countries ,
            'cast':self.cast ,
            'directors':self.directors,
            'comments':self.comments ,
        }

    def movie_exist(self):
        if movie_collection.find_one({'title': self.title}) is not None:
            return True
        return False

    def create(self):
        try:
             result = movie_collection.insert_one({
                    'title':self.title,
                    'overview':self.overview ,
                    'poster_path':self.poster_path ,
                    'backdrop_path': self.backdrop_path ,
                    'release_date':self.release_date ,
                    'runtime':self.runtime,
                    'tagline':self.tagline,
                    'production_countries':self.production_countries ,
                    'cast':self.cast ,
                    'directors':self.directors,
                    'comments':self.comments ,
            })
        except Exception as e:
            print("Error while creating movie. Error : ", e)
        else:
            return result.inserted_id

    def delete(self):
        try:
            movie_collection.delete_one({'_id': ObjectId(self.id)})
        except Exception as e:
            print("Error while deleting movie. Error : ", e)

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

    def update_multiple_fields(self,id, title=None, 
                 overview=None, 
                 poster_path=None, 
                 backdrop_path=None, 
                 release_date=None, 
                 runtime=None, 
                 tagline=None, 
                 production_countries=None, 
                 cast=None, directors=None, 
                 comments=None):
        fields = {}
        fields['id'] = ObjectId(id)
        if title:
            fields['title'] = title
        if overview:
            fields['overview'] = overview
        if poster_path:
            fields['poster_path'] = poster_path
        if backdrop_path:
            fields['backdrop_path'] = backdrop_path
        if release_date:
            fields['release_date'] = release_date
        if runtime:
            fields['runtime'] = runtime
        if tagline:
            fields['tagline'] = tagline
        if production_countries:
            fields['production_countries'] = production_countries
        if cast:
            fields['cast'] = cast
        if directors:
            fields['directors'] = directors
        if comments:
            fields['comments'] = comments
        
        try:
            movie_collection.update_one({fields})
        except Exception as e:
            print("Error while updating movie. Error : ", e)

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

    def set_backdrop_path(self, backdrop_path):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'backdrop_path': backdrop_path}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.backdrop_path = backdrop_path

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

    def set_tagline(self, tagline):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'tagline': tagline}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.tagline = tagline

    def set_production_countries(self, production_countries):
        try:
            movie_collection.update_one({'_id': ObjectId(self.id)}, {'$set': {'production_countries': production_countries}})
        except Exception as e:
            print("Error while updating movie. Error : ", e)
        else:
            self.production_countries = production_countries

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


        