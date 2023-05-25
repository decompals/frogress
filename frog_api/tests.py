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


SAMPLE_PROJECT_SLUG = "oot"
SAMPLE_VERSION_SLUG = "us"
SAMPLE_DATA = {
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


class CreateEntriesTests(APITestCase):
    def create_project_metadata(self, project_slug: str, version_slug: str) -> None:
        # Create a test Project, Version, and Categories
        project = Project(
            slug=project_slug, name="Ocarina of Time", auth_key="test_key_123"
        )
        project.save()

        version = Version(slug=version_slug, name="US", project=project)
        version.save()

        category1 = Category(slug="default", name="Default", version=version)
        category1.save()

        category2 = Category(slug="actors", name="Actors", version=version)
        category2.save()

    def test_create_entries(self) -> None:
        """
        Ensure that the entry creation endpoint works
        """

        self.create_project_metadata(SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG)

        response = self.client.post(
            reverse("version-data", args=[SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG]),
            SAMPLE_DATA,
            format="json",
        )

        # Confirm we created the entries and that they are in the DB
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entry.objects.count(), 2)
        self.assertEqual(Measure.objects.count(), 10)

    def test_create_duplicate_entries(self) -> None:
        """
        Ensure that it's impossible to make duplicate entries
        """

        self.create_project_metadata(SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG)

        response = self.client.post(
            reverse("version-data", args=[SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG]),
            SAMPLE_DATA,
            format="json",
        )

        # Confirm we created the entries and that they are in the DB
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entry.objects.count(), 2)
        self.assertEqual(Measure.objects.count(), 10)

        response = self.client.post(
            reverse("version-data", args=[SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG]),
            SAMPLE_DATA,
            format="json",
        )

        # Ensure we got a bad request code since we shouldn't be able to create duplicate entries
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Entry.objects.count(), 2)
        self.assertEqual(Measure.objects.count(), 10)

    def test_atomicity(self) -> None:
        """
        Ensure that if some entries fail to be created, none are created
        """

        self.create_project_metadata(SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG)

        yucky_data = {
            "api_key": "test_key_123",
            "entries": [
                {
                    "categories": {
                        "actors": {
                            "code_matching": 103860,
                            "code_total": 4747584,
                        },
                    },
                    "timestamp": 1615435438,
                    "git_hash": "e788bfecbfb10afd4182332db99bb562ea75b1de",
                },
                {
                    "categories": {
                        "actors": {
                            "code_matching": 103860,
                            "code_total": 4747584,
                        },
                    },
                    "timestamp": 1615435438,
                    "git_hash": "e788bfecbfb10afd4182332db99bb562ea75b1de",
                },
            ],
        }

        response = self.client.post(
            reverse("version-data", args=[SAMPLE_PROJECT_SLUG, SAMPLE_VERSION_SLUG]),
            yucky_data,
            format="json",
        )

        # Confirm no entries or measures are created
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Entry.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
