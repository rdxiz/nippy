import functools
import os
from django.conf.global_settings import LANGUAGES
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError, models, transaction
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from sqids.sqids import Sqids
from core.fields import ResizedImageField
from core.types import (
    CommentsOptions,
    PlaylistType,
    PostAction,
    Rating,
    VideoCategory,
    VideoStatus,
    VideoVisibility,
)

# For generating String IDs


class Encoding:
    OTHER = 3
    PROFILE = 1
    VIDEO = 2


ENCODING_LEN = {
    Encoding.OTHER: 4,
    Encoding.PROFILE: 22,
    Encoding.VIDEO: 11,
}


class Sequential(models.Model):
    pass


SQUIDS_ALPHABET = os.environ.get("SQUIDS_ALPHABET", "XnpeHockQZ-47I6gV0Cs_aAhjf1l9GqPutS2EFyM8YdTOULWJvxmKDNiBz3wR5br")


def gen_str_id(encoding=None, length=None):
    num = Sequential.objects.create().id
    if not length:
        length = ENCODING_LEN[encoding]
    hasher = Sqids(alphabet=SQUIDS_ALPHABET, min_length=length)
    return hasher.encode([num])


class Queue(models.Model):
    payload = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)


class RateLimiter(models.Model):
    record_id = models.CharField(max_length=50, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    last_request = models.DateTimeField(default=timezone.now)


class User(AbstractUser):
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True, blank=True)
    pass
    # email = models.EmailField()
    # real_email = models.EmailField(unique=True) # Email without dots & plus...
    # email_verified = models.BooleanField(default=False)


class Profile(models.Model):
    record_id = models.CharField(
        max_length=22,
        default=functools.partial(gen_str_id, encoding=Encoding.PROFILE),
        unique=True,
        db_index=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    handle = models.CharField(
        null=True, blank=True, max_length=30, unique=True, db_index=True
    )
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    avatar = ResizedImageField(
        null=True, blank=True, upload_to="img/p/avatar/100", width=100, height=100
    )
    banner = ResizedImageField(null=True, blank=True, upload_to="img/p/banner")
    watermark = ResizedImageField(null=True, blank=True, upload_to="img/p/watermark")
    links = models.JSONField(null=True, blank=True)
    pl_likes = models.ForeignKey(
        "PlaylistInfo",
        null=True,
        blank=True,
        related_name="pl_likes",
        on_delete=models.SET_NULL,
    )
    pl_dislikes = models.ForeignKey(
        "PlaylistInfo",
        null=True,
        blank=True,
        related_name="pl_dislikes",
        on_delete=models.SET_NULL,
    )
    pl_history = models.ForeignKey(
        "PlaylistInfo",
        null=True,
        blank=True,
        related_name="pl_history",
        on_delete=models.SET_NULL,
    )
    pl_favorites = models.ForeignKey(
        "PlaylistInfo",
        null=True,
        blank=True,
        related_name="pl_favorites",
        on_delete=models.SET_NULL,
    )
    pl_watch_later = models.ForeignKey(
        "PlaylistInfo",
        null=True,
        blank=True,
        related_name="pl_watch_later",
        on_delete=models.SET_NULL,
    )
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.record_id})"

    @property
    def following_list(self):
        return self.follower.select_related("following")

    @property
    def followers_list(self):
        return self.following.select_related("follower")

    @property
    def get_id(self):
        return "UC" + self.record_id

    @property
    def get_url(self):
        return (
            reverse("core:profile_custom_url", args=[self.handle])
            if self.handle
            else reverse("core:profile_default_url", args=[self.get_id])
        )

    def is_following(self, profile):
        return Follow.objects.filter(follower=self, following=profile).exists()

    @transaction.atomic
    def follow(self, profile):
        if self.id == profile.id:
            return
        try:
            Follow.objects.create(follower=self, following=profile)
            Profile.objects.filter(id=self.id).update(
                following_count=models.F("following_count") + 1
            )
            Profile.objects.filter(id=profile.id).update(
                followers_count=models.F("followers_count") + 1
            )
        except IntegrityError:
            pass

    @transaction.atomic
    def unfollow(self, profile):
        if self.id == profile.id:
            return
        follow_instance = Follow.objects.filter(
            follower=self, following=profile
        ).first()
        if not follow_instance:
            return
        follow_instance.delete()
        Profile.objects.filter(id=self.id).update(
            following_count=models.F("following_count") - 1
        )
        Profile.objects.filter(id=profile.id).update(
            followers_count=models.F("followers_count") - 1
        )


class Follow(models.Model):
    follower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="follower"
    )
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="following"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("follower", "following")


class Video(models.Model):
    record_id = models.CharField(
        max_length=11,
        default=functools.partial(gen_str_id, encoding=Encoding.VIDEO),
        unique=True,
        db_index=True,
    )
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="videos")
    status = models.SmallIntegerField(
        choices=VideoStatus.CHOICES, default=VideoStatus.UPLOADING
    )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=5000, null=True, blank=True)
    short_description = models.CharField(max_length=300, null=True, blank=True)
    tags = ArrayField(
        models.CharField(max_length=20),
        size=15,
        null=True,
        blank=True,
    )
    visibility = models.SmallIntegerField(
        choices=VideoVisibility.CHOICES, default=VideoVisibility.PRIVATE
    )
    category = models.SmallIntegerField(
        choices=VideoCategory.CHOICES, default=VideoCategory.PEOPLE_AND_BLOGS
    )
    progress = models.SmallIntegerField(default=0)
    featured = models.BooleanField(default=False)
    featured_order = models.SmallIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    user_can_vote_on_comments = models.BooleanField(default=True)
    user_can_see_ratings = models.BooleanField(default=True)  # for the video
    positive_ratings = models.PositiveIntegerField(default=0)
    negative_ratings = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(null=True, blank=True, upload_to="vi/sd")
    thumbnail_0 = models.ImageField(null=True, blank=True, upload_to="img/vi/thumb/0")
    thumbnail_1 = models.ImageField(null=True, blank=True, upload_to="img/vi/thumb/1")
    thumbnail_2 = models.ImageField(null=True, blank=True, upload_to="img/vi/thumb/2")
    thumbnail = models.ImageField(null=True, blank=True, upload_to="img/vi/thumb")
    language = models.CharField(max_length=7, choices=LANGUAGES, null=True, blank=True)

    @property
    def get_absolute_url(self):
        return f"{reverse('core:watch')}?v={self.record_id}"

    @property
    def get_id(self):
        return self.record_id

    def __str__(self):
        return f"Video ({self.record_id})"


class ServerError(models.Model):
    author = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.SET_NULL
    )
    url = models.CharField(max_length=1000, null=True, blank=True)
    error = models.CharField(max_length=1000, null=True, blank=True)
    traceback = models.CharField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return self.error


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=5000, null=True, blank=True)
    action = models.SmallIntegerField(
        default=PostAction.POSTED, choices=PostAction.CHOICES
    )
    created_at = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.CharField(max_length=5000, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    positive_ratings = models.PositiveIntegerField(default=0)
    negative_ratings = models.PositiveIntegerField(default=0)


class CommentRating(models.Model):
    comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.CASCADE
    )
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=Rating.NEUTRAL, choices=Rating.CHOICES)


class PlaylistInfo(models.Model):
    record_id = models.CharField(
        max_length=16,
        default=functools.partial(gen_str_id, length=16),
        unique=True,
        db_index=True,
    )
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="playlists"
    )
    title = models.CharField(null=True, blank=True, max_length=100)
    type = models.SmallIntegerField(
        default=PlaylistType.CUSTOM, choices=PlaylistType.CHOICES
    )
    visibility = models.SmallIntegerField(
        choices=VideoVisibility.CHOICES, default=VideoVisibility.PRIVATE
    )
    created_at = models.DateTimeField(default=timezone.now)
    thumbnail = models.ImageField(null=True, blank=True, upload_to="img/vi/thumb")
    custom_thumbnail = models.BooleanField(default=False)

    @property
    def get_id(self):
        return self.record_id


class PlaylistVideo(models.Model):
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.CASCADE)
    playlist = models.ForeignKey(
        PlaylistInfo,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("video", "playlist")
