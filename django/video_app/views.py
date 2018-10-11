# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from django_project import settings
from video_app.domain.csv_file import CsvFileManager
from video_app.forms import CsvUploadForm
from video_app.models import Video, CsvFile


class CsvUploadView(View):
    def get(self, request):
        form = CsvUploadForm()
        c = {'form': form, }
        return render(request, 'csv_upload.html', c)

    def post(self, request):
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        c = {'form': form}
        return render(request, 'csv_upload.html', c)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CsvUploadView, self).dispatch(*args, **kwargs)


class CsvUploadStatusView(View):
    def get(self, request):
        form = CsvUploadForm()
        c = {'form': form, }
        return render(request, 'csv_upload_status.html', c)

    def post(self, request):
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('status')
        c = {'form': form}
        return render(request, 'csv_upload_status.html', c)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CsvUploadStatusView, self).dispatch(*args, **kwargs)


class VideoDownloadView(View):
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        data = open(video.video_file.file, b'rb+')
        filename = '%s.mp4' % video.file_name
        response = HttpResponse(data, content_type='application/mp4')
        response['Content-Disposition'] = 'attachment; filename=%s;' % filename
        response['Cache-Control'] = 'no-cache'
        return response

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VideoDownloadView, self).dispatch(*args, **kwargs)


class VideoDetailView(View):
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        return render(request, 'video_detail.html', {'video': video})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VideoDetailView, self).dispatch(*args, **kwargs)


class CsvDownloadView(View):
    def get(self, request, pk):
        csv_file = get_object_or_404(CsvFile, pk=pk)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % csv_file.file.name

        writer = csv.writer(response)
        columns = OrderedDict(
            [('date', 0), ('email', 1), ('description', 2), ('name', 3), ('company', 4), ('video URL', 5),
             ('image URL', 6)])
        writer.writerow([name for name in columns])
        records = CsvFileManager(
            os.path.join(settings.MEDIA_ROOT, csv_file.file.name), columns,
            has_header=True).get_records(['date', 'email', 'description', 'name', 'company'])
        for row in csv_file.rows.all():
            if row.line not in records:
                continue
            data = records[row.line]
            if 'error' in data:
                continue
            video = row.videos.last()
            data['video URL'] = ''
            data['image URL'] = ''
            if video and video.video_file:
                data['video URL'] = request.build_absolute_uri(video.video_file.url)
            if video and video.thumbnail_file:
                data['image URL'] = request.build_absolute_uri(video.thumbnail_file.url)
            line = [data[col] for col in columns.keys()]
            writer.writerow(line)

        return response

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CsvDownloadView, self).dispatch(*args, **kwargs)
