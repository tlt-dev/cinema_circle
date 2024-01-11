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
        profile_pic_path='avatar_' + str(random.randint(1,10)) + '.png',
        admin=request.POST.get('admin')
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
    logged_user = LoggedUser(user=request.session['user'])

    displayed_movies = list()
    to_display = logged_user.get_popular_movies()
    recommandations = [
        {
            "category_title": "Popular movies",
            "movie_list": to_display
        }]
    displayed_movies += to_display
    logged_user.get_favorites_genres()
    
    for genre in logged_user.favorite_genres[:3]:
        to_display = logged_user.get_recommended_movie_from_genre(genre["genre"], [d['_id'] for d in displayed_movies if '_id' in d])
        recommandations.append({"category_title":"Because you like " + genre["genre"] + " movies", 
                                    "movie_list": to_display})
        displayed_movies += to_display

    return render(request, 'movie_recommandations.html', {'recommandations': recommandations})


def movie_details(request, id):
    movie = movie_collection.find_one({'_id': ObjectId(id)})
    movie['comments'] = sorted(movie['comments'], key=lambda x: x['date'], reverse=True)

    logged_user = LoggedUser(user=request.session['user'])

    request.session['user']['has_seen_movie'] = logged_user.has_seen_movie(id)
    request.session['user']['has_liked_movie'] = logged_user.has_liked_movie(id)

    return render(request, 'movie_details.html', {'movie': movie})


def get_user_page(request, id):
    user = User(user_collection.find_one({'_id': ObjectId(id)}))
    logged_user = LoggedUser(user=request.session['user'])

    request.session['user']['is_following'] = logged_user.is_following(id)

    user.get_watched_list(
        request.GET.get('watched_list_filter')) if 'watched_list_filter' in request.GET else user.get_watched_list()
    user.get_favorites_genres(request.GET.get(
        'favorite_genres_filter')) if 'favorite_genres_filter' in request.GET else user.get_favorites_genres()
    user.get_liked_movies_count()
    user.get_disliked_movies_count()
    user.get_reviews_count()
    user.get_last_activities(request.GET.get(
        'last_activities_filter')) if 'last_activities_filter' in request.GET else user.get_last_activities()

    filter = ""
    if 'last_activities_filter' in request.GET:
        filter = {"last_activities_filter": request.GET.get('last_activities_filter')}
    if 'favorite_genres_filter' in request.GET:
        filter = {"favorite_genres_filter": request.GET.get('favorite_genres_filter')}
    if 'watched_list_filter' in request.GET:
        filter = {"watched_list_filter": request.GET.get('watched_list_filter')}


    return render(request, 'user_page.html', {'user': user, 'filter': filter})


def get_recommanded_users(request):

    logged_user = LoggedUser(user=request.session['user'])

    recommandations = [
        {
            "category_title": "Most actives",
            "user_list": logged_user.get_most_active_users()
        },
        {
            "category_title": "Popular users",
            "user_list": logged_user.get_most_popular_users()
        }]
    logged_user.get_favorites_genres()
    recommanded_user_list = logged_user.get_recommanded_user_with_genre([data["genre"] for data in logged_user.favorite_genres[:3]])
    
    for genre in logged_user.favorite_genres[:3]:
        recommandations.append({
            "category_title": "People who likes " + genre["genre"],
            "user_list": logged_user.get_recommanded_user_by_genre(recommanded_user_list[genre["genre"]])
        })

    return render(request, 'users_recommandations.html', {'recommandations': recommandations})


def get_user_profile(request):
    genres = get_genres()

    user = LoggedUser(user=request.session.get('user'))

    user.get_watched_list(request.GET.get('watched_list_filter')) if 'watched_list_filter' in request.GET else user.get_watched_list()
    user.get_favorites_genres(request.GET.get('favorite_genres_filter')) if 'favorite_genres_filter' in request.GET else user.get_favorites_genres()
    user.get_liked_movies_count()
    user.get_disliked_movies_count()
    user.get_reviews_count()
    user.get_last_activities(request.GET.get('last_activities_filter')) if 'last_activities_filter' in request.GET else user.get_last_activities()

    filter = ""
    if 'last_activities_filter' in request.GET:
        filter = {"last_activities_filter": request.GET.get('last_activities_filter')}
    if 'favorite_genres_filter' in request.GET:
        filter = {"favorite_genres_filter": request.GET.get('favorite_genres_filter')}
    if 'watched_list_filter' in request.GET:
        filter = {"watched_list_filter": request.GET.get('watched_list_filter')}


    return render(request, 'user_profile.html', {"user": user, "genres": genres, "filter": filter})

@require_http_methods(["POST"])
def follow_user(request, id, value):
    logged_user = LoggedUser(user=request.session.get('user'))

    logged_user.follow_user(id, value)

    return HttpResponse(json.dumps({'value': value}))


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



def admin_page(request):
    pass