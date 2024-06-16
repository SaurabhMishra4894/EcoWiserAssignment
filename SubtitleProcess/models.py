from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='public/video_files',
                                  validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'mov'])])
    subtitle_file = models.URLField(max_length=200,blank=True)
    s3_file = models.URLField(max_length=200,blank=True)
    is_subtitle_processed = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
