from datetime import datetime, timedelta

from neo4j import GraphDatabase
import pymongo

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")
client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']
user_collection = document_db['user']


def get_total_users_count():
    query = "MATCH (all_users:User) Return COUNT(all_users) as total_user"

    records, summary, keys = graph_driver.execute_query(query)

    return records[0].data()['total_user']


def get_new_users_count(filter="P15D"):
    if filter == "all":
        return get_total_users_count()
    else:
        if filter == "P15D":
            date_limite = datetime.now() - timedelta(days=15)
        if filter == "P1M":
            date_limite = datetime.now() - timedelta(days=31)
        if filter == "P3M":
            date_limite = datetime.now() - timedelta(days=93)
        if filter == "P6M":
            date_limite = datetime.now() - timedelta(days=186)

        new_users_count = user_collection.count_documents({"creation_date": {"$gte": date_limite}})

    return new_users_count


def get_active_users(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:SEEN|LIKED|REVIEWED|FOLLOWS]->()
                RETURN count(DISTINCT u) as active_users
                """
        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
            MATCH (u:User)-[r:SEEN|LIKED|REVIEWED|FOLLOWS]->()
            WHERE datetime(r.date) >= datetime() - duration($duration)
            RETURN count(DISTINCT u) as active_users
            """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return records[0].data()['active_users']


def get_users_who_seen_movie(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:SEEN]->(:Movie)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:SEEN]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return records[0].data()['nb']


def get_users_who_like_movie(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:LIKED]->(:Movie)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:LIKED]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return records[0].data()['nb']


def get_users_who_posted_review(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:REVIEWED]->(:Movie)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:REVIEWED]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(DISTINCT u) AS nb
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return records[0].data()['nb']


def get_average_seens_per_user(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:SEEN]->(:Movie)
                RETURN COUNT(r) as avg_seen
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:SEEN]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) as avg_seen
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['avg_seen'] / get_total_users_count(), 2)


def get_average_likes_per_user(filter="P15D"):
    if filter == 'all':
        query = """
                MATCH (u:User)-[r:LIKED]->(:Movie)
                RETURN COUNT(r) as avg_like
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:LIKED]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) as avg_like
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['avg_like'] / get_total_users_count(), 2)


def get_average_reviews_per_user(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:REVIEWED]->(:Movie)
                RETURN COUNT(r) as avg_reviews
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:REVIEWED]->(:Movie)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) as avg_reviews
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['avg_reviews'] / get_total_users_count(), 2)


def get_average_followers_per_user(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (:User)-[r:FOLLOWS]->(:User)
                RETURN COUNT(r) as avg_followers
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (:User)-[r:FOLLOWS]->(:User)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) as avg_followers
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['avg_followers'] / get_total_users_count(), 2)


def get_follows_interation(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:FOLLOWS]->(:User)
                RETURN COUNT(r) as nb_follows_interaction
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:FOLLOWS]->(:User)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) as nb_follows_interaction
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return records[0].data()['nb_follows_interaction']


def get_movies_count():
    query = """
            MATCH (m:Movie) RETURN COUNT(m) AS nb_movies
            """

    records, summary, keys = graph_driver.execute_query(query)

    return records[0].data()['nb_movies']


def get_genres_count():
    query = """
            MATCH (g:Genre) RETURN COUNT(g) AS nb_genres
            """

    records, summary, keys = graph_driver.execute_query(query)

    return records[0].data()['nb_genres']


def get_movies_per_genres():
    query = """
            MATCH (m:Movie)-[:TYPE_OF]->(g:Genre)
            WITH g, COUNT(m) AS nb_movies
            RETURN g.name AS name, nb_movies
            ORDER BY nb_movies DESC
            """

    records, summary, keys = graph_driver.execute_query(query)

    result = []
    for r in records:
        result.append(r.data())
    return result


def get_popular_genres(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (u:User)-[r:LIKED|REVIEWED|SEEN]->(m:Movie)-[:TYPE_OF]->(g:Genre)
                RETURN g.name AS name, COUNT(DISTINCT m) AS movies_count 
                ORDER BY movies_count DESC
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (u:User)-[r:LIKED|REVIEWED|SEEN]->(m:Movie)-[:TYPE_OF]->(g:Genre)
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN g.name AS name, COUNT(DISTINCT m) AS movies_count 
                ORDER BY movies_count DESC
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    result = []
    for r in records:
        result.append(r.data())
    return result


def get_average_views_per_movie(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (m:Movie)<-[r:SEEN]-()
                RETURN COUNT(r) AS total_views
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (m:Movie)<-[r:SEEN]-()
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) AS total_views
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['total_views'] / get_movies_count(), 2)


def get_average_like_interactions_per_movie(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (m:Movie)<-[r:LIKED]-()
                RETURN COUNT(r) AS total_interactions
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (m:Movie)<-[r:LIKED]-()
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) AS total_interactions
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['total_interactions'] / get_movies_count(), 2)


def get_average_reviews_per_movie(filter="P15D"):
    if filter == "all":
        query = """
                MATCH (m:Movie)<-[r:REVIEWED]-()
                RETURN COUNT(r) AS total_reviews
                """

        records, summary, keys = graph_driver.execute_query(query)
    else:
        query = """
                MATCH (m:Movie)<-[r:REVIEWED]-()
                WHERE datetime(r.date) >= datetime() - duration($duration)
                RETURN COUNT(r) AS total_reviews
                """

        records, summary, keys = graph_driver.execute_query(query, duration=filter)

    return round(records[0].data()['total_reviews'] / get_movies_count(), 2)


