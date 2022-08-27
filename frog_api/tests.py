from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from frog_api.models import Category, Project, Version


class CreateCategoriesTests(APITestCase):
    def test_create_categories(self) -> None:
        """
        Ensure that the category creation endpoint works
        """

        create_json = {
            "api_key": "test_key_123",
            "categories": {
                "total": "Total",
                "actors": "Actors",
            },
        }

        # Create a test Project and Version
        project = Project(slug="oot", name="Ocarina of Time", auth_key="test_key_123")
        project.save()

        version = Version(slug="us", name="US", project=project)
        version.save()

        self.assertEqual(Category.objects.count(), 0)

        response = self.client.post(
            reverse("category-structure", args=[project.slug, version.slug]),
            create_json,
            format="json",
        )

        # Confirm we created the categories and that they are in the DB
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), len(create_json["categories"]))
