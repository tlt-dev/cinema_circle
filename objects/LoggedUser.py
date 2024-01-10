from objects.User import User
from bson import ObjectId, json_util
from neo4j import GraphDatabase
from datetime import datetime

import pymongo

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")


class LoggedUser(User):
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, profile_pic_path=None, id=None, preferences=None, creation_date=None, admin=None):
        if user is not None:
            User.__init__(self, user=user)
            self.admin = user['admin'] if 'admin' in user else False
        else:
            User.__init__(self, first_name=first_name, last_name=last_name, email=email, password=password, profile_pic_path=profile_pic_path, id=id, preferences=preferences, creation_date=creation_date)
            self.admin = admin

    def to_json(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'preferences': self.preferences,
            'profile_pic_path': self.profile_pic_path,
            'creation_date': self.creation_date.strftime('%Y/%m/%d'),
        }

    def update_multiple_fields(self, id, first_name=None, last_name=None, email=None, password=None, preferences=None):
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
        if preferences:
            fields['preferences'] = preferences

        try:
            user_collection.updateOne({fields})
        except Exception as e:
            print("Error while updating user. Error : ", e)

    def get_by_email(self):
        if self.email is not None:
            try:
                user = LoggedUser(user=user_collection.find_one({'email': self.email}))
            except Exception as e:
                print("User does not exist. Error : ", e)
            else:
                return user

    def set_password(self, password):
        try:
            user_collection.updateOne({'_id': ObjectId(self), 'password': password})
        except Exception as e:
            print("Error updating user. Error : ", e)
        else:
            self.password = password

    def set_preferences(self, preferences):
        try:
            user_collection.update_one({'_id': ObjectId(self.id)}, {"$set": {'preferences': preferences}})
        except Exception as e:
            print("Error updating user. Error : ", e)
        else:
            self.preferences = preferences

    def see_movie(self, movie_id):
        query = "MATCH (u:User {id: $user_id}), (m:Movie {id: $movie_id}) CREATE (u)-[:SEEN {date:$date}]->(m) RETURN exists((u)-[:SEEN]->(m))"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id, date=datetime.today())

        return records[0]

    def like_movie(self, movie_id, value):

        query = "MATCH (u:User {id: $user_id}), (m:Movie {id: $movie_id}) RETURN exists((u)-[:LIKED]->(m)) as relation_exist"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id)

        if records[0].data()['relation_exist']:
            # if LIKED relationship already exists, edit it
            query = "MATCH (u:User {id: $user_id})-[r:LIKED]->(m:Movie {id: $movie_id}) SET r.like=$value, r.date=$date RETURN exists((u)-[:LIKED {like: $value}]->(m)) as return_value"
        else:
            query = "MATCH (u:User {id: $user_id}), (m:Movie {id: $movie_id}) CREATE (u)-[:LIKED {like:$value, date:$date}]->(m) RETURN exists((u)-[:LIKED]->(m)) as return_value"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id, value=value, date=datetime.today())

        return records[0].data()['return_value']

    def add_review(self, movie_id):
        query = "MATCH (u:User {id: $user_id}), (m:Movie {id: $movie_id}) CREATE (u)-[:REVIEWED {date:$date}]->(m) RETURN exists((u)-[:REVIEWED]->(m)) as return_value"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id, date=datetime.today())

        return records[0].data()['return_value']

    def has_seen_movie(self, movie_id):
        query = "OPTIONAL MATCH (u:User {id: $user_id})-[r:SEEN]->(m:Movie {id: $movie_id}) RETURN CASE WHEN r IS NOT NULL THEN r ELSE NULL END as return_value"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id)

        return records[0].data()['return_value']

    def has_liked_movie(self, movie_id):
        query = "OPTIONAL MATCH (u:User {id: $user_id})-[r:LIKED]->(m:Movie {id: $movie_id}) RETURN CASE WHEN r IS NOT NULL THEN r.like ELSE NULL END as return_value"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id)

        return records[0].data()['return_value']

    def has_reviewed_movie(self, movie_id):
        query = "OPTIONAL MATCH (u:User {id: $user_id})-[r:REVIEWED]->(m:Movie {id: $movie_id}) RETURN CASE WHEN r IS NOT NULL THEN r ELSE NULL END as return_value"

        records, summary, keys = graph_driver.execute_query(query, user_id=self.id, movie_id=movie_id)

        return records[0].data()['return_value']



