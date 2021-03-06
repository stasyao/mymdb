from django.contrib import admin
from django.urls import include, path

import movies.urls
import users.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(users.urls, namespace='users')),
    path('', include(movies.urls, namespace='movies')),
]
