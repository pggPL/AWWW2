import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def display_directories_and_files(directory, level):
    result = ''
    indent = 10 * (level) * 4
    
    if not directory.is_available:
        return ''
    
    result += f'<div class="directory" id="dir{directory.id}" onclick="showDir({directory.id})" style="padding-left: {indent}px">{directory.name}</div>'
    
    indent += 40
    
    for file in directory.file_set.filter(is_available=True):
        result += f'<div class="file" id="file{file.id}" onclick="showFile({file.id})" style="padding-left: {indent}px">{file.name}</div>'
    
    for subdirectory in directory.directory_set.all():
        result += display_directories_and_files(subdirectory, level + 1)
    
    return mark_safe(result)


@register.filter(name='split_in_lines')
def split_in_lines(text):
    if text.startswith('Error'):
        text = text[6:]
        split = text.split('\n')[:-1]
        error_lines = []
        for line in split:
            if line.startswith('./app_main/c_files/'):
                error_lines.append(int(line.split(':')[1]))
            else:
                error_lines.append(None)
        return "ERROR", split, error_lines
    lines = text.split('\n')
    sections = []
    current_section = [""]
    
    section_started = False
    code_started = False
    for line in lines:
        if code_started:
            current_section.append(line)
            continue
        if line.startswith(";-----------------------------------------"):
            if section_started:
                sections.append(current_section)
                section_started = False
            else:
                current_section = [""]
                section_started = True
                continue
        else:
            if section_started:
                current_section[0] = current_section[0] + line[2:] + '\n'
                if line.startswith("; code"):
                    code_started = True
            else:
                current_section.append(line)
    sections.append(current_section)
    return sections
