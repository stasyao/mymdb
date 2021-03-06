from django.contrib import admin

from movies import models

admin.site.register(models.Movie)
admin.site.register(models.Role)
admin.site.register(models.Person)
admin.site.register(models.Vote)
