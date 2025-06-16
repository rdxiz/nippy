import datetime
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from core.const import ALLOWED_VIDEO_TYPES
from core.decorators import profile_required
from core.forms import VideoUploadForm
from core.models import Follow, PlaylistVideo, Video
from core.types import RateLimit, VideoStatus, VideoVisibility
from core.utils.ratelimit import limit, limit_key
from core.utils.strings import rate_limit_msg


@profile_required
def my_videos_upload(request):
    with limit(
        limit_key(request.remote_addr, RateLimit.VIDEO_UPLOAD),
        limit=10,
        period="1d",
        save=False,
    ) as diff:
        if diff:
            messages.error(request, rate_limit_msg(diff))
            return redirect("core:index")
        options = {
            "form": VideoUploadForm(),
            "drop_form": VideoUploadForm(auto_id="%s"),
            "max_video_size": settings.MAXIMUM_VIDEO_SIZE_BYTES,
            "chunk_size": settings.CHUNK_SIZE_BYTES,
            "maximum_video_duration": settings.MAXIMUM_VIDEO_DURATION,
            "allowed_video_types": ALLOWED_VIDEO_TYPES,
        }
        return render(request, "legacy/my_videos_upload.html", options)


@profile_required
def results(request):
    return render(
        request,
        "legacy/results.html",
        {
            "videos": Video.objects.annotate(
                rank=SearchRank(
                    SearchVector("title", "description"),
                    SearchQuery(request.GET["search_query"], search_type="websearch"),
                )
            )
            .select_related("author")
            .filter(rank__gte=0.0001)
            .order_by("-rank")[:20]
        },
    )


def convert_ids(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.strftime("%a %b %d %H:%M:%S GMT %Y")
    if isinstance(obj, (FieldFile, ImageFieldFile)):
        return obj.url if obj else None
    else:
        return obj


def obj_to_dict(obj, fields):
    result = {}

    for field in fields:
        keys = field.split("__")
        value = obj

        # Traverse through the object attributes according to the keys
        for key in keys:
            value = getattr(value, key, None)
            if value is None:
                break
            value = convert_ids(value)

        # Create nested dictionary structure
        d = result
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        final_key = keys[-1]
        if final_key == "record_id":
            final_key = "id"
        d[final_key] = value

    return result


def watch(request):
    video_fields = [
        "author__name",
        "author__handle",
        "author__avatar",
        "author__record_id",
        "author__created_at",
        "created_at",
        "file",
        "status",
        "title",
        "description",
        "views",
        "thumbnail",
        "duration",
        "record_id",
        "positive_ratings",
        "negative_ratings",
        "comments_count",
        "allow_comments",
        "user_can_vote_on_comments",
        "user_can_see_ratings",
        "visibility",
    ]
    video = get_object_or_404(
        Video.objects.select_related("author").only(*video_fields),
        record_id=request.GET["v"],
    )

    options = {
        "video": video,
        "recommended_videos": Video.objects.filter(
            status=VideoStatus.ONLINE, visibility=VideoVisibility.PUBLIC
        )
        .select_related("author")
        .only(
            "author__name",
            "author__record_id",
            "author__handle",
            "created_at",
            "title",
            "views",
            "thumbnail",
            "duration",
            "record_id",
        )
        .order_by("-id")[:9],
    }
    if video.user_can_vote_on_comments:
        if video.negative_ratings == 0:
            options["ratings_ratio"] = 100.0 if video.positive_ratings > 0 else 0.0
        else:
            options["ratings_ratio"] = (
                video.positive_ratings
                / (video.positive_ratings + video.negative_ratings)
            ) * 100
    my_profile = request.profile
    if my_profile:
        options["is_following"] = my_profile.is_following(video.author)
        # options['is_liked'] = PlaylistVideo.objects.filter(video=video, pl_id=profile.pl_likes_id).exists()
        # options['is_disliked'] = PlaylistVideo.objects.filter(video=video, pl_id=profile.pl_dislikes_id).exists()
        options["is_liked"] = my_profile.pl_likes.videos.filter(video=video).exists()
        options["is_disliked"] = my_profile.pl_dislikes.videos.filter(
            video=video
        ).exists()

    return render(request, "legacy/watch.html", options)
