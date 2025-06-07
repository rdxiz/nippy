import mimetypes
import os
from core.types import CommentsOptions, VideoCategory, VideoVisibility
from django.core.files.storage import default_storage

from core.utils import mkdirs
PROFILE_VIEWS = ['core:profile_default_url', 'core:profile_default_url_page', 'core:profile_custom_url', 'core:profile_custom_url_page']
GUIDE_VIEWS = ['core:index', 'core:results', 'core:watch', 'core:subscriptions'] + PROFILE_VIEWS
SESSION_KEY_PROFILE = "__profile"
IMAGE_PATH = os.path.join(default_storage.location, 'img')
VIDEO_PATH = os.path.join(default_storage.location, 'vi')
VIDEO_PARTS_PATH = os.path.join(VIDEO_PATH, 'p')
VIDEO_PROCESSING_PATH = os.path.join(VIDEO_PATH, 'g')
VIDEO_SD_PATH = os.path.join(VIDEO_PATH, 'sd')
VIDEO_HD_PATH = os.path.join(VIDEO_PATH, 'hd')
mkdirs([IMAGE_PATH, VIDEO_PATH, VIDEO_PARTS_PATH, VIDEO_PROCESSING_PATH, VIDEO_SD_PATH, VIDEO_HD_PATH])
mkdirs([os.path.join(IMAGE_PATH, 'vi'), os.path.join(IMAGE_PATH, 'vi/thumb'), os.path.join(IMAGE_PATH, 'vi/thumb/0'), os.path.join(IMAGE_PATH, 'vi/thumb/1'), os.path.join(IMAGE_PATH, 'vi/thumb/2')])
ALLOWED_VIDEO_TYPES = [
    'video/mp4', # mp4
    'video/x-msvideo', # .avi
    'video/mpeg', # .mpeg
    'video/ogg', # .ogv
    'video/webm', # .webm
    'video/3gpp', # .3gp
    'video/3gpp2', # .3g2
    'video/x-ms-wmv', # .wmv
    'video/quicktime', # .mov
    'video/x-flv', # .flv
]