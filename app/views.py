import datetime
import json
import random

from bson import ObjectId, json_util
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login

from db_utlis import get_document_db
from objects.User import User
from utils_functions import get_genres
import pymongo

import logging
logger = logging.getLogger("mylogger")

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']
user_collection = document_db['user']

def index(request):
    return render(request, 'index.html')


@require_http_methods(['GET'])
def register_page(request):
    genres = get_genres()
    return render(request, 'register.html', {'genres': genres})


@require_http_methods(['POST'])
def register(request):
    user = User(
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        email=request.POST.get('email'),
        password=request.POST.get('password'),
        preferences=[request.POST.get('preference_1'), request.POST.get('preference_2'), request.POST.get('preference_3')],
        profile_pic_path='avatar_' + str(random.randint(1,10)) + '.png'
    )

    if user.user_exist():
        return HttpResponse('The email is already registered. Please try to login.')
    else:
        try:
            user.id = user.create()
        except Exception as e:
            print(e)
        else:
            print(user)
            request.session['user'] = user.to_json()
            return redirect('recommendations')


def login_page(request):
    return render(request, 'login.html')


@require_http_methods(['POST'])
def authenticate(request):
    user = User(email=request.POST.get('email'), password=request.POST.get('password'))
    print(user)
    if user.user_exist():
        user = user.get_by_email()
        if user is not None:
            request.session['user'] = user.to_json()
            return redirect('recommendations')
    else:
        return HttpResponse({'message': 'Invalid email or password'})


def logout(request):
    del request.session['user']
    return redirect('index')


def recommendations(request):
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
    movie = list(movie_collection.find({'_id': ObjectId(id)}))[0]
    return render(request, 'movie_details.html', {'movie': movie})


def get_user(request, id):
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


def get_user_profile(request):
    genres = get_genres()

    user_id = request.session.get('user')['id']

    user = user_collection.find_one({'_id': ObjectId(user_id)})

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

    genres_count = {}
    for movie in user["watched_list"]:
        for genre in movie["genre"]:
            if genre not in genres_count.keys():
                genres_count[genre] = 1
            else:
                genres_count[genre] += 1

    user["favorites_genres"] = dict(sorted(genres_count.items(), key=lambda x: x[1], reverse=True))
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

@require_http_methods(["POST"])
def update_preferences(request):
    preferences = [request.POST.get('preference_1'), request.POST.get('preference_2'), request.POST.get('preference_3')]

    user = User(id=request.session['user']['id'])
    user.set_preferences(preferences)

    return redirect('get_user_profile')