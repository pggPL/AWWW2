from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:file_id>', views.display_file, name='display_file'),
    path('dir/<int:dir_id>', views.display_dir, name='display_directory'),
    path('add_directory/', views.add_directory, name='add_directory'),
    path('add_file/', views.add_file, name='add_file'),
    path('delete_item/', views.delete_item, name='delete_item'),
    path('recompile/', views.recompile, name='recompile'),
    path('download_asm/<int:file_id>/', views.download_asm, name='download_asm'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
