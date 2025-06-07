from io import BytesIO
from PIL import Image, ImageOps
from django import forms
from django.conf.global_settings import LANGUAGES
from django.contrib.auth import get_user_model
from django.db.models import Q

from core.models import Profile, User, Video
from core.types import CommentsOptions, PlaylistType, VideoActions, VideoCategory, VideoVisibility
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm




class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""


class CreateProfileForm(BaseForm):
    name = forms.CharField(max_length=50)
    avatar = forms.ImageField(required=False)
    

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')


class SignInForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')

class StudioForm(BaseForm):
    actions = forms.ChoiceField(
        choices=VideoActions.CHOICES,
        initial=VideoActions.ACTIONS,
        label="Video actions",
        required=False,
        disabled=True
    )
    playlists = forms.ChoiceField(
        label="Playlists",
        required=False,
        disabled=True
    )
    def __init__(self, *args, **kwargs):
        profile : Profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        playlists = profile.playlists.filter(Q(type=PlaylistType.CUSTOM) | Q(type=PlaylistType.FAVORITES))
        choices = [('-1', 'Playlists')]
        for playlist in playlists:
            choices.append((playlist.record_id, playlist.title if playlist.type is not PlaylistType.FAVORITES else "Favorites"))
        self.fields['playlists'].choices = choices
        self.fields['playlists'].initial = '-1'
    
    
class FeedForm(BaseForm):
    text = forms.CharField(
        label="Description", 
        widget=forms.Textarea(attrs={'placeholder': 'Create a new Post'}),
        max_length=5000
        )
    link = forms.CharField(
        label="Link", 
        widget=forms.TextInput(attrs={'placeholder': 'Add a new video or playlist link to feature (optional)'}),
        max_length=100,
        required=False
    )
    def clean_link(self):
        link = self.cleaned_data['link']
        if not link: return
        invalid_video_error = forms.ValidationError(("Invalid video URL!"))
        if 'watch?v=' not in link:
            raise invalid_video_error
        try:
            return Video.objects.get(record_id=link.split('watch?v=', maxsplit=1)[1])
        except Video.DoesNotExist:
            raise invalid_video_error


class CommentForm(BaseForm):
    text = forms.CharField(
        label="Type something", 
        widget=forms.Textarea(attrs={'placeholder': 'Create a new Post'}),
        max_length=5000
    )
        

class VideoUploadForm(BaseForm):
    thumbnail = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(label="Title", max_length=100)
    description = forms.CharField(
        label="Description", 
        widget=forms.Textarea(),
        max_length=5000, required=False
    )
    tags = forms.CharField(
        label="Tags", 
        widget=forms.TextInput(attrs={'placeholder': 'Tags (ex. mashup, albert einstein, peppa pig)'}),
        max_length=100, required=False
    )
    visibility = forms.ChoiceField(
        choices=VideoVisibility.CHOICES,
        label="Privacy settings",
        required=True,
        initial=VideoVisibility.PUBLIC
    )
    language = forms.ChoiceField(
        choices=LANGUAGES,
        label="Language",
        required=True,
    )
    category = forms.ChoiceField(
        choices=VideoCategory.CHOICES,
        label="Category",
        required=True,
        initial=VideoCategory.PEOPLE_AND_BLOGS
    )
    comments_options = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CommentsOptions.CHOICES,
        initial=[CommentsOptions.ALLOW_COMMENTS, CommentsOptions.USER_CAN_SEE_RATINGS, CommentsOptions.USER_CAN_VOTE_ON_COMMENTS]
    )
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if ', ' not in tags:
            return []
        return tags.split(', ')