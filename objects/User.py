from xml.dom.minidom import Document

from bson import ObjectId, json_util
import pymongo
from neo4j import GraphDatabase


client = pymongo.MongoClient(host="localhost", port=27018, username=None, password=None)
document_db = client['cinema_circle']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")


class User:
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, profile_pic_path=None, id=None, creation_date=None):
        ''' Use user arg if user dict from db'''
        if user is not None:
            self.id = str(user['_id']) if "_id" in user.keys() else str(user['id'])
            self.first_name = user['first_name']
            self.last_name = user['last_name']
            self.email = user['email']
            self.password = user['password']
            self.profile_pic_path = user['profile_pic_path']
            self.creation_date = user['creation_date']
        else:
            self.id = str(id)
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.password = password
            self.profile_pic_path = profile_pic_path
            self.creation_date = creation_date
        self.watched_list = None
        self.reviews_count = None
        self.liked_movies_count = None
        self.disliked_movies_count = None
        self.favorite_genres = None
        self.last_activities = None

    def to_json(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'profile_pic_path': self.profile_pic_path,
            'creation_date': self.creation_date.strftime('%Y/%m/%d'),
        }

    def user_exist(self):
        print(user_collection.find_one({'email': self.email}))
        if user_collection.find_one({'email': self.email}) is not None:
            return True
        return False

    def create(self):
        try:
             result = user_collection.insert_one({
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'password': self.password,
                'profile_pic_path': self.profile_pic_path
            })
        except Exception as e:
            print("Error while creating user. Error : ", e)
        else:
            return result.inserted_id

    def delete(self):
        try:
            user_collection.delete_one({'_id': ObjectId(self.id)})
        except Exception as e:
            print("Error while deleting user. Error : ", e)

    def get_by_id(self):
        if self.id is not None:
            try:
                user = user_collection.find_one({'_id': ObjectId(self.id)})
            except Exception as e:
                print("User does not exist. Error : ", e)
            else:
                return user
        else:
            raise Exception("User id not provided")

    def get_by_first_name_last_name(self):
        if self.first_name is not None and self.last_name is not None:
            try:
                user = user_collection.find({'first_name': self.first_name, 'last_name': self.last_name})
                if user.count() > 1:
                    raise Exception("More than one user found. Please get user by email or id")
            except Exception as e:
                print('User does not exist. Error : ', e)
            else:
                return user

    def update_multiple_fields(self, id, first_name=None, last_name=None, email=None, password=None):
        fields = {}
        fields['id'] = ObjectId(id)
        if first_name:
            fields['first_name'] = first_name
        if last_name:
            fields['last_name'] = last_name
        if email:
            fields['email'] = email
        if password:
            fields['password'] = password

        try:
            user_collection.update_one({fields})
        except Exception as e:
            print("Error while updating user. Error : ", e)

    def set_first_name(self, first_name):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'first_name': first_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            self.first_name = first_name

    def set_last_name(self, last_name):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'last_name': last_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            self.last_name = last_name

    def set_email(self, email):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'email': email})
        except Exception as e:
            print("Error updating user. Error : ", e)
        else:
            self.email = email

    def get_watched_list(self):
        query = "MATCH (u:User {id: $id})-[:SEEN]->(m:Movie) RETURN m"

        records, summary, keys = graph_driver.execute_query(query, id=self.id, database="cinemacircle")

        self.watched_list = [record.data()['m'] for record in records]

    def get_reviews_count(self):
        pass

    def get_last_activities(self):
        pass

    def get_favorites_genres(self):
        query = """
                MATCH (user:User {id: $id})-[r:LIKED|REVIEWED|SEEN]->(m:Movie)-[:TYPE_OF]->(g:Genre)
                WITH user, g, r, m,
                    CASE 
                    WHEN r:SEEN THEN 
                        CASE
                        WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 4
                        WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 3
                        WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 2
                        ELSE 1
                        END
                    WHEN r:LIKED AND r.like = 0 THEN 
                        CASE
                        WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 7
                        WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 5
                        WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 2
                        ELSE 3
                        END
                    WHEN r:REVIEWED AND r.like = 0 THEN 
                        CASE
                        WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 15
                        WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 12
                        WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 9
                        ELSE 6
                        END
                    WHEN r:LIKED AND r.like = -1 THEN 
                        CASE
                        WHEN datetime(r.date) >= datetime() - duration('P3D') THEN -7
                        WHEN datetime( r.date) >= datetime() - duration('P1W') THEN -5
                        WHEN datetime(r.date) >= datetime() - duration('P2W') THEN -2
                        ELSE -3
                        END
                    WHEN r:REVIEWED AND r.like = -1 THEN 
                        CASE
                        WHEN datetime(r.date) >= datetime() - duration('P3D') THEN -15
                        WHEN datetime(r.date) >= datetime() - duration('P1W') THEN -12
                        WHEN datetime(r.date) >= datetime() - duration('P2W') THEN -9
                        ELSE -6
                        END
                    END AS score
                WITH g, SUM(score) + 100 AS totalScore
                RETURN g AS Genre, totalScore
                ORDER BY totalScore DESC
                LIMIT 3
            """
        records, summary, keys = graph_driver.execute_query(query, id=self.id, database="cinemacircle")

        self.favorite_genres = [record.data()['Genre'] for record in records]

    def get_liked_movies_count(self):
        pass

    def get_disliked_movies_count(self):
        pass



