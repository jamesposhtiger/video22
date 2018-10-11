from django import forms

from video_app.models import CsvFile


class CsvUploadForm(forms.ModelForm):
    class Meta:
        fields = ('file', 'template')
        model = CsvFile
