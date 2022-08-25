from frog_api.exceptions import (
    NonexistentCategoryException,
    NonexistentProjectException,
    NonexistentVersionException,
)
from frog_api.models import Category, Project, Version


def get_project(slug: str) -> Project:
    ret = Project.objects.filter(slug=slug).first()
    if not ret:
        raise NonexistentProjectException(slug)
    return ret


def get_version(slug: str, project: Project) -> Version:
    ret = Version.objects.filter(slug=slug, project=project).first()
    if not ret:
        raise NonexistentVersionException(project.slug, slug)
    return ret


def get_category(slug: str, version: Version) -> Category:
    ret = Category.objects.filter(slug=slug, version=version).first()
    if not ret:
        raise NonexistentCategoryException(version.project.slug, version.slug, slug)
    return ret
