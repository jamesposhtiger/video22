from django.conf.urls import url
from video_app.api_rest.views import FileListView

urlpatterns = [
    url(r'^files/$', FileListView.as_view()),
]
