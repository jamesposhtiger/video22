from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from video_app.api_rest.serializers import CsvFileSerializer
from video_app.models import CsvFile


class FileListView(ListAPIView):
    queryset = CsvFile.objects.all()
    serializer_class = CsvFileSerializer
    permission_classes = (IsAuthenticated,)

