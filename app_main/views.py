import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Directory, File, FileSection, SectionType, SectionStatus
from .forms import DirectoryForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json

from .templatetags.custom_filters import display_directories_and_files, split_in_lines


def index(request):
    directories = Directory.objects.filter(parent_directory=None)
    files = File.objects.filter(directory=None, is_available=True)
    return render(request, 'index.html', {'directories': directories, 'files': files})


def display_file(request, file_id):
    file = File.objects.get(id=file_id)
    sections = FileSection.objects.filter(file=file)
    context = {
        'status': "ok",
        'sections': list(sections),
        'code_in_c': file.get_code_in_c(),
        'code_in_asm': file.assembly_code,
        'file_id': file_id,
        'dir_id': file.directory.id if file.directory else None,
        'right_panel_code': split_in_lines(file.assembly_code)
    }
    return JsonResponse(context)


def display_dir(request, dir_id):
    directories = Directory.objects.filter(parent_directory=None)
    files = File.objects.filter(directory=None, is_available=True)
    context = {
        'directories': directories,
        'dir_id': dir_id,
        'files': files
    }
    return render(request, 'index.html', context)


def get_dir_list(request):
    dir_list = ""
    for f in File.objects.filter(directory=None, is_available=True):
        dir_list += f'<div class="file" id="file{f.id}" onclick="showFile({f.id})" style="padding-left: 0px">{f.name}</div>'
    for d in Directory.objects.filter(parent_directory=None, is_available=True):
        dir_list += display_directories_and_files(d, 0)
    return dir_list


def add_directory(request):
    if request.method == 'POST':
        # initiral
        form = DirectoryForm(request.POST)
        if form.is_valid():
            dir = form.save(commit=False)
            dir.save()
            context = {
                "dir_list": get_dir_list(request),
            }
            return JsonResponse(context)
    return JsonResponse({'error': 'error'})


def add_file(request):
    if request.method == 'POST':
        # assert that there is file sent by "file_upload" name
        uploaded_file = request.FILES['file_upload']
        if uploaded_file.name.endswith('.c'):
            # create .c file with uploaded content
            file_path = os.path.join('./app_main/c_files', uploaded_file.name)
            with open(file_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        else:
            return JsonResponse({'status': 'error', 'error': 'Plik musi mieć rozszerzenie .c!'})

        if 'directory_id' not in request.POST or request.POST['directory_id'] == '':
            File(name=uploaded_file.name, path=file_path).save()
        else:
            dir_id = request.POST['directory_id']
            dir = Directory.objects.get(id=dir_id)
            File(name=uploaded_file.name, path=file_path, directory=dir).save()
        return JsonResponse({'status': 'ok', 'dir_list': get_dir_list(request)})


def recompile(request):
    if request.method == 'POST':
        file_id = request.POST['file_id']
        processor = request.POST['processor']
        dependent = request.POST['dependent']
        optimization = request.POST['optimization']
        opt1 = 'opt1' in optimization
        opt2 = 'opt2' in optimization
        opt3 = 'opt3' in optimization

        file = File.objects.get(id=file_id)
        file.compile(processor=processor, dependent=dependent, opt1=opt1, opt2=opt2, opt3=opt3)

        return display_file(request, file_id)
    else:
        return JsonResponse({'status': 'error', 'error': 'Błąd kompilacji'})
    

def delete_item(request):
    if request.method == 'POST':
        if 'dir_id' not in request.POST:
            redirect('index')
        dir_id = request.POST['dir_id']
        if request.POST['file_id'] != '':
            file_id = request.POST['file_id']
            file = File.objects.get(id=file_id)
            file.is_available = False
            file.save()
        else:
            dir = Directory.objects.get(id=dir_id)
            dir.is_available = False
            dir.save()
        return JsonResponse({'status': 'success'})


def download_asm(request, file_id):
    file = File.objects.get(id=file_id)
    response = HttpResponse(file.assembly_code, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{file.name[:-2]}.asm"'
    return response


def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failure'}, status=401)
    else:
        return render(request, 'login.html')
