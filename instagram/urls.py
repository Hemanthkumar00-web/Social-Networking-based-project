from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('feed.urls')),
    path('', include('posts.urls')),
    path('', include('messasing.urls')),
    path('', include('profile_section.urls')),
    path('', include('authentication.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
