from bson import ObjectId, json_util

from db_utlis import get_document_db

db, client = get_document_db()
user_collection = db['user']


class User:
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, preferences=None, profile_pic_path=None, id=None):
        ''' Use user arg if user dict from db'''
        if user is not None:
            self.id = str(user['_id'])
            self.first_name = user['first_name']
            self.last_name = user['last_name']
            self.email = user['email']
            self.password = user['password']
            self.preferences = user['preferences'] if 'preferences' in user else None
            self.profile_pic_path = profile_pic_path
        else:
            self.id = id
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.password = password
            self.preferences = preferences
            self.profile_pic_path = profile_pic_path


    def to_json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'preferences': self.preferences,
            'profile_pic_path': self.profile_pic_path
        }

    def user_exist(self):
        if user_collection.find_one({'email': self.email}) is not None:
            return True
        return False

    def create(self):
        try:
            user_collection.insert_one({
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'password': self.password,
                'preferences': self.preferences,
                'profile_pic_path': self.profile_pic_path
            })
        except Exception as e:
            print("Error while creating user. Error : ", e)

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

    def get_by_email(self):
        if self.email is not None:
            try:
                user = User(user=user_collection.find_one({'email': self.email}))
            except Exception as e:
                print("User does not exist. Error : ", e)
            else:
                return user

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

    def set_first_name(self, first_name):
        try:
            user_collection.updateOne({'_id': ObjectId(self.id), 'first_name': first_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            self.first_name = first_name

    def set_last_name(self, last_name):
        try:
            user_collection.updateOne({'_id': ObjectId(self.id), 'last_name': last_name})
        except Exception as e:
            print("Error while updating user. Error : ", e)
        else:
            self.last_name = last_name

    def set_email(self, email):
        try:
            user_collection.updateOne({'_id': ObjectId(self.id), 'email': email})
        except Exception as e:
            print("Error updating user. Error : ", e)
        else:
            self.email = email

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



