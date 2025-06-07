from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import PlaylistInfo, PlaylistVideo, Profile, User
from core.types import PlaylistType


@receiver(post_save, sender=User)
def create_default_profile(sender, instance, created, **kwargs):
    if not created:
        return
    Profile.objects.create(
        name=instance.username, 
        user=instance
    )
    
    
@receiver(post_save, sender=Profile)
def create_default_playlists(sender, instance, created, **kwargs):
    if not created:
        return
    
    if not instance.pl_watch_later:
        pl_watch_later = PlaylistInfo.objects.create(
            author=instance,
            type=PlaylistType.WATCH_LATER
        )
        instance.pl_watch_later = pl_watch_later
        instance.save()
        
    if not instance.pl_favorites:
        pl_favorites = PlaylistInfo.objects.create(
            author=instance,
            type=PlaylistType.FAVORITES
        )
        instance.pl_favorites = pl_favorites
        instance.save()
        
    # Create default playlists 
    if not instance.pl_likes:
        pl_likes = PlaylistInfo.objects.create(
            author=instance,
            type=PlaylistType.LIKES
        )
        instance.pl_likes = pl_likes
        instance.save()

    if not instance.pl_dislikes:
        pl_dislikes = PlaylistInfo.objects.create(
            author=instance,
            type=PlaylistType.DISLIKES
        )
        instance.pl_dislikes = pl_dislikes
        instance.save()

    

    if not instance.pl_history:
        pl_history = PlaylistInfo.objects.create(
            author=instance,
            type=PlaylistType.HISTORY
        )
        instance.pl_history = pl_history
        instance.save()

@receiver(post_save, sender=PlaylistVideo)
def set_playlist_thumb(sender, instance, created, **kwargs):
    if not created:
        return
    playlist = instance.playlist
    if not playlist or playlist.custom_thumbnail:
        return
    playlist.thumbnail = instance.video.thumbnail
    playlist.save()