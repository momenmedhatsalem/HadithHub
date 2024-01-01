from django.urls import path
from . import views

urlpatterns = [
    
    path('update_progress/<int:hadith_id>/<str:source>/', views.update_progress, name='update_progress'),
    path('hadith/<str:source>', views.hadith, name='hadith'),
    path('', views.index, name='index'),
    path('single_hadith/<int:hadith_id>/', views.single_hadith, name='singlehadith'),
    path('hadith_image/<int:hadith_id>', views.hadith_image, name='hadith_image'),
    path('create_account/', views.my_create_account_view, name='create_account'),
    path('login/', views.my_login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.my_logout_view, name='logout'),

]
