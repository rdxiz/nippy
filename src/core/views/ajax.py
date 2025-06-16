import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.files.storage import default_storage
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import puremagic

from core.const import ALLOWED_VIDEO_TYPES, VIDEO_PARTS_PATH, VIDEO_PROCESSING_PATH
from core.decorators import ajax_only, profile_required
from core.forms import FeedForm, VideoUploadForm
from core.models import Comment, PlaylistVideo, Post, Profile, Queue, Video
from core.types import (
    CommentsOptions,
    QueueType,
    RateLimit,
    VideoStatus,
    VideoVisibility,
)
from core.utils.ratelimit import limit, limit_key
from core.utils.strings import rate_limit_msg
from core.tasks import process_video


@csrf_exempt
@profile_required
def delete_post(request):
    Post.objects.filter(author=request.profile, id=request.POST["id"]).delete()
    return HttpResponse("")


@profile_required
def new_post(request):
    form = FeedForm(data=request.POST)
    if not form.is_valid():
        return render(
            request, "legacy/widgets/forms/posting.html", {"form": form}, status=406
        )

    Post.objects.create(
        author=request.profile,
        text=form.cleaned_data["text"],
        video=form.cleaned_data["link"],
    )

    return render(
        request,
        "legacy/widgets/feed.html",
        {
            "posts": Post.objects.select_related("author")
            .select_related("video")
            .filter(author=request.profile)
            .order_by("-id")[:20],
        },
    )


@profile_required
def video_comments(request, video_id):
    video = Video.objects.only("id", "record_id").get(record_id=video_id)
    video_content_type = ContentType.objects.get_for_model(Video)
    comments = Comment.objects.filter(
        content_type=video_content_type, object_id=video.id
    )

    return render(
        request,
        "legacy/widgets/comment_list.html",
        {
            "comments": comments,
        },
    )


@profile_required
def update_video(request):
    current_tab = int(request.POST["current_tab"])
    video_id = request.POST["video_id"]
    form = VideoUploadForm(data=request.POST)
    if not form.is_valid():
        return render(
            request,
            "legacy/widgets/forms/video_upload.html",
            {"form": form, "tab": current_tab},
            status=406,
        )
    try:
        data = form.cleaned_data
        data["short_description"] = (
            Truncator(data["description"]).chars(300) if data["description"] else None
        )
        data["allow_comments"] = (
            f"{CommentsOptions.ALLOW_COMMENTS}" in data["comments_options"]
        )
        data["user_can_vote_on_comments"] = (
            f"{CommentsOptions.USER_CAN_VOTE_ON_COMMENTS}" in data["comments_options"]
        )
        data["user_can_see_ratings"] = (
            f"{CommentsOptions.USER_CAN_SEE_RATINGS}" in data["comments_options"]
        )
        data.pop("comments_options")
        video = Video.objects.filter(record_id=video_id, author=request.profile)
        # ugly...
        if data["thumbnail"] == "0":
            data["thumbnail"] = video[0].thumbnail_0.name
        elif data["thumbnail"] == "1":
            data["thumbnail"] = video[0].thumbnail_1.name
        elif data["thumbnail"] == "2":
            data["thumbnail"] = video[0].thumbnail_2.name
        else:
            data.pop("thumbnail")
        video.update(**data)
    except Exception as e:
        raise e
        return render(
            request,
            "legacy/widgets/forms/video_upload.html",
            {"form": form, "tab": current_tab},
            status=406,
        )
    return render(
        request,
        "legacy/widgets/forms/video_upload.html",
        {"form": form, "tab": current_tab},
    )


@csrf_exempt
def video_views(request):
    if request.method != "POST":
        return HttpResponse("", status=400)

    video_id = request.POST.get("video_id")
    if not video_id:
        return HttpResponse("", status=400)
    try:
        video = (
            Video.objects.select_related("author")
            .only("id", "views", "author__id", "author__view_count")
            .get(record_id=video_id)
        )
    except Video.DoesNotExist:
        return HttpResponse("", status=404)

    with limit(
        limit_key(request.remote_addr, RateLimit.VIEWS, video.id), limit=5, period="90s"
    ) as diff:
        if diff or video.views > 300:
            return HttpResponse(intcomma(video.views))
        views = video.views + 1
        video.views = F("views") + 1
        video.save()
        video.author.view_count = F("view_count") + 1
        video.author.save()
        if request.profile:
            pl_history = request.profile.pl_history.videos

            try:
                video_watched = pl_history.get(video=video)
                video_watched.created_at = timezone.now()
                video_watched.save()
            except PlaylistVideo.DoesNotExist:
                pl_history.create(video=video)
        return HttpResponse(intcomma(views))


@profile_required
@csrf_exempt
def video_ratings(request):
    if request.method != "POST":
        return HttpResponse("", status=400)
    video_id = request.POST.get("video_id")
    if not video_id:
        return HttpResponse("", status=400)
    decoded_id = video_id
    try:
        video = Video.objects.only("id", "positive_ratings", "negative_ratings").get(
            record_id=decoded_id
        )
    except Video.DoesNotExist:
        return HttpResponse("", status=404)

    rating = request.POST.get("rating")
    pl_likes = request.profile.pl_likes.videos
    pl_dislikes = request.profile.pl_dislikes.videos

    def remove_likes():
        try:
            liked_video = pl_likes.get(video=video)
        except PlaylistVideo.DoesNotExist:
            return
        liked_video.delete()
        video.positive_ratings = video.positive_ratings - 1

    def remove_dislikes():
        try:
            disliked_video = pl_dislikes.get(video=video)
        except PlaylistVideo.DoesNotExist:
            return
        disliked_video.delete()
        video.negative_ratings = video.negative_ratings - 1

    if rating == "0":
        remove_likes()
        remove_dislikes()
    elif rating == "1":
        try:
            pl_likes.get(video=video)
        except PlaylistVideo.DoesNotExist:
            remove_dislikes()
            pl_likes.create(video=video)
            video.positive_ratings = video.positive_ratings + 1
    elif rating == "-1":
        try:
            pl_dislikes.get(video=video)
        except PlaylistVideo.DoesNotExist:
            remove_likes()
            pl_dislikes.create(video=video)
            video.negative_ratings = video.negative_ratings + 1
    video.save()

    return HttpResponse(
        f'["{intcomma(video.positive_ratings)}", "{intcomma(video.negative_ratings)}"]'
    )


@profile_required
@csrf_exempt
def follow(request):
    if request.method != "POST":
        return HttpResponse("", status=400)

    profile = Profile.objects.get(record_id=request.POST.get("profile_id"))

    follow = request.POST.get("follow") == "true"
    if follow:

        request.profile.follow(profile)
    else:
        request.profile.unfollow(profile)

    return HttpResponse(
        Profile.objects.values_list("followers_count", flat=True).filter(pk=profile.id)
    )


@profile_required
@csrf_exempt
def video_status(request):
    video = Video.objects.only(
        "status", "progress", "thumbnail_0", "thumbnail_1", "thumbnail_2"
    ).get(record_id=request.POST["video_id"], author=request.profile)
    response = {
        "status": video.status,
        "progress": video.progress,
        "thumbnail": (
            [
                str(video.thumbnail_0.url),
                str(video.thumbnail_1.url),
                str(video.thumbnail_2.url),
            ]
            if video.thumbnail_0
            else []
        ),
    }

    return JsonResponse(response, safe=False)


@csrf_exempt
def video_related(request):
    related_videos = (
        Video.objects.select_related("author")
        .only("thumbnail", "title", "author__name", "record_id", "id")
        .filter(status=VideoStatus.ONLINE, visibility=VideoVisibility.PUBLIC)[:9]
    )
    return render(
        request,
        "legacy/widgets/player_end_screen.html",
        {"related_videos": related_videos},
    )


@profile_required
@csrf_exempt
def upload_video(request):
    chunk = request.FILES["file"]
    chunk_number = int(request.POST["chunk"])
    total_chunks = int(request.POST["total_chunks"])

    video = Video.objects.get(
        record_id=request.POST["video_id"], author=request.profile
    )

    upload_id = f"{video.record_id}.part"
    if total_chunks > settings.TOTAL_CHUNKS:
        video.delete()
        return HttpResponse("", status=413)

    if chunk_number < 1:
        file_type = puremagic.from_stream(chunk, mime=True)
        print(file_type)
        if not file_type.startswith("video/"):
            video.delete()
            return HttpResponse("", status=400)
    file_path = os.path.join(VIDEO_PARTS_PATH, upload_id)

    with default_storage.open(file_path, "ab") as destination:
        for chunk_data in chunk.chunks():
            destination.write(chunk_data)

    if chunk_number + 1 == total_chunks:
        video.status = VideoStatus.PROCESSING
        video.save()
        # foram feitos upload de todos os chunks, hora de renomear o arquivo e processar.
        final_path = os.path.join(VIDEO_PROCESSING_PATH, upload_id)
        os.rename(file_path, final_path)
        # parte de processamento, queue!
        process_video(video, final_path)
        # Queue.objects.create(payload={
        #     'id': video.id,
        #     'type': QueueType.PROCESS_VIDEO,
        #     'path': final_path
        # })
        return HttpResponse("")
    # Upload do chunk feito com sucesso, realizando outro upload.
    return HttpResponse("")


@profile_required
@csrf_exempt
def new_video(request):
    with limit(
        limit_key(request.remote_addr, RateLimit.VIDEO_UPLOAD), limit=10, period="1d"
    ) as diff:
        if diff:
            return HttpResponse(rate_limit_msg(diff), 429)
    video = Video.objects.create(
        title=request.POST["title"][:100], author=request.profile
    )
    return HttpResponse(video.get_id)
