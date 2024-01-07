from pymongo import MongoClient
from neo4j import GraphDatabase

def get_document_db(db_name="cinema_circle", host="localhost", port=27017, username=None, password=None):
    client = MongoClient(host=host, port=port, username=username, password=password)
    document_db = client[db_name]

    return document_db, client

def get_graph_db():
    return GraphDatabase.driver("bolt://localhost:7474", "neo4j", "Maelle090801")


def add_one_document(collection, document):
    collection.insert_one(document)


def add_many_documents(collection, documents):
    collection.insert_many(documents)

