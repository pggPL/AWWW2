from django.contrib import admin
from .models import Directory, File, FileSection, SectionType, SectionStatus

# Register all models.

admin.site.register(Directory)
admin.site.register(File)
admin.site.register(FileSection)
admin.site.register(SectionType)
admin.site.register(SectionStatus)

