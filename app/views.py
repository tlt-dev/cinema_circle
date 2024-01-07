import datetime

from bson import ObjectId
from django.shortcuts import render
from db_utlis import get_document_db
from utils_functions import get_genres

import logging
logger = logging.getLogger("mylogger")


def index(request):
    return render(request, 'index.html')


def register_page(request):
    genres = get_genres()
    return render(request, 'register.html', {'genres': genres})


def login_page(request):
    return render(request, 'login.html')


def login(request):
    # TODO: Process authentification

     # return render(request, 'movie_recommandations.html')
    return recommendations(request)


def recommendations(request):
    db, client = get_document_db()

    movie_collection = db['movie']

    recommandations = [
        {
            "category_title": "Popular movies",
            "movie_list": list(movie_collection.find().limit(6))
        },
        {
            "category_title": "Western (from your preferences)",
            "movie_list": list(movie_collection.find().limit(12))[-6:]
        },
        {
            "category_title": "Thriller (from your preferences)",
            "movie_list": list(movie_collection.find().limit(18))[-6:]
        },
        {
            "category_title": "Horror (from your preferences)",
            "movie_list": list(movie_collection.find().limit(24))[-6:]
        },
        {
            "category_title": "Because you liked The Godfather",
            "movie_list": list(movie_collection.find().limit(30))[-6:]
        },
        {
            "category_title": "Your friends watch",
            "movie_list": list(movie_collection.find().limit(36))[-6:]
        },
        {
            "category_title": "Because you watched The Godfather",
            "movie_list": list(movie_collection.find().limit(42))[-6:]
        }
        ]

    return render(request, 'movie_recommandations.html', {'recommandations': recommandations})


def movie_details(request, id):
    db, client = get_document_db()

    movie_collection = db['movie']
    movie = list(movie_collection.find({'_id': ObjectId(id)}))[0]
    return render(request, 'movie_details.html', {'movie': movie})


def get_user(request, id):
    db, client = get_document_db()

    user_collection = db['user']
    movie_collection = db['movie']
    user = user_collection.find_one({'_id': ObjectId(id)})

    if str(user['_id'])[-1].isdigit() and int(str(user['_id'])[-1]) in range(0, 10):
        user['avatar'] = "avatar_" + str(user['_id'])[-1]
    else:
        user['avatar'] = "avatar_10"

    user["watched_list"] = list(movie_collection.find().limit(15))

    count = 0
    user["commented_movies"] = []
    for movie in user["watched_list"]:
        user["commented_movies"].append({
            "movie": movie,
            "comment": movie["comments"][0]
        })
        count += 1
        if count == 10:
            break

    genres = {}
    for movie in user["watched_list"]:
        for genre in movie["genre"]:
            if genre not in genres.keys():
                genres[genre] = 1
            else:
                genres[genre] += 1

    user["favorites_genres"] = dict(sorted(genres.items(), key=lambda x:x[1], reverse=True))
    user["last_activities"] = [
        {
            "action": "review",
            "review_id": "...",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",
            },
            "date": datetime.date(2024, 1, 4)
        },
        {
            "action": "liked",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",

            },
            "date": datetime.date(2024, 1, 4)
        },
        {
            "action": "watched",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",
            },
            "date": datetime.date(2024, 1, 4)
        }
    ]

    return render(request, 'user_page.html', {'user': user})


def add_review(request, id):
    pass


def get_recommanded_users(request):
    db, client = get_document_db()

    user_collection = db['user']

    recommandations = [
        {
            "category_title": "Most actives",
            "user_list": list(user_collection.find().limit(6))[-6:]
        },
        {
            "category_title": "Popular users",
            "user_list": list(user_collection.find().limit(12))[-6:]
        },
        {
            "category_title": "People who likes Thriller",
            "user_list": list(user_collection.find().limit(18))[-6:]
        },
        {
            "category_title": "People who likes Horror",
            "user_list": list(user_collection.find().limit(24))[-6:]
        },
        {
            "category_title": "Peole who likes Drama",
            "user_list": list(user_collection.find().limit(30))[-6:]
        },
    ]

    return render(request, 'users_recommandations.html', {'recommandations': recommandations})

def get_user_profile(request, id="657b4425e7be990ba7cdf109"):
    genres = get_genres()

    db, client = get_document_db()

    user_collection = db['user']
    movie_collection = db['movie']
    user = user_collection.find_one({'_id': ObjectId(id)})

    if int(str(user['_id'])[-1]) in range(0, 10):
        user['avatar'] = "avatar_" + str(user['_id'])[-1]
    else:
        user['avatar'] = "avatar_10"

    user["watched_list"] = list(movie_collection.find().limit(15))

    count = 0
    user["commented_movies"] = []
    for movie in user["watched_list"]:
        user["commented_movies"].append({
            "movie": movie,
            "comment": movie["comments"][0]
        })
        count += 1
        if count == 10:
            break

    genres = {}
    for movie in user["watched_list"]:
        for genre in movie["genre"]:
            if genre not in genres.keys():
                genres[genre] = 1
            else:
                genres[genre] += 1

    user["favorites_genres"] = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    user["last_activities"] = [
        {
            "action": "review",
            "review_id": "...",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",
            },
            "date": datetime.date(2024, 1, 4)
        },
        {
            "action": "liked",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",

            },
            "date": datetime.date(2024, 1, 4)
        },
        {
            "action": "watched",
            "movie": {
                "id": "657b2245d448da2cface22ea",
                "title": "The Godfather",
            },
            "date": datetime.date(2024, 1, 4)
        }
    ]

    return render(request, 'user_profile.html', {"user": user, "genres": genres})