from datetime import datetime
import json
import random
import pymongo

from bson import ObjectId, json_util
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage

from objects.LoggedUser import LoggedUser
from objects.Movie import Movie
from objects.User import User
from utils_functions import get_genres
from statistics_function import *

from neo4j import GraphDatabase

import logging
logger = logging.getLogger("mylogger")

client = pymongo.MongoClient(host="localhost", port=27017, username=None, password=None)
document_db = client['cinema_circle']
movie_collection = document_db['movie']
user_collection = document_db['user']

graph_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "lsmdb_2024"), database="cinemacircle")

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


@require_http_methods(['GET'])
def admin_page(request):
    logged_user = LoggedUser(request.session['user'])
    if not logged_user.admin:
        return redirect('recommendations')

    users_activities_overview = []
    users_activities_overview.append({'title': 'Users', 'statistic': get_total_users_count()})
    users_activities_overview.append({'title': 'Actives users', 'statistic': get_active_users()})
    users_activities_overview.append({'title': 'New users', 'statistic': get_new_users_count()})

    users_activities=[]
    users_activities.append({'title': 'users have seen a movie', 'statistic': get_users_who_seen_movie()})
    users_activities.append({'title': 'users liked a movie', 'statistic': get_users_who_like_movie()})
    users_activities.append({'title': 'users have poster a review', 'statistic': get_users_who_posted_review()})
    users_activities.append({'title': 'movies seen per user', 'statistic': get_average_seens_per_user()})
    users_activities.append({'title': 'movies liked per user', 'statistic': get_average_likes_per_user()})
    users_activities.append({'title': 'reviews posted per user', 'statistic': get_average_reviews_per_user()})

    user_networking_activities = []
    user_networking_activities.append({'title': 'followers per user', 'statistic': get_average_followers_per_user()})
    user_networking_activities.append({'title': 'follows interaction', 'statistic': get_follows_interation()})

    return render(request, "admin_page.html", {'users_activities_overview': users_activities_overview, 'users_activities': users_activities, 'users_networking_activities': user_networking_activities})

@require_http_methods(['GET'])
def users_activities_overview(request, filter=None):
    users_activities_overview = []
    users_activities_overview.append({'title': 'Users', 'statistic': get_total_users_count()})
    users_activities_overview.append({'title': 'Actives users', 'statistic': get_active_users(filter)})
    users_activities_overview.append({'title': 'New users', 'statistic': get_new_users_count(filter)})

    return HttpResponse(json.dumps({'overview': users_activities_overview, 'filter': filter}))


@require_http_methods(['GET'])
def users_activities(request, filter=None):
    users_activities = []
    users_activities.append({'title': 'users have seen a movie', 'statistic': get_users_who_seen_movie(filter)})
    users_activities.append({'title': 'users liked a movie', 'statistic': get_users_who_like_movie(filter)})
    users_activities.append({'title': 'users have poster a review', 'statistic': get_users_who_posted_review(filter)})
    users_activities.append({'title': 'movies seen per user', 'statistic': get_average_seens_per_user(filter)})
    users_activities.append({'title': 'movies liked per user', 'statistic': get_average_likes_per_user(filter)})
    users_activities.append({'title': 'reviews posted per user', 'statistic': get_average_reviews_per_user(filter)})

    return HttpResponse(json.dumps({'activities': users_activities, 'filter': filter}))
@require_http_methods(['GET'])
def users_networking_activities(request, filter=None):
    user_networking_activities = []
    user_networking_activities.append({'title': 'followers per user', 'statistic': get_average_followers_per_user(filter)})
    user_networking_activities.append({'title': 'follows interaction', 'statistic': get_follows_interation(filter)})

    return HttpResponse(json.dumps({'activities': user_networking_activities, 'filter': filter}))


@require_http_methods(['GET'])
def movies_statistics(request):
    movies_statistics_overview = []
    movies_statistics_overview.append({'title': 'Movies', 'statistic': get_movies_count()})
    movies_statistics_overview.append({'title': 'Genres', 'statistic': get_genres_count()})

    movies_per_genre = []
    movies_genres = get_movies_per_genres()
    for genre in movies_genres:
        movies_per_genre.append({'title': genre['name'], 'statistic': genre['nb_movies']})

    popular_genres = []
    popular = get_popular_genres()
    for genre in popular:
        popular_genres.append({'title': 'Interactions on' + genre['name'], 'statistic': genre['movies_count']})

    detailled_statistics = []
    detailled_statistics.append({'title': 'Views per movie', 'statistic': get_average_views_per_movie()})
    detailled_statistics.append({'title': 'Likes per movie', 'statistic': get_average_like_interactions_per_movie()})
    detailled_statistics.append({'title': 'Reviews per movie', 'statistic': get_average_reviews_per_movie()})


    return HttpResponse(json.dumps({'overview': movies_statistics_overview, 'popular': popular_genres, 'movies_per_genre': movies_per_genre, 'detailled_statistics': detailled_statistics}))


def get_admin_popular_genres(request, filter):
    popular_genres = []
    popular = get_popular_genres(filter)
    for genre in popular:
        popular_genres.append({'title': 'Interactions on' + genre['name'], 'statistic': genre['movies_count']})

    return HttpResponse(json.dumps({'popular': popular_genres, 'filter': filter}))


def get_detailled_statistics(request, filter):
    detailled_statistics = []
    detailled_statistics.append({'title': 'Views per movie', 'statistic': get_average_views_per_movie(filter)})
    detailled_statistics.append({'title': 'Likes per movie', 'statistic': get_average_like_interactions_per_movie(filter)})
    detailled_statistics.append({'title': 'Reviews per movie', 'statistic': get_average_reviews_per_movie(filter)})

    return HttpResponse(json.dumps({'detailled_statistics': detailled_statistics, 'filter': filter}))


def get_movie_list(request, page):
    movies_list = list(movie_collection.find(projection=('title', 'release_date', 'runtime')).sort({'_id': -1}))
    paginator = Paginator(movies_list, 10)

    try:
        movies = paginator.page(page)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    return HttpResponse(json_util.dumps({'movies': movies.object_list, 'page': int(page)}))


def get_movie(request, id):
    movie = Movie(movie=movie_collection.find_one({'_id': ObjectId(id)}))

    return HttpResponse(json_util.dumps(movie.to_json()))


def add_movie(request):
    if request.POST.get('release_date'):
        date = request.POST.get('release_date').split('-')
        release_date = datetime(int(date[0]), int(date[1]), int(date[2]))
    else:
        release_date = None

    movie = Movie(
        title=request.POST.get('title'),
        release_date=release_date,
        runtime=int(request.POST.get('runtime')),
        genre=[request.POST.get('genre')],
        overview=request.POST.get('overview')
    )

    inserted_id = movie.create()
    return HttpResponse(json.dumps({'movie_id': str(inserted_id)}))

def edit_movie(request, id):
    movie = Movie(movie=movie_collection.find_one({'_id': ObjectId(id)}))


    if request.POST.get('release_date'):
        date = request.POST.get('release_date').split('-')
        release_date = datetime(int(date[0]), int(date[1]), int(date[2]))
    else:
        release_date = None
    movie.update_multiple_fields(
        title=request.POST.get('title'),
        release_date=release_date,
        runtime=int(request.POST.get('runtime')),
        genre=[request.POST.get('genre')],
        overview=request.POST.get('overview')
    )

    return HttpResponse(json.dumps({'movie_id': movie.id}))


def delete_movie(request, id):
    movie = Movie(id=id)
    movie.delete()

    return HttpResponse(json.dumps({'movie_id': movie.id}))
