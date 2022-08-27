from datetime import datetime
from django.db import models
from django.utils.crypto import get_random_string

AUTH_KEY_LEN = 10


def gen_auth_key() -> str:
    ret = get_random_string(length=AUTH_KEY_LEN)

    if Project.objects.filter(auth_key=ret).exists():
        return gen_auth_key()

    return ret


# Example: OOT
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=AUTH_KEY_LEN, default=gen_auth_key)
    repository = models.URLField(blank=True)
    discord = models.URLField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.slug


# Example: US 1.0
class Version(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="versions"
    )
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.project} {self.slug}"


# Example: Actors
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return f"{self.version} {self.slug}"


# A snapshot in time of progress, tied to a Category
class Entry(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    git_hash = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = "Entries"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        time_string = datetime.utcfromtimestamp(self.timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{self.category} {time_string}"


# A measure (total bytes, bytes matched, functions matched, bytes decompiled, etc) tied to an Entry
class Measure(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="measures")
    type = models.CharField(max_length=255)
    value = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.entry} {self.type}: {self.value}"
