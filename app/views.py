import datetime
import json
import random
import pymongo

from bson import ObjectId
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from objects.LoggedUser import LoggedUser
from objects.User import User
from utils_functions import get_genres
from neo4j import GraphDatabase

import logging
logger = logging.getLogger("mylogger")

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")

graph_driver.verify_connectivity()


def index(request):
    return render(request, 'index.html')


def all_movies(request):
    movies = list(movie_collection.find().sort({"_id": -1}).limit(10000))
    print(movies[0])

    return render(request, 'all.html',{'movies':movies})

@require_http_methods(['GET'])
def register_page(request):
    genres = get_genres()
    return render(request, 'register.html', {'genres': genres})


@require_http_methods(['POST'])
def register(request):
    user = LoggedUser(
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
    user = LoggedUser(email=request.POST.get('email'), password=request.POST.get('password'))
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
    movie = movie_collection.find_one({'_id': ObjectId(id)})
    movie['comments'] = sorted(movie['comments'], key=lambda x: x['date'], reverse=True)

    logged_user = LoggedUser(user=request.session['user'])

    request.session['user']['has_seen_movie'] = logged_user.has_seen_movie(id)
    request.session['user']['has_liked_movie'] = logged_user.has_liked_movie(id)

    return render(request, 'movie_details.html', {'movie': movie})


def get_user(request, id):
    user = User(user_collection.find_one({'_id': ObjectId(id)}))
    logged_user = LoggedUser(user=request.session['user'])

    user.get_watched_list()

    # count = 0
    # user.commented_movies = []
    # for movie in user.watched_list:
    #     user.commented_movies.append({
    #         "movie": movie,
    #         "comment": movie["comments"][0]
    #     })
    #     count += 1
    #     if count == 10:
    #         break
    #
    # genres = {}
    # for movie in user.watched_list:
    #     for genre in movie["genre"]:
    #         if genre not in genres.keys():
    #             genres[genre] = 1
    #         else:
    #             genres[genre] += 1
    #
    # user.favorite_genres = dict(sorted(genres.items(), key=lambda x:x[1], reverse=True))
    # user.last_activities = [
    #     {
    #         "action": "review",
    #         "review_id": "...",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     },
    #     {
    #         "action": "liked",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     },
    #     {
    #         "action": "watched",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     }
    # ]

    return render(request, 'user_page.html', {'user': user})




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

    user = LoggedUser(user=request.session.get('user'))

    user.get_watched_list()

    # count = 0
    # user.commented_movies = []
    # for movie in user.watched_list:
    #     user.commented_movies.append({
    #         "movie": movie,
    #         "comment": movie["comments"][0]
    #     })
    #     count += 1
    #     if count == 10:
    #         break
    #
    # genres_count = {}
    # for movie in user.watched_list:
    #     for genre in movie["genre"]:
    #         if genre not in genres_count.keys():
    #             genres_count[genre] = 1
    #         else:
    #             genres_count[genre] += 1
    #
    # user.favorite_genres = dict(sorted(genres_count.items(), key=lambda x: x[1], reverse=True))
    # user.last_activities = [
    #     {
    #         "action": "review",
    #         "review_id": "...",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     },
    #     {
    #         "action": "liked",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     },
    #     {
    #         "action": "watched",
    #         "movie": {
    #             "id": "657b2245d448da2cface22ea",
    #             "title": "The Godfather",
    #         },
    #         "date": datetime.date(2024, 1, 4)
    #     }
    # ]

    return render(request, 'user_profile.html', {"user": user, "genres": genres})

@require_http_methods(["POST"])
def update_preferences(request):
    preferences = [request.POST.get('preference_1'), request.POST.get('preference_2'), request.POST.get('preference_3')]

    user = LoggedUser(user=request.session.get('user'))
    user.set_preferences(preferences)

    return redirect('get_user_profile')


@require_http_methods(["POST"])
def mark_movie_as_seen(request, id):
    user = LoggedUser(user=request.session.get('user'))
    if user.see_movie(id):
        return HttpResponse(json.dumps({'message': 'Movie mark as seen'}))
    else:
        return HttpResponse(status=404)


@require_http_methods(["POST"])
def like_movie(request, id, value):
    user = LoggedUser(user=request.session.get('user'))
    if user.like_movie(id, value):
        return HttpResponse(json.dumps({'value': value}))
    else:
        return HttpResponse(status=404)


@require_http_methods(['POST'])
def add_review(request, id):
    user = LoggedUser(user=request.session['user'])

    comment = {
        'title': request.POST.get('title'),
        'date': datetime.datetime.now(),
        'content': request.POST.get('content'),
        'user': {
            'id': user.id,
            'lastName': user.last_name,
            'firtName': user.first_name
        }
    }

    try:
        movie_collection.update_one({'_id': ObjectId(id)}, {'$push': {'comments': comment}})
    except Exception as e:
        print('Error in updating movie comments. Error : ', e)
    else:
        user.add_review(id)

    return redirect('movie_details', id=id)