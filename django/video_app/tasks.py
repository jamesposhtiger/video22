# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess
import uuid

from django_project import settings
from django_project.celery import app
from video_app.domain.ffmpeg_maker import EffectTemplate, TransitionTemplate
from video_app.domain.imagemagick_maker import TextTemplate, ImageMagickTextMaker
from video_app.models import Video


def temp_png_path(path):
    return os.path.join(path, '%s.png' % uuid.uuid4())


def list_upper(t, upper):
    return [e.upper() for e in t] if upper else t


@app.task
def make_video(video_id):
    video = Video.objects.get(pk=video_id)
    template_data = video.data_row.csv_file.template.get_data()
    template_video = video.data_row.csv_file.template.get_video_filename()
    thumb_frame = 40

    upper = template_data.get('upper', False)

    path = os.path.join(settings.MP4_DIR, "%s" % video.data_row.csv_file.name)
    output_file = os.path.join(path, '%s.mp4' % video.file_name)
    thumbnail_file = "%s.jpg" % output_file[:-4]

    # Change status
    # IMPORTANT! Do not use video_part.save() because it will call a signal which will set status to 0
    # See: signals.video_part_pre_save
    Video.objects.filter(pk=video_id).update(status='2')

    # Texts
    texts = []
    for name, text in template_data['texts'].items():
        if 'effects' in text['transition']:
            effects = [EffectTemplate(**e) for e in text['transition']['effects']]
            text['transition']['effects'] = effects
        # lines = []
        lines = video.data_row.texts.get(name=name).value.split('|')

        texts.append({
            'template': TextTemplate(**text['template']),
            'transition': TransitionTemplate(**text['transition']),
            'lines': lines,
        })
        if text.get('guest_field', False):
            thumb_frame = text.get('frame', thumb_frame)

    text_files = [
        ImageMagickTextMaker(temp_png_path(path), t['template'], list_upper(t['lines'], upper)).make()
        for t in texts
    ]

    effects = [t['transition'].get_script() for t in texts]

    arguments = ['-i', template_video]
    effects = ",".join(effects)
    arg_files = []
    for f in text_files:
        arg_files += ['-i', f]
    # arguments += arg_files + ['-filter_complex', effects, "-b:v", "3M", "-c:a", "aac", "-strict", "-2"]
    # arguments += arg_files + ['-filter_complex', effects, "-b:v", "3M", "-c:a", "aac", "-strict", "-2"]
    arguments += arg_files + ['-filter_complex', effects, "-b:v", "3M", '-c:v', 'h264', "-c:a", "aac", "-strict", "-2"]

    # If using in a debug mode use mpeg4 codec because it's faster
    # if settings.DEBUG:
    #     arguments += ['-c:v', 'mpeg4']

    arguments += [output_file]
    code = subprocess.call([settings.FFMPEG_CMD] + arguments)
    print ([settings.FFMPEG_CMD] + arguments)
    thumb_arguments = ['-i', output_file, "-f", "image2", "-frames:v", str(thumb_frame), "-update", "1", thumbnail_file]
    subprocess.call([settings.FFMPEG_CMD] + thumb_arguments)

    if code:
        Video.objects.filter(pk=video.pk).update(status='4')  # Error
        return False

    Video.objects.filter(pk=video.pk).update(status='3',
                                             video_file=output_file[len(settings.MEDIA_ROOT):],
                                             thumbnail_file=thumbnail_file[len(settings.MEDIA_ROOT):])
    os.chmod(output_file, 0o777)
    return output_file
