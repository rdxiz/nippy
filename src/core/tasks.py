import logging
import os
from huey import signals
from huey.contrib.djhuey import db_task, periodic_task, task, signal

from core.const import VIDEO_SD_PATH
from core.utils import random_str
from core.models import Video
from core.utils.video_processing import convert_video, logger



@task()
def process_video(video, input_path):
    upload_id = f"{random_str(32)}.mp4"
    output_path = os.path.join(VIDEO_SD_PATH, upload_id)
    output_absolute_path = os.path.join('vi/sd', upload_id)
    logger.info(f'Processing queue item {upload_id}')
    convert_video(video, input_path, output_path, output_absolute_path)
    logger.info(f'Converted to {output_path}')
    os.remove(input_path)