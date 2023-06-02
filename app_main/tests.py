import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import DirectoryForm
from .models import Directory, File, SectionType, SectionStatus, FileSection

from .templatetags.custom_filters import display_directories_and_files, split_in_lines

class TestCustomFilters(TestCase):
    
        def test_display_directories_and_files(self):
            user = User.objects.create(username="testuser")
            directory = Directory.objects.create(name="Test Directory", owner=user)
            file = File.objects.create(id=1, name="test_file.c", owner=user, directory=directory, path="test_path")
            self.assertEqual(
                display_directories_and_files(directory, 0),
                '<div class="directory" id="dir1" onclick="showDir(1)" style="padding-left: 0px">Test Directory</div><div class="file" id="file1" onclick="showFile(1)" style="padding-left: 40px">test_file.c</div>'
                )
    
        def test_split_in_lines(self):
            self.assertEqual(split_in_lines("int main() {return 0;}"), [['', 'int main() {return 0;}']])
            
        def test_error_in_lines(self):
            self.assertEqual(split_in_lines("Error: ./app_main/c_files/test.c:2: error 20: Undefined identifier 'r2'"),
                             ('ERROR', [], []))

        def test_split_in_lines_2(self):
            split_in_lines(asm_prog)
            
            
class DirectoryModelTests(TestCase):

    def test_directory_creation(self):
        user = User.objects.create(username="testuser")
        directory = Directory.objects.create(name="Test Directory", owner=user)
        self.assertEqual(directory.name, "Test Directory")
        self.assertEqual(directory.owner, user)


class FileModelTests(TestCase):

    def test_file_creation(self):
        user = User.objects.create(username="testuser")
        directory = Directory.objects.create(name="Test Directory", owner=user)
        file = File.objects.create(id=1, name="test_file.c", owner=user, directory=directory, path="test_tgdfdpath")
        self.assertEqual(file.name, "test_file.c")
        self.assertEqual(file.owner, user)
        self.assertEqual(file.directory, directory)

    def test_compile_code(self):
        code = """ int main() {
            int a = 5;
            int b = 6;
            int c = a + b;
            return c;
            }"""
        
        with open("test_file.c", "w") as f:
            f.write(code)
        
        user = User.objects.create(username="testuser")
        directory = Directory.objects.create(name="Test Directory", owner=user)
        file = File.objects.create(id=1, name="test_file.c", owner=user, directory=directory, path=".")
        file.compile_code()
        
        os.remove("test_file.c")
        

    def test_get_code_in_c(self):
        code = """ int main() {
                    int a = 5;
                    int b = 6;
                    int c = a + b;
                    return c;
                    }"""
    
        with open("test_file.c", "w") as f:
            f.write(code)
        
        user = User.objects.create(username="testuser")
        directory = Directory.objects.create(name="Test Directory", owner=user)
        file = File.objects.create(id=1, name="test_file.c", owner=user, directory=directory, path="test_file.c")
        file.get_code_in_c()
        
        os.remove("test_file.c")


class SectionTypeModelTests(TestCase):

    def test_section_type_creation(self):
        section_type = SectionType.objects.create(name="Test Section Type")
        self.assertEqual(section_type.name, "Test Section Type")


class SectionStatusModelTests(TestCase):

    def test_section_status_creation(self):
        section_status = SectionStatus.objects.create(name="Test Section Status")
        self.assertEqual(section_status.name, "Test Section Status")


class FileSectionModelTests(TestCase):

    def test_file_section_creation(self):
        user = User.objects.create(username="testuser")
        directory = Directory.objects.create(name="Test Directory", owner=user)
        file = File.objects.create(id=5, name="test2_file.c", owner=user, directory=directory, path="test_path")
        section_type = SectionType.objects.create(name="Test Section Type")
        section_status = SectionStatus.objects.create(name="Test Section Status")

        file_section = FileSection.objects.create(
            name="Test File Section",
            start_line=1,
            end_line=10,
            section_type=section_type,
            status=section_status,
            content="Test content",
            file=file
        )

        self.assertEqual(file_section.name, "Test File Section")
        self.assertEqual(file_section.file, file)


class ViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_index_view(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_display_file_view(self):
        code = """ int main() {
                    int a = 5;
                    int b = 6;
                    int c = a + b;
                    return c;
                    }"""
        # create file
        with open("test_file.c", "w") as f:
            f.write(code)
        
        file = File.objects.create(id=1, name="test_file.c", owner=self.user, path="./test_file.c", assembly_code="")
        url = reverse('display_file', args=[file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        os.remove("test_file.c")

    def test_display_dir_view(self):
        directory = Directory.objects.create(name="test_directory", owner=self.user)
        url = reverse('display_directory', args=[directory.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_directory_view(self):
        url = reverse('add_directory')
        data = {'name': 'Test Directory'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_add_file_view(self):
        url = reverse('add_file')
        # Create a temporary file to simulate the upload
        file_content = b'Test content'
        uploaded_file = SimpleUploadedFile('test_file.c', file_content)
        data = {'file_upload': uploaded_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)

    def test_recompile_view(self):
        file = File.objects.create(id=1, name="test_file.c", owner=self.user)
        url = reverse('recompile')
        data = {
            'file_id': file.id,
            'processor': 'processor',
            'dependent': 'dependent',
            'optimization': ['opt1', 'opt2'],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_delete_item_view(self):
        directory = Directory.objects.create(name="test_directory", owner=self.user)
        url = reverse('delete_item')
        data = {'dir_id': directory.id, 'file_id': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})

    def test_download_asm_view(self):
        file = File.objects.create(id=1, name="test_file.c", owner=self.user)
        url = reverse('download_asm', args=[file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        

class FormTests(TestCase):

    def test_directory_form(self):
        parent_directory = Directory.objects.create(name="Parent Directory")
        form_data = {
            'parent_directory': parent_directory.id,
            'add_directory_name': 'Test Directory'
        }
        form = DirectoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        directory = form.save()
        self.assertEqual(directory.name, 'Test Directory')
        self.assertEqual(directory.parent_directory, parent_directory)