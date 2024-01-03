from bson import ObjectId
from django.shortcuts import render
from db_utlis import get_document_db

import logging
logger = logging.getLogger("mylogger")

def index(request):
    return render(request, 'index.html')


def register_page(request):
    return render(request, 'register.html')


def login_page(request):
    return render(request, 'login.html')


def login(request):
    # TODO: Process authentification

    # return render(request, 'recommendations.html')
    return recommendations(request)


def recommendations(request):
    db, client = get_document_db()

    movie_collection = db['movie']
    movies = list(movie_collection.find().limit(10))
    return render(request, 'recommendations.html', {'movies': movies})


def movie_details(request, id):
    db, client = get_document_db()

    movie_collection = db['movie']
    movie = list(movie_collection.find({'_id': ObjectId(id)}))[0]
    return render(request, 'movie_details.html', {'movie': movie})


def get_user(request, id):
    db, client = get_document_db()

    user_collection = db['user']
    user = list(user_collection.find({'_id': ObjectId(id)}))[0]
    return render(request, 'user_page.html', {'user': user})


def add_review(request, id):
    pass