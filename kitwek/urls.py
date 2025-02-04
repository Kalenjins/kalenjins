from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),    
    path('profile/', views.profile_view, name='profile'),  
    path('profile/<int:id>/', views.profile_view, name='profile_user_by_id'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),           
    path('post/<int:post_id>/', views.post_detail, name='post_detail'), 
    path('ajax/sorted-posts/', views.get_sorted_posts, name='get_sorted_posts'),  
    path('like/<int:post_id>/', views.like_post, name='like_post'), 
    path('like/', views.like_post, name='like_post'),
    path('like_post/', views.like_post, name='like_post'),
    path('clan/', views.clans, name='clans_list'),    
    path('clan/<int:pk>/', views.clan_detail, name='clan_detail'),  
    path('origin/', views.origin, name='origin'),  
    path('quote/', views.quote, name='quote'), 
    path('quotes/', views.quote, name='quotes'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('like_comment/', views.like_comment, name='like_comment'),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)