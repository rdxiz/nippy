from datetime import timedelta
from io import BytesIO
import os
import random
import string
import sys
from PIL import Image, ImageOps, ImageSequence
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from sqids import Sqids

# chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def random_str(length=16):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for i in range(length))
    return random_string


def mkdirs(path_list: list):
    for path in path_list:
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
