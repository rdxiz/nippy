"""
URL configuration for nippy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    # auth
    path("signup", views.signup, name="signup"),
    path("login", views.signin, name="signin"),
    path("logout", views.signout, name="signout"),
    # path("accounts/", include("django.contrib.auth.urls")),
    path("", views.index, name="index"),
    path("explore", views.view_explore, name="view_explore"),
    # logged in
    path("channel_switcher", views.profile_switcher, name="profile_switcher"),
    path("my_videos_upload", views.my_videos_upload, name="my_videos_upload"),
    path("my_videos", views.my_videos, name="my_videos"),
    path("my_videos/<str:video_id>/edit", views.video_edit, name="video_edit"),
    path("my_playlists", views.my_playlists, name="my_playlists"),
    path(
        "my_playlists/<str:playlist_id>/edit", views.playlist_edit, name="playlist_edit"
    ),
    path("my_account", views.my_account, name="my_account"),
    path("subscriptions", views.subscriptions, name="subscriptions"),
    path("c/<str:profile_handle>", views.profile_view, name="profile_custom_url"),
    path(
        "c/<str:profile_handle>/<str:page>",
        views.profile_view,
        name="profile_custom_url_page",
    ),
    path("channel/<str:profile_id>", views.profile_view, name="profile_default_url"),
    path(
        "channel/<str:profile_id>/<str:page>",
        views.profile_view,
        name="profile_default_url_page",
    ),
    path("watch", views.watch, name="watch"),
    path("results", views.results, name="results"),
    # ajax
    path("posts/new", views.new_post, name="new_post"),
    path("posts/delete", views.delete_post, name="delete_post"),
    path("video/upload", views.upload_video, name="upload_video"),
    path("video/new", views.new_video, name="new_video"),
    path("video/update", views.update_video, name="update_video"),
    path("video/status", views.video_status, name="video_status"),
    path("video/views", views.video_views, name="video_views"),
    path("video/ratings", views.video_ratings, name="video_ratings"),
    path("video/related", views.video_related, name="video_related"),
    path("video/<str:video_id>/comments", views.video_comments, name="video_comments"),
    path("follow", views.follow, name="follow"),
]
