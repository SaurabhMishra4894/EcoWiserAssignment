import os
import subprocess
import simplejson as json
from celery import shared_task
from django.contrib import messages

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView

from SubtitleProcess.forms import VideoForm, SubtitleForm
from SubtitleProcess.models import Video
from VideoProcessor import settings
from helper.dynamodb_helper import store_subtitle, search_subtitles
from helper.s3_helper import upload_file_to_s3


# Create your views here.
@shared_task
def process_subtitle(subtitle_file_path, video_id):
    with open(subtitle_file_path, 'r') as subtitle_file:
        subtitle_text = subtitle_file.read().strip().split('\n\n')

        for line in subtitle_text:
            order = line.splitlines()[0]
            time = line.splitlines()[1]
            subtitles = line.splitlines()[2:]
            subtitle_string = ''
            for subtitle in subtitles:
                subtitle_string += ' ' + subtitle.strip()
            store_subtitle(video_id=video_id, timestamp=time, subtitle=subtitle_string)
        video_obj = Video.objects.get(id=video_id)
        video_obj.is_subtitle_processed = True
        video_obj.save()


def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = form.cleaned_data['video_file']

            fs = FileSystemStorage()
            filename = fs.save(video_file.name, video_file)
            file_path = fs.path(filename)

            upload_file_to_s3.delay(file_path)
            s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
            # Call ccextractor to extract subtitles
            subtitle_file_path = os.path.splitext(file_path)[0] + '.srt'
            subprocess.run(['ccextractor', file_path, '-o', subtitle_file_path])

            form.instance.video_file = file_path
            form.instance.subtitle_file = subtitle_file_path
            form.instance.s3_file = s3_url
            new_video = form.save()
            # Read generated subtitles and store in DynamoDB
            process_subtitle.delay(subtitle_file_path, new_video.id)
            messages.success(request,
                             "Video uploaded successfully and is being processed. Subtitles and video URL will be "
                             "available in few minutes")
            return redirect(reverse('upload_video'))

    else:
        form = VideoForm()
        videos = Video.objects.all()
        context = {
            'videos': videos,
            'form': form
        }
        return render(request, 'videos/upload_video.html', context)


def search_video(request, id):
    if request.method == 'POST':
        form = SubtitleForm(request.POST)
        if form.is_valid():
            search_text = form.cleaned_data['search_text']
            search_subtitle = search_subtitles(id, search_text)
            return HttpResponse(json.dumps(search_subtitle), content_type="application/json")

    else:
        form = SubtitleForm()
        video = get_object_or_404(Video, id=id)
        context = {
            'form': form,
            'video': video
        }
        return render(request, 'videos/searchVideo.html', context)
