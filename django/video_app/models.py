# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import uuid

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse

from django_project import settings
from video_app.domain.csv_file import CsvFileManager
from video_app.utils import clear_dir


class Template(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=64)
    background_video = models.CharField(max_length=100, default='')

    def get_data_filename(self):
        return os.path.join(settings.VIDEOS_TEMPLATES, '%s.json' % self.name)

    def get_video_filename(self):
        return os.path.join(settings.VIDEOS_TEMPLATES, '%s.mp4' % (
            self.background_video if (self.background_video and len(self.background_video)) else self.name))

    def get_data(self):
        with open(self.get_data_filename()) as f:
            return json.load(f)["screens"]["0"]

    def __unicode__(self):
        return "%s (%s)" % (
            self.name,
            self.background_video if (self.background_video and len(self.background_video)) else self.name)


class CsvFile(models.Model):
    name = models.UUIDField('name', default=uuid.uuid4)
    datetime = models.DateTimeField('date time', auto_now_add=True)
    file = models.FileField('file', upload_to='csv_files')
    template = models.ForeignKey(Template, related_name='csv_files', blank=False)

    def load_data(self):
        records = CsvFileManager(os.path.join(settings.MEDIA_ROOT, self.file.name),
                                 {'name': 3, 'company': 4},
                                 has_header=True).get_records(['name', 'company'])
        for line, record in records.items():
            error = record.get('error', None)
            row = DataRow.objects.create(csv_file=self, line=line, error=(error if error else ''))
            if not error:
                for name, value in record.items():
                    TextDataField.objects.create(data_row=row, name=name, value=value)
                Video.objects.create(data_row=row)

    class Meta:
        ordering = ('-datetime',)

    def sample(self):
        if Video.objects.filter(data_row__csv_file=self, status=3).count():
            return Video.objects.filter(data_row__csv_file=self, status=3).first()
        return None


@receiver(pre_save, sender=CsvFile)
def csv_file_pre_save(sender, instance, **kwargs):
    if not instance.template:
        instance.template = Template.objects.last()


@receiver(post_save, sender=CsvFile)
def csv_file_post_save(sender, instance, created, **kwargs):
    path = os.path.join(settings.MP4_DIR, "%s" % instance.name)
    clear_dir(path)
    if created:
        instance.load_data()


class DataRow(models.Model):
    csv_file = models.ForeignKey(CsvFile, verbose_name='csv file', related_name='rows')
    line = models.PositiveSmallIntegerField('line number')
    error = models.CharField('error', max_length=128, default='')

    class Meta:
        ordering = ('csv_file', 'line')


class TextDataField(models.Model):
    data_row = models.ForeignKey(DataRow, verbose_name='data', related_name='texts')
    name = models.CharField('name', max_length=128, default='')
    value = models.CharField('value', max_length=256, default='')


@receiver(post_save, sender=TextDataField)
def text_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.name == 'name':
            instance.value = '%s|you are|invited' % instance.value
            instance.save()
        if instance.name == 'company':
            instance.value = 'and make|%s|really stand out' % instance.value
            instance.save()


class Video(models.Model):
    STATUS_CHOICES = (
        ('0', 'Created'),  # Video record is created/updated in DB
        ('1', 'In queue'),  # Video part is queued to make an mp4 file
        ('2', 'Active'),  # ffmpeg started the work on creating the file
        ('3', 'Ready'),  # Video part file is ready
        ('4', 'Error'),  # There is an error with generating the video
    )
    file_name = models.UUIDField('file name', default=uuid.uuid4)
    datetime = models.DateTimeField('date time', auto_now_add=True)
    last_time = models.DateTimeField('last time', auto_now=True)
    data_row = models.ForeignKey(DataRow, verbose_name='data row', related_name='videos')
    status = models.CharField('status', max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    video_file = models.FileField('video file')
    thumbnail_file = models.ImageField('thumbnail file')

    def get_absolute_url(self):
        return reverse('detail', args=[str(self.id)])

    class Meta:
        ordering = ('-last_time', '-datetime')


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        from .tasks import make_video
        make_video.delay(instance.id)
