from pymongo import MongoClient


def get_document_db(db_name="cinema_circle", host="localhost", port=27017, username=None, password=None):
    client = MongoClient(host=host, port=port, username=username, password=password)
    document_db = client[db_name]

    return document_db, client


def add_one_document(collection, document):
    collection.insert_one(document)


def add_many_documents(collection, documents):
    collection.insert_many(documents)

