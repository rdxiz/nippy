

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.const import SESSION_KEY_PROFILE
from core.forms import CreateProfileForm, FeedForm
from core.models import Follow, Post, Profile, Video
from core.types import RateLimit, VideoStatus, VideoVisibility
from core.utils.ratelimit import limit, limit_key, limits
from core.utils.strings import rate_limit_msg


@login_required
def profile_switcher(request):
    # needs improvement
    profile_id = request.GET.get('c', None)
    if profile_id:
        profile = Profile.objects.get(record_id=profile_id,user=request.user)
        request.session[SESSION_KEY_PROFILE] = profile.id
        return redirect("core:index")
    options = {
        "form": CreateProfileForm(request.POST or None, request.FILES or None),
        "modal": request.GET.get('create', None)
    }
    
    
    if request.method == 'POST':
        
        options["form"] = CreateProfileForm(request.POST, request.FILES)
        form = options["form"]
        if form.is_valid():
            with limits(
                limit_key(request.remote_addr, RateLimit.PROFILE_CREATION),
                limits=[(2, '1m'), (1, '5s')]
            ) as diff:
                if diff:
                    form.add_error('name', rate_limit_msg(diff))
                    return render(request, "profile_switcher.html", options)

            data = form.cleaned_data
            profile = Profile.objects.create(
                name=data['name'], 
                avatar=data.get('avatar'), 
                user=request.user
            )
            request.session[SESSION_KEY_PROFILE] = profile.id
            return redirect("core:index")
        else:
            options["modal"] = True
    options["profiles"] = Profile.objects.filter(user=request.user)
    options["modal"] = options["modal"] or len(options["profiles"]) < 1 
    return render(request, "profile_switcher.html", options)
        

def profile_view(request, profile_id=None, profile_handle=None, page=None):
    options = {}
    if profile_id:
        profile_id = profile_id[2:]
        if not request.profile or request.profile.record_id != profile_id:
            profile = get_object_or_404(Profile, record_id=profile_id) 
        else: 
            profile = request.profile
            options['my_profile'] = True
    else:
        profile = get_object_or_404(Profile, handle=profile_handle)
    related_profiles = None

    if profile.following_count > 0:
        related_profiles = profile.following_list
        if request.profile:
            # get last 8 users and see if you're following them
            following_subquery = Follow.objects.filter(
                follower=request.profile,
                following=OuterRef('following_id')
            ).values('id')

            related_profiles = related_profiles.annotate(
                is_following=Exists(following_subquery)
            )
        related_profiles = related_profiles.all().order_by('-following__followers_count')[:8]
    if not page:
        post_select = profile.posts.select_related('author').select_related('video')
        posts = post_select.only(
            'author__name', 'author__handle', 'author__avatar', 'author__record_id',
            'video__record_id', 'video__title', 'video__short_description', 'video__views', 'video__thumbnail', 'video__duration', 
            'id', 'text', 'action', 'created_at',
        )
        options['posts'] = list(posts.order_by('-id')[:20])
    elif page == 'videos':
        options['videos'] = list(profile.videos.filter(status=VideoStatus.ONLINE, visibility=VideoVisibility.PUBLIC).only('record_id', 'author_id', 'title', 'description', 'views','created_at', 'thumbnail', 'duration').order_by('-id')[:20])
    options['profile'] = profile
    if not options.get('my_profile', None) and request.profile:
        options['is_following'] = request.profile.is_following(profile)
    options['form'] = FeedForm(auto_id="posting-%s")
    options['page'] = page
    options['related_profiles'] = related_profiles
    return render(request, "profile.html", options)
    
