from django.contrib import admin
import nested_admin

from frog_api.models import Category, Entry, Measure, Project, Version


class CategoryInline(nested_admin.NestedStackedInline):
    model = Category
    extra = 0


class VersionInline(nested_admin.NestedStackedInline):
    model = Version
    inlines = [CategoryInline]
    extra = 0


class ProjectAdmin(nested_admin.NestedModelAdmin):
    model = Project
    inlines = [VersionInline]
    extra = 0


admin.site.register(Project, ProjectAdmin)
admin.site.register(Entry)
admin.site.register(Measure)
