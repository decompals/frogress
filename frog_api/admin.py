from django.contrib import admin

from frog_api.models import Category, Entry, Measure, Project, Version

admin.site.register(Project)
admin.site.register(Version)
admin.site.register(Category)
admin.site.register(Entry)
admin.site.register(Measure)
