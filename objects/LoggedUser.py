from objects.User import User
from bson import ObjectId, json_util
from neo4j import GraphDatabase

import pymongo

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"))


class LoggedUser(User):
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, profile_pic_path=None, id=None, preferences=None):
        if user is not None:
            User.__init__(self, user=user)
            self.preferences = user['preferences'] if 'preferences' in user else None
        else:
            User.__init__(self, first_name=first_name, last_name=last_name, email=email, password=password, profile_pic_path=profile_pic_path, id=id)
            self.preferences = preferences

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

    def see_movie(self, movie_id, value):
        pass

    def like_movie(self, movie_id, value):
        pass

    def add_review(self, movie_id, title, comment):
        pass

    def has_seen_movie(self, movie_id):
        pass

    def has_liked_movie(self, movie_id):
        "if liked = True / if disliked = False / else None"
        pass

    def has_reviewed_movie(self, movie_id):
        pass



