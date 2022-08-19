from django.db import models


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)


class Version(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255)


class Entry(models.Model):
    id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    git_hash = models.CharField(max_length=40)
    # Functions
    total_functions = models.IntegerField()
    decompiled_functions = models.IntegerField()
    matching_functions = models.IntegerField()
    # Bytes
    total_bytes = models.IntegerField()
    decompiled_bytes = models.IntegerField()
    matching_bytes = models.IntegerField()
    # Other
    other_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
