from django import forms
from django.forms import ModelForm

from SubtitleProcess.models import Video


class VideoForm(ModelForm):
    class Meta:
        model = Video
        fields = ["title", "video_file"]


class SubtitleForm(forms.Form):
    search_text = forms.CharField(label='Search', required=True)
