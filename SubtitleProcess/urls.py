from django.urls import path, include

from SubtitleProcess import views

urlpatterns = [
    # path('', views.video_upload_view, name='UploadVideo'),
    path('<int:id>/', views.search_video, name='searchVideo'),
    path('', views.upload_video, name='upload_video'),
]