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
    def __init__(self, user=None, first_name=None, last_name=None, email=None, password=None, profile_pic_path=None, id=None, creation_date=None, admin=None):
        if user is not None:
            User.__init__(self, user=user)
            self.admin = user['admin'] if 'admin' in user else False
        else:
            User.__init__(self, first_name=first_name, last_name=last_name, email=email, password=password, profile_pic_path=profile_pic_path, id=id, creation_date=creation_date)
            self.admin = admin

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
    
    def get_recommended_movie_from_genre(self, genre, displayed_movies):
        followed_user_movies = self.get_followed_user_movies(displayed_movies)
        followed_user_score = self.get_followed_user_score()
        movie_list = {}
        for user_id, movies in followed_user_movies.items():
            for movie in movies:
                if movie["genre"] == genre:
                    if movie["liked"] == 1:
                        score = followed_user_score[user_id]
                    else:
                        score = followed_user_score[user_id] / 4
                    if movie["movie"]["id"] in movie_list:
                        movie_list[movie["movie"]["id"]]["score"] += score
                    else:
                        movie_list[movie["movie"]["id"]] = {"movie": movie["movie"], "score": score}
                        
        movie_list = dict(sorted(movie_list.items(), key=lambda x: x[1]['score'], reverse=True))
        recommended_movies = [movie["movie"] for _,movie in dict(list(movie_list.items())[:6]).items()]
        for i in range(len(recommended_movies)):
            recommended_movies[i]["_id"] =  recommended_movies[i].pop("id")
        
        return recommended_movies

    def get_followed_user_movies(self,displayed_movies):
        query = """
            MATCH (user:User {id:$id})-[:FOLLOWS]->(followed:User)
            MATCH (followed)-[seen:SEEN]->(movie:Movie)
            WHERE NOT movie.id  IN $displayed_movies
            OPTIONAL MATCH (followed)-[liked:LIKED]->(movie) WHERE liked.like <> 0
            MATCH (movie)-[:TYPE_OF]->(genre:Genre)
            RETURN followed AS FollowedUser, 
            COLLECT(DISTINCT {movie: movie, seen: date(seen.date), liked: liked.like, genre: genre.name}) AS Movies
        """
        records, summary, keys = graph_driver.execute_query(query, id=self.id, displayed_movies=displayed_movies)
    
        result = {}
        for record in records:
            movies_dict = []
            for movies in record.data()['Movies']:
                movies_dict.append({
                    "genre" : movies["genre"],
                    "liked" : movies["liked"],
                    "movie" : movies["movie"],
                    "seen" : movies["seen"].iso_format()
                })
            result[record.data()['FollowedUser']["id"]] = movies_dict
        return result
    
    def get_followed_user_score(self):
        query = """
            MATCH (user:User {id: $id})-[:FOLLOWS]->(followed:User)
            OPTIONAL MATCH (followed)-[seen:SEEN]->(movie)
            WITH user, followed, COALESCE(SUM(
                CASE
                WHEN datetime(seen.date) >= datetime() - duration('P1D') THEN 25
                WHEN datetime(seen.date) >= datetime() - duration('P3D') THEN 20
                WHEN datetime(seen.date) >= datetime() - duration('P1W') THEN 10
                WHEN datetime(seen.date) >= datetime() - duration('P2W') THEN 5
                ELSE 0
                END
            ), 0) AS seenScore
            OPTIONAL MATCH (followed)-[liked:LIKED]->(movie)
            WITH followed, seenScore, COALESCE(SUM(
                CASE
                WHEN datetime(liked.date) >= datetime() - duration('P1D') THEN 35
                WHEN datetime(liked.date) >= datetime() - duration('P3D') THEN 30
                WHEN datetime(liked.date) >= datetime() - duration('P1W') THEN 25
                WHEN datetime(liked.date) >= datetime() - duration('P2W') THEN 20
                ELSE 0
                END
            ), 0) AS likedScore
            OPTIONAL MATCH (followed)-[reviewed:REVIEWED]->(movie)
            WITH followed, seenScore, likedScore, COALESCE(SUM(
                CASE
                WHEN datetime(reviewed.date) >= datetime() - duration('P1D') THEN 45
                WHEN datetime(reviewed.date) >= datetime() - duration('P3D') THEN 40
                WHEN datetime(reviewed.date) >= datetime() - duration('P1W') THEN 35
                WHEN datetime(reviewed.date) >= datetime() - duration('P2W') THEN 25
                ELSE 0
                END
            ), 0) AS reviewedScore
            WITH followed, 
                seenScore + likedScore + reviewedScore AS activityScore
            OPTIONAL MATCH (followed)-[seen:SEEN]->(movie)
            WITH followed, activityScore, COUNT(seen) AS moviesWatched
            OPTIONAL MATCH (followed)-[liked:LIKED]->(movie)
            WHERE liked.like = 0
            WITH followed, activityScore, moviesWatched, COUNT(liked) AS likes
            OPTIONAL MATCH (followed)-[disliked:LIKED]->(movie)
            WHERE disliked.like = -1
            WITH followed, activityScore, moviesWatched, likes, COUNT(disliked) AS dislikes
            OPTIONAL MATCH (followed)-[reviewed:REVIEWED]->(movie)
            WITH followed, activityScore, moviesWatched, likes, dislikes, COUNT(reviewed) AS reviews
            RETURN followed, 
                activityScore + 
                moviesWatched * 1 + 
                likes * 1.5 + 
                dislikes * 1.5 + 
                reviews * 2 AS InterestScore
            ORDER BY InterestScore DESC
        """
        records, summary, keys = graph_driver.execute_query(query, id=self.id)

        result = {}
        for record in records:
            result[record.data()["followed"]["id"]] = record.data()["InterestScore"]
            
        return result

    def get_popular_movies(self):
        query = """
        MATCH (m:Movie)<-[r:SEEN|LIKED|REVIEWED]-(u:User)
        WHERE datetime(r.date) >= datetime() - duration('P1M') 
        WITH m, COUNT(r) AS interactions
        RETURN m
        ORDER BY interactions DESC
        LIMIT 6
        """
        records, summary, keys = graph_driver.execute_query(query)

        movies = [record.data()['m'] for record in records]
        for i in range(len(movies)):
            movies[i]["_id"] =  movies[i].pop("id")
        return movies

    def follow_user(self, user_id, value):
        if value == 1:
            query = "MATCH (lu:User {id: $logged_user_id}), (u:User {id: $user_id}) CREATE (lu)-[:FOLLOWS {date:$date}]->(u) RETURN exists((lu)-[:FOLLOWS]->(u)) as return_value"
            records, summary, keys = graph_driver.execute_query(query, logged_user_id=self.id, user_id=user_id,
                                                                date=datetime.today())
        else:
            query = "MATCH (lu:User {id: $logged_user_id})-[r:FOLLOWS]->(u:User {id: $user_id}) DELETE r RETURN exists((lu)-[:FOLLOWS]->(u)) as return_value"
            records, summary, keys = graph_driver.execute_query(query, logged_user_id=self.id, user_id=user_id)

        return records[0].data()['return_value']

    def is_following(self, id):
        query = "RETURN EXISTS((:User {id: $logged_user_id})-[:FOLLOWS]->(:User {id: $user_id})) as is_following"

        records, summary, keys = graph_driver.execute_query(query, logged_user_id=self.id, user_id=id)

        return records[0].data()['is_following']