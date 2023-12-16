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

    movie_collection = db['movies']
    movies = list(movie_collection.find().limit(10))
    logger.info(movies)
    return render(request, 'recommendations.html', {'movies': movies})


def movie_details(request, id):
    db, client = get_document_db()

    movie_collection = db['movies']
    movie = list(movie_collection.find({'_id': ObjectId(id)}))[0]
    logger.info(movie)
    return render(request, 'movie_details.html', {'movie': movie})
