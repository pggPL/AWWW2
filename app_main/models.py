import os
import subprocess
import uuid

from django.db import models

from django.contrib.auth.models import User


class Directory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    availability_date = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    parent_directory = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Directories'


class File(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    availability_date = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, blank=True, null=True)
    path = models.CharField(max_length=255)
    assembly_code = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Files'

    def compile_code(self, processor=None, dependent=None, opt1=None, opt2=None, opt3=None):
        # print args
        # compile C code to assembly using sdcc command
        if self.path and self.name.endswith('.c'):
            try:
                # generate unique filename for assembly code
                filename = f'{uuid.uuid4().hex}.asm'
                cmd = ['sdcc', '-S', '-o', filename]
            
                if processor:
                    cmd.append(f'-{processor}')
            
                if dependent:
                    cmd.append(f'--{dependent}')
            
                if opt1:
                    cmd.append(f'--{opt1}')
            
                if opt2:
                    cmd.append(f'--{opt2}')
            
                if opt3:
                    cmd.append(f'--{opt3}')
            
                cmd.append(self.path)
                
            
                result = subprocess.run(cmd, capture_output=True)
            
                if result.returncode != 0:
                    raise Exception(result.stderr.decode())
                else:
                    # open file and read its content
                    with open(filename, 'r') as f:
                        self.assembly_code = f.read()
                    # remove assembly file
                    os.remove(filename)
            except Exception as e:
                self.assembly_code = f'Error: {e}'
        else:
            self.assembly_code = 'No assembly code available for this file.'

    def remove_old_sections(self):
        FileSection.objects.filter(file=self).delete()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.assembly_code and not self.id:
            self.save()
            self.compile_code()

    def compile(self, processor=None, dependent=None, opt1=None, opt2=None, opt3=None):
        self.compile_code(processor=processor, dependent=dependent, opt1=opt1, opt2=opt2, opt3=opt3)
        self.remove_old_sections()
        self.save()
    
    def get_code_in_c(self):
        # get code from file for path
        if self.path and self.name.endswith('.c'):
            with open(self.path, 'r') as f:
                return f.read()
        else:
            return 'No C code available for this file.'


class SectionType(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = 'Section Types'


class SectionStatus(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = 'Section Statuses'


class FileSection(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_line = models.IntegerField()
    start_char = models.IntegerField(blank=True, null=True)
    end_line = models.IntegerField()
    end_char = models.IntegerField(blank=True, null=True)
    section_type = models.ForeignKey(SectionType, on_delete=models.CASCADE)
    status = models.ForeignKey(SectionStatus, on_delete=models.CASCADE)
    status_data = models.TextField(blank=True, null=True)
    content = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = 'File Sections'
