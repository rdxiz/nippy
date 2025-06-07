import json
import logging
import os
import shlex
from threading import Thread
import time
import subprocess as sp

from django.core.files.storage import default_storage
from django.db import transaction
from django.conf import settings
from core.models import Post, Video
from core.types import PostAction, VideoStatus, VideoVisibility
from core.utils import random_str
from core.utils.video_processing.exceptions import VideoTooLong
from nippy.settings import FFMPEG_PATH, FFPROBE_PATH

logger = logging.getLogger("nippy")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] INFO:nippy:%(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

supported_resolutions = [
    (256, 144),
    (426, 240),
    (640, 360),
]


def progress_reader(proc, q):
    while True:
        if proc.poll() is not None:
            break

        progress_text = proc.stdout.readline()
        if not progress_text:
            break

        progress_text = progress_text.decode("utf-8").strip()
        if progress_text.startswith("frame="):
            frame = int(progress_text.partition("=")[-1].strip())
            q[0] = frame


def get_video_resolution(input_path):
    try:
        command = [
            FFPROBE_PATH,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            input_path,
        ]
        result = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, check=True)
        resolution = result.stdout.decode().strip()

        width, height = map(int, resolution.split(","))
        return width, height
    except sp.CalledProcessError as e:
        logger.error(f"Error getting video resolution: {e}")
        return None, None


def get_video_duration(input_path):
    try:
        command = [
            FFPROBE_PATH,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_path,
        ]
        data = sp.run(command, stdout=sp.PIPE, check=True).stdout
        seconds = float(data.strip())
        logger.info(f"{seconds} seconds")
        return seconds
    except sp.CalledProcessError as e:
        logger.error(f"Error getting video duration: {e}")
        return 0


def get_total_n_frames(input_path):
    data = sp.run(
        shlex.split(
            f"{FFPROBE_PATH} -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of json '{input_path}'"
        ),
        stdout=sp.PIPE,
        check=True,
    ).stdout
    metadata = json.loads(data)
    tot_n_frames = float(metadata["streams"][0]["nb_read_packets"])
    logger.info(f"{tot_n_frames} frames total")
    return tot_n_frames


def update_video_progress(video_id, progress_percent):
    with transaction.atomic():
        Video.objects.filter(id=video_id).update(progress=progress_percent)


def generate_thumbnail(input_path, thumbnail_path, timestamp, resolution):
    command = [
        FFMPEG_PATH,
        "-y",
        "-loglevel",
        "error",
        "-ss",
        str(timestamp),
        "-i",
        input_path,
        "-vf",
        f"thumbnail,scale={resolution[0]}:{resolution[1]}",  # Scale and generate thumbnail
        "-frames:v",
        "1",
        thumbnail_path,
    ]
    logger.info(" ".join(command))
    sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE)
    logger.info(f"Thumbnail generated at: {thumbnail_path}")


def generate_thumbnails(
    video_id, duration, input_path, input_absolute_path, resolution
):
    folder = "img/vi/thumb"
    folder_path = os.path.join(default_storage.location, folder)
    each_sec = int(duration / 3)
    thumbnail_paths = [
        f"0/{random_str(32)}.jpg",
        f"1/{random_str(32)}.jpg",
        f"2/{random_str(32)}.jpg",
    ]
    update = {
        "status": VideoStatus.ONLINE,
        "duration": duration,
        "file": input_absolute_path,
    }
    for index, path in enumerate(thumbnail_paths):
        generate_thumbnail(
            input_path, os.path.join(folder_path, path), each_sec * index, resolution
        )
        image_field = os.path.join("img/vi/thumb", thumbnail_paths[index])
        logger.info(f"Imagefield name {image_field}")

        update[f"thumbnail_{index}"] = image_field

    update["thumbnail"] = update["thumbnail_0"]
    update["status"] = VideoStatus.ONLINE

    with transaction.atomic():
        video = Video.objects.filter(id=video_id)
        video.update(**update)
        video = video[0]
        if video.visibility == VideoVisibility.PUBLIC:
            Post.objects.create(
                author=video.author, video=video, action=PostAction.UPLOADED
            )


def convert_video(video, input_path, output_path, output_absolute_path):
    duration = get_video_duration(input_path)
    if duration > settings.MAXIMUM_VIDEO_DURATION:
        raise VideoTooLong
    video_width, video_height = get_video_resolution(input_path)
    resolution = min(supported_resolutions, key=lambda res: abs(res[1] - video_height))
    logger.info(f"Converting to {resolution[0]}x{resolution[1]}")
    tot_n_frames = get_total_n_frames(input_path)
    command = [
        FFMPEG_PATH,
        "-y",
        "-loglevel",
        "error",
        "-i",
        input_path,
        "-vf",
        ", ".join(
            [
                "scale=w=trunc(ih*dar/2)*2:h=trunc(ih/2)*2",
                "setsar=1/1",
                f"scale=w={resolution[0]}:h={resolution[1]}:force_original_aspect_ratio=1",
                f"pad=w={resolution[0]}:h={resolution[1]}:x=(ow-iw)/2:y=(oh-ih)/2:color=#000000",
            ]
        ),
        "-fpsmax",
        "24" if resolution[1] > 144 else "15",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium" if resolution[1] > 240 else "veryfast",
        "-crf",
        "35",
        "-maxrate",
        "400k",
        "-bufsize",
        "800k",
        "-c:a",
        "aac",
        "-b:a",
        "72k" if resolution[1] > 144 else "48k",
        "-movflags",
        "+faststart",
        "-map_metadata",
        "-1",
        "-map_chapters",
        "-1",
        "-progress",
        "pipe:1",
        output_path,
    ]

    logger.info(" ".join(command))
    with sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE) as process:
        q = [0]
        progress_reader_thread = Thread(target=progress_reader, args=(process, q))
        progress_reader_thread.start()

        while True:
            if process.poll() is not None:
                break

            time.sleep(1)

            n_frame = q[0]
            if tot_n_frames > 0:
                progress_percent = (n_frame / tot_n_frames) * 100
                progress_percent = int(progress_percent)
                update_video_progress(video.id, progress_percent)
                logger.info(f"{video.title} {progress_percent}%")

        process.stdout.close()
        progress_reader_thread.join()
        process.wait()
    generate_thumbnails(
        video.id, duration, output_path, output_absolute_path, resolution
    )
