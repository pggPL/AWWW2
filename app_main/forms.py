from django import forms
from .models import Directory, File, FileSection, SectionType, SectionStatus


class DirectoryForm(forms.ModelForm):
    add_directory_name = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = Directory
        fields = ['parent_directory', 'add_directory_name']
    
    def save(self, commit=True):
        directory = Directory(
            parent_directory=self.cleaned_data['parent_directory'],
            name=self.cleaned_data['add_directory_name']
        )
        if commit:
            directory.save()
        return directory


