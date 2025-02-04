from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kitwek.urls')),  # Your app's URL configuration
]

# Add Django Debug Toolbar URLs conditionally (only in DEBUG mode)
if settings.DEBUG:  # Only show the toolbar in debug mode
    
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
