# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from video_app.models import Template, CsvFile, DataRow, TextDataField, Video


@admin.register(Template, CsvFile, DataRow, TextDataField)
class GenModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Video)
class VideoModelAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'row_line', 'status', 'video_url']

    def row_line(self, obj):
        return obj.data_row.line

    row_line.short_description = 'Row Line'

    def video_url(self, obj):
        return obj.video_file.url if obj.video_file else ''

    video_url.short_description = 'Video Url'
