# Generated by Django 4.1.3 on 2022-11-22 17:15

from typing import Any
from django.db import migrations, models
import django.db.models.deletion
import frog_api.models


class Migration(migrations.Migration):

    replaces = [
        ("frog_api", "0001_initial"),
        ("frog_api", "0002_remove_entry_version_category_entry_category"),
        (
            "frog_api",
            "0003_rename_decompiled_functions_entry_decompiled_chunks_and_more",
        ),
        ("frog_api", "0004_alter_category_options_alter_entry_options_and_more"),
        ("frog_api", "0005_remove_entry_decompiled_bytes_and_more"),
        ("frog_api", "0006_alter_project_auth_key"),
        ("frog_api", "0007_alter_entry_timestamp"),
        ("frog_api", "0008_project_discord_project_repository_project_website"),
        ("frog_api", "0009_alter_project_discord_alter_project_repository_and_more"),
    ]

    initial = True

    dependencies: Any = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "auth_key",
                    models.CharField(
                        default=frog_api.models.gen_auth_key, max_length=10
                    ),
                ),
                ("discord", models.URLField(blank=True, default="")),
                ("repository", models.URLField(blank=True, default="")),
                ("website", models.URLField(blank=True, default="")),
            ],
        ),
        migrations.CreateModel(
            name="Version",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="frog_api.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                (
                    "version",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="frog_api.version",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Categories",
            },
        ),
        migrations.CreateModel(
            name="Entry",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("timestamp", models.IntegerField()),
                ("git_hash", models.CharField(max_length=40)),
                (
                    "category",
                    models.ForeignKey(
                        default="",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="frog_api.category",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "verbose_name_plural": "Entries",
            },
        ),
        migrations.CreateModel(
            name="Measure",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("type", models.CharField(max_length=255)),
                ("value", models.IntegerField()),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="measures",
                        to="frog_api.entry",
                    ),
                ),
            ],
        ),
    ]
