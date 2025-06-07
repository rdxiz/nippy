
from core.const import GUIDE_VIEWS
from core.models import Profile
from core.types import PlaylistType, VideoStatus

def custom_context(request):
    
    context = {
        'app_name': 'nippy >>',
        # types
        'VideoStatus': VideoStatus,
        'PlaylistType': PlaylistType,
    }
    if request.resolver_match.view_name in GUIDE_VIEWS:
        if request.profile:
            context['subscriptions'] = request.profile.following_list.order_by('-id')[:8]
        else:
            context['recommended_profiles'] = Profile.objects.all().order_by('-id')[:8]
    return context