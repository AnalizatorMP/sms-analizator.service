from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('auth/', include('users_app.api.auth.urls')),
]
