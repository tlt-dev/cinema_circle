from bson import ObjectId, json_util
import pymongo
from neo4j import GraphDatabase
from datetime import datetime

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")


class User:
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, profile_pic_path=None,
                 id=None, creation_date=None, admin=None):
        ''' Use user arg if user dict from db'''
        if user is not None:
            self.id = str(user['_id']) if "_id" in user.keys() else str(user['id'])
            self.first_name = user['first_name']
            self.last_name = user['last_name']
            self.email = user['email']
            self.password = user['password']
            self.profile_pic_path = user['profile_pic_path']
            self.creation_date = user['creation_date']
            self.admin = user['admin']
        else:
            self.id = str(id)
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.password = password
            self.profile_pic_path = profile_pic_path
            self.creation_date = creation_date
            self.admin = admin
        self.watched_list = None
        self.reviews_count = None
        self.liked_movies_count = None
        self.disliked_movies_count = None
        self.favorite_genres = []
        self.last_activities = []

    def to_json(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'profile_pic_path': self.profile_pic_path,
            'creation_date': self.creation_date.strftime('%Y/%m/%d'),
            'admin': self.admin
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
                'profile_pic_path': self.profile_pic_path,
                'creation_date': datetime.now(),
                'admin': self.admin
            })
        except Exception as e:
            print("Error while creating user. Error : ", e)
        else:
            graph_driver.execute_query(
                "CREATE (User {id: $id, first_name: $first_name, last_name: $last_name, profile_pic_path: $profile_pic_path})",
                id=str(result.inserted_id), first_name=self.first_name, last_name=self.last_name,
                profile_pic_path=self.profile_pic_path)
            return str(result.inserted_id)

    def delete(self):
        try:
            user_collection.delete_one({'_id': ObjectId(self.id)})
        except Exception as e:
            print("Error while deleting user. Error : ", e)
        else:
            graph_driver.execute_query("MATCH (u:User {id: $id}) DELETE u", id=self.id)

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

    def update_multiple_fields(self, first_name=None, last_name=None, email=None, password=None, admin=None):
        fields = {}
        if first_name:
            fields['first_name'] = first_name
        if last_name:
            fields['last_name'] = last_name
        if email:
            fields['email'] = email
        if password:
            fields['password'] = password
        if admin is not None:
            fields['admin'] = admin

        try:
            user_collection.update_one({'_id': ObjectId(self.id)}, {'$set': fields})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            if first_name and last_name:
                graph_driver.execute_query(
                    "MATCH (u:User {id: $id}) SET u.first_name = $first_name, u.last_name = $last_name", id=self.id,
                    first_name=first_name, last_name=last_name)
            elif first_name:
                graph_driver.execute_query(
                    "MATCH (u:User {id: $id}) SET u.first_name = $first_name", id=self.id,
                    first_name=first_name)
            elif last_name:
                graph_driver.execute_query(
                    "MATCH (u:User {id: $id}) SET u.last_name = $last_name", id=self.id,
                    last_name=last_name)

    def set_first_name(self, first_name):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'first_name': first_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            graph_driver.execute_query(
                "MATCH (u:User {id: $id}) SET u.first_name = $first_name", id=self.id,
                first_name=first_name)
            self.first_name = first_name

    def set_last_name(self, last_name):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'last_name': last_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            graph_driver.execute_query(
                "MATCH (u:User {id: $id}) SET u.last_name = last_name", id=self.id,
                last_name=last_name)
            self.last_name = last_name

    def set_email(self, email):
        try:
            user_collection.update_one({'_id': ObjectId(self.id), 'email': email})
        except Exception as e:
            print("Error updating user. Error : ", e)
        else:
            self.email = email

    def get_watched_list(self, filter="date_desc"):

        if filter == "date_desc": order_by = "r.date DESC"
        if filter == "date_asc": order_by = "r.date ASC"
        if filter == "title_asc": order_by = "m.title ASC"
        if filter == "title_desc": order_by = "m.title DESC"

        query = "MATCH (u:User {id: $id})-[r:SEEN]->(m:Movie) RETURN m ORDER BY " + order_by

        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        self.watched_list = [record.data()['m'] for record in records]

    def get_reviews_count(self):
        query = "MATCH (u:User {id: $id})-[r:REVIEWED]->() RETURN count(r) as result"

        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        self.reviews_count = records[0].data()['result']

    def get_last_activities(self, filter='P15D'):
        if filter == "all":
            query = "MATCH (u:User {id:$id})-[r:SEEN|LIKED|REVIEWED]->(m:Movie) RETURN u, r, r.date, r.like, m"
        else:
            query = "MATCH (u:User {id:$id})-[r:SEEN|LIKED|REVIEWED]->(m:Movie) WHERE datetime(r.date) >= datetime() - duration($duration) RETURN u, r, r.date, r.like, m"

        records, summary, keys = graph_driver.execute_query(query, id=self.id, duration=filter)

        for record in records:
            activity = {
                "date": record.data()['r.date'].to_native().strftime('%d/%m/%Y'),
                "movie_id": record.data()['m']['id'],
                "movie_title": record.data()['m']['title']
            }
            if record.data()['r'][1] == "LIKED":
                if record.data()['r.like'] == 1:
                    activity["action"] = "liked"
                else:
                    activity["action"] = "disliked"
            else:
                activity["action"] = record.data()['r'][1].lower()
            self.last_activities.append(activity)

    def get_favorites_genres(self, filter="score_desc"):
        if filter == "score_desc": order_by = "totalScore DESC"
        if filter == "score_asc": order_by = "totalScore ASC"
        if filter == "name_desc": order_by = "g.name DESC"
        if filter == "name_asc": order_by = "g.name ASC"

        query = "MATCH (user:User {id: $id})-[r:LIKED|REVIEWED|SEEN]->(m:Movie)-[:TYPE_OF]->(g:Genre) WITH user, g, r, m, CASE WHEN r:SEEN THEN CASE WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 4 WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 3 WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 2 ELSE 1 END WHEN r:LIKED AND r.like = 0 THEN CASE WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 7 WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 5 WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 2 ELSE 3 END WHEN r:REVIEWED AND r.like = 0 THEN CASE WHEN datetime(r.date) >= datetime() - duration('P3D') THEN 15 WHEN datetime(r.date) >= datetime() - duration('P1W') THEN 12 WHEN datetime(r.date) >= datetime() - duration('P2W') THEN 9 ELSE 6 END WHEN r:LIKED AND r.like = -1 THEN CASE WHEN datetime(r.date) >= datetime() - duration('P3D') THEN -7 WHEN datetime( r.date) >= datetime() - duration('P1W') THEN -5 WHEN datetime(r.date) >= datetime() - duration('P2W') THEN -2 ELSE -3 END WHEN r:REVIEWED AND r.like = -1 THEN CASE WHEN datetime(r.date) >= datetime() - duration('P3D') THEN -15 WHEN datetime(r.date) >= datetime() - duration('P1W') THEN -12 WHEN datetime(r.date) >= datetime() - duration('P2W') THEN -9 ELSE -6 END END AS score WITH g, SUM(score) + 100 AS totalScore RETURN g AS Genre, totalScore ORDER BY " + order_by
        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        for record in records:
            self.favorite_genres.append({'genre': record.data()['Genre']['name'], 'score': record['totalScore']})

    def get_liked_movies_count(self):
        query = "MATCH (u:User {id: $id})-[r:LIKED {like: 1}]->() RETURN count(r) as result"

        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        self.liked_movies_count = records[0].data()['result']

    def get_disliked_movies_count(self):
        query = "MATCH (u:User {id: $id})-[r:LIKED {like: 0}]->() RETURN count(r) as result"

        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        self.disliked_movies_count = records[0].data()['result']
