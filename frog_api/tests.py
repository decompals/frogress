from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from frog_api.models import Category, Entry, Measure, Project, Version


class CreateCategoryTests(APITestCase):
    def test_create_categories(self) -> None:
        """
        Ensure that the category creation endpoint works
        """

        # Create a test Project and Version
        project = Project(slug="oot", name="Ocarina of Time", auth_key="test_key_123")
        project.save()

        version = Version(slug="us", name="US", project=project)
        version.save()

        response = self.client.post(
            reverse("category-structure", args=[project.slug, version.slug, "total"]),
            {
                "api_key": "test_key_123",
                "name": "Total",
            },
            format="json",
        )

        response = self.client.post(
            reverse("category-structure", args=[project.slug, version.slug, "actors"]),
            {
                "api_key": "test_key_123",
                "name": "Actors",
            },
            format="json",
        )

        # Confirm we created the categories and that they are in the DB
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)


class CreateEntriesTests(APITestCase):
    def test_create_entries(self) -> None:
        """
        Ensure that the entry creation endpoint works
        """
        create_json = {
            "api_key": "test_key_123",
            "entries": [
                {
                    "categories": {
                        "default": {
                            "code_matching": 103860,
                            "code_total": 4747584,
                            "asm": 4597948,
                            "nonmatching_functions_count": 49,
                            "assets_identified": 0,
                            "assets_total": 40816656,
                            "code_decompiled": 120152,
                            "assets_debinarised": 0,
                        },
                        "actors": {
                            "code_matching": 103860,
                            "code_total": 4747584,
                        },
                    },
                    "timestamp": 1615435438,
                    "git_hash": "e788bfecbfb10afd4182332db99bb562ea75b1de",
                }
            ],
        }

        # Create a test Project, Version, and Categories
        project = Project(slug="oot", name="Ocarina of Time", auth_key="test_key_123")
        project.save()

        version = Version(slug="us", name="US", project=project)
        version.save()

        category1 = Category(slug="default", name="Default", version=version)
        category1.save()

        category2 = Category(slug="actors", name="Actors", version=version)
        category2.save()

        response = self.client.post(
            reverse("version-data", args=[project.slug, version.slug]),
            create_json,
            format="json",
        )

        # Confirm we created the entries and that they are in the DB
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Entry.objects.count(), 2)
        self.assertEqual(Measure.objects.count(), 10)
