from django.conf.urls import url
from django.contrib import admin

from video_app import views

urlpatterns = [
    url(r'^$', views.CsvUploadView.as_view(), name='home'),
    url(r'^status/$', views.CsvUploadStatusView.as_view(), name='status'),
    url(r'^download/(?P<pk>\d+)/$', views.VideoDownloadView.as_view(), name='download'),
    url(r'^csv/(?P<pk>\d+)/$', views.CsvDownloadView.as_view(), name='csv'),
    url(r'^detail/(?P<pk>\d+)/$', views.VideoDetailView.as_view(), name='detail'),

]
