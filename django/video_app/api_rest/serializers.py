from django.template.defaultfilters import date
from django.urls import reverse
from rest_framework import serializers

from video_app.models import Video, CsvFile


class VideoUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'video_file','thumbnail_file')


class CsvFileSerializer(serializers.ModelSerializer):
    datetime = serializers.SerializerMethodField()
    rows = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    ready = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    generate_url = serializers.SerializerMethodField()
    sample = VideoUrlSerializer()

    class Meta:
        model = CsvFile
        fields = ('id', 'datetime', 'file', 'rows', 'created', 'active', 'ready', 'error', 'generate_url', 'sample')

    def get_datetime(self, obj):
        return date(obj.datetime, 'SHORT_DATETIME_FORMAT')

    def get_rows(self, obj):
        return obj.rows.count()

    def get_created(self, obj):
        return Video.objects.filter(data_row__csv_file=obj, status=0).count()

    def get_active(self, obj):
        return Video.objects.filter(data_row__csv_file=obj, status=2).count()

    def get_ready(self, obj):
        return Video.objects.filter(data_row__csv_file=obj, status=3).count()

    def get_error(self, obj):
        return Video.objects.filter(data_row__csv_file=obj, status=4).count()

    def get_generate_url(self, obj):
        return reverse('csv', args=[obj.id])
