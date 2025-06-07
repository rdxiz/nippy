from django.shortcuts import render
from core.decorators import profile_required
from core.forms import StudioForm
from core.models import PlaylistInfo, Video


@profile_required
def my_account(request):
    options = {
        'account_settings': True,
    }
    return render(request, "studio/my_account.html", options)



@profile_required
def my_videos(request):
    options = {
        'video_manager': True,
        'videos': request.profile.videos.order_by('-id').all(),
        'studio_form': StudioForm(profile=request.profile)
    }
    return render(request, "studio/my_videos.html", options)

@profile_required
def my_playlists(request):
    options = {
        'video_manager': True,
        'playlists': request.profile.playlists.order_by('type', '-id').all(),
        
    }
    return render(request, "studio/my_playlists.html", options)

@profile_required
def video_edit(request, video_id):
    options = {
        'video_manager': True,
        'video': request.profile.videos.get(record_id=video_id),
        
    }
    return render(request, "studio/video_edit.html", options)

@profile_required
def playlist_edit(request, playlist_id):
    options = {
        'video_manager': True,
        'playlist': request.profile.playlists.get(record_id=playlist_id),
    }
    return render(request, "studio/playlist_edit.html", options)


