from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path(
        'movies/',
        # Ознакомиться со списком фильмов
        views.MovieList.as_view(),
        name='MovieList'
    ),
    path(
        'movie/<int:movie_id>/vote/',
        # Проголосовать за конкретный фильм
        views.CreateVote.as_view(),
        name='CreateVote'
    ),

    path(
        'movie/<int:movie_id>/vote/<int:pk>/',
        views.UpdateVote.as_view(),
        # Обновить свой голос
        name='UpdateVote'
    ),

    path(
        'movie/<int:pk>/',
        # Ознакомиться с конкретным фильмом
        views.MovieDetail.as_view(),
        name='MovieDetail'
    ),

    path(
        'person/<int:pk>/',  # Посмотреть информацию о личности
        views.PersonDetail.as_view(),
        name='PersonDetail'
        ),
]
