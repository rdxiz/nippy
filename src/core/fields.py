import os
from django.db import models
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile

from core.utils import random_str

class ResizedImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', 48)
        self.height = kwargs.pop('height', 48)
        self.alpha = kwargs.pop('alpha', False)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)

        if file and (self.width or self.height):
            self.resize_image(file, model_instance)

        return file

    def resize_image(self, file, model_instance):
        size = (self.width, self.height)
        file_extension = 'JPEG'
        
        img = Image.open(file)
        method = Image.NEAREST if img.size == size else Image.LANCZOS
        img = img.convert('RGB')
        img = ImageOps.fit(img, size, method=method, bleed=0.0, centering=(0.5, 0.5))
    
        temp = BytesIO()
        img.save(temp, format=file_extension, quality=80)
        temp.seek(0)
        file.name = f"{random_str()}.{file_extension.lower()}"
            
        # Save the resized image back to the model field
        file.save(file.name, ContentFile(temp.read()), save=False)