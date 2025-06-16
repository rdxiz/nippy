from debug_toolbar.utils import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import F
from django.templatetags.static import static
from django.urls import reverse

from core.templatetags.filters import format_duration, get_thumbnail
from .models import *

admin.site.site_title = "Nippy site admin"
admin.site.site_header = "Nippy administration"
admin.site.index_title = "Site administration"

# Register your models here.
admin.site.register(User, UserAdmin)

admin.site.register(Queue)
admin.site.register(RateLimiter)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id","profile_picture", "url", "name", "followers_count", "following_count",  "created_at", "user", ]
    readonly_fields = ["record_id"]
    list_select_related = ["user"]
    def url(self, obj):
        profile_url = obj.get_url
        return format_html(f'<a href="{profile_url}">{profile_url}</a>')
    
    def profile_picture(self, obj):
        return format_html('<img src="{}" width="48"/>'.format(obj.avatar.url if obj.avatar else static('img/silhouette100.png')))


    # list_select_related = ["venue"]
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Follow)

@admin.action(description="Feature video")
def feature_video(modeladmin, request, queryset):
    queryset.update(featured=True)

@admin.action(description="Increase featured order")
def increase_feature_video(modeladmin, request, queryset):
    queryset.update(featured_order=F('featured_order') + 1)

@admin.action(description="Decrease featured order")
def decrease_feature_video(modeladmin, request, queryset):
    queryset.update(featured_order=F('featured_order') - 1)

@admin.action(description="Remove video feature")
def remove_feature_video(modeladmin, request, queryset):
    queryset.update(featured=False, featured_order=0)

class VideoAdmin(admin.ModelAdmin):
    
    def url(self, obj):
        video_url = f"{reverse('core:watch')}?v={obj.record_id}"
        return format_html(f'<a href="{video_url}">{video_url}</a>')
    
    def video_author(self, obj):
        return format_html(f'<a href="{obj.author.get_url}">{obj.author.name}</a>')
    def duration_field(self, obj):
        return format_duration(obj.duration)
    duration_field.short_description = 'duration'
    def video_thumbnail(self, obj):
        html = '<img src="{}" height="60"/>'.format(get_thumbnail(obj.thumbnail))
        return format_html(html)
    def generated_thumbnails(self, obj):
        html = '<img src="{}" height="30"/>'.format(get_thumbnail(obj.thumbnail_0))
        html = html + '<img src="{}" height="30"/>'.format(get_thumbnail(obj.thumbnail_1))
        html = html + '<img src="{}" height="30"/>'.format(get_thumbnail(obj.thumbnail_2))
        return format_html(html)
    list_display = ["id", "video_author", "url", "video_thumbnail", "generated_thumbnails",  "duration_field", "status", "visibility", "featured","featured_order", "title",  "views",  "positive_ratings",  "negative_ratings", "comments_count",  "created_at",]
    readonly_fields = ["record_id", "thumbnail_0", "thumbnail_1", "thumbnail_2",]
    list_select_related = ["author"]
    search_fields = ["title", "description", "record_id", "id", "author__name"]
    ordering = ['-featured', '-id']
    actions = [feature_video, remove_feature_video, increase_feature_video, decrease_feature_video]
    
admin.site.register(Video, VideoAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(CommentRating)
admin.site.register(PlaylistInfo)
admin.site.register(PlaylistVideo)

class ServerErrorAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    list_display = ["id", "error", "url", "author"]
    readonly_fields = ["author", "url", "error", "traceback"]
admin.site.register(ServerError, ServerErrorAdmin)
