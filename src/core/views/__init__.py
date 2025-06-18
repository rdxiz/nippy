from django.db.models import Q
from django.shortcuts import redirect, render
from core.models import Video, Post
from core.types import PostAction, VideoVisibility
from nippy.settings import MASTER_PASSWORD
from core.decorators import ajax_only, profile_required


def explore(request):
    videos = Video.objects.filter(
        status=VideoStatus.ONLINE, visibility=VideoVisibility.PUBLIC
    )
    featured_videos = (
        videos.filter(featured=True)
        .only(
            "author__handle",
            "author__record_id",
            "author__name",
            "title",
            "description",
            "views",
            "created_at",
            "thumbnail",
            "duration",
            "record_id",
        )
        .select_related("author")
        .order_by("-featured_order")[:5]
    )
    videos = videos.only(
        "title",
        "description",
        "views",
        "created_at",
        "thumbnail",
        "duration",
        "record_id",
    ).order_by("-id")[:20]
    featured_videos = list(featured_videos)
    videos = list(videos)
    return render(
        request,
        "legacy/index.html",
        {
            "videos": videos,
            "featured_videos": featured_videos,
        },
    )


@profile_required
def view_explore(request):
    return explore(request)


def index(request):
    if not request.profile and request.user.is_authenticated:
        return redirect("core:profile_switcher")

    if request.profile:
        options = {}
        post_select = Post.objects.select_related("author").select_related("video")
        post_select = post_select.only(
            "author__name",
            "author__handle",
            "author__avatar",
            "author__record_id",
            "video__title",
            "video__short_description",
            "video__views",
            "video__thumbnail",
            "video__duration",
            "video__record_id",
            "id",
            "text",
            "action",
            "created_at",
        )
        if request.profile.following_count > 1:
            posts = (
                post_select.filter(author__following__follower=request.profile)
                .filter(
                    Q(video__visibility=VideoVisibility.PUBLIC)
                    | Q(action=PostAction.POSTED)
                )
                .order_by("-id")[:20]
            )
            options["posting_form"] = FeedForm(auto_id="posting-%s")
        else:
            posts = post_select.filter(
                action=PostAction.UPLOADED, video__visibility=VideoVisibility.PUBLIC
            ).order_by("-id")[:20]
            options["homepage_alert"] = True
        options["posts"] = posts
        return render(request, "legacy/home.html", options)
    return explore(request)


def subscriptions(request):
    return render(
        request,
        "legacy/subscriptions.html",
        {
            "total_subscriptions": request.profile.following_list.order_by("-id")[:100],
        },
    )


from .ajax import *
from .auth import *
from .profile import *
from .video import *
from .settings import *
from .webapp import *
