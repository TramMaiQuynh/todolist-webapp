from django.test import TestCase
from tasks.models import Category
from django.utils.text import slugify

class CategoryModelTest(TestCase):
    def test_create_default_categories(self):
        # Clear existing categories
        Category.objects.all().delete()

        # Ensure no categories exist initially
        self.assertEqual(Category.objects.count(), 0)

        # Call the method to create default categories
        Category.create_default_categories()

        # Check that the default categories have been created
        default_categories = [name for name, _ in Category.DEFAULT_CATEGORIES]
        created_categories = Category.objects.filter(name__in=default_categories)

        self.assertEqual(created_categories.count(), len(default_categories))

        for category in created_categories:
            self.assertTrue(category.is_default)
            self.assertIn(category.name, default_categories)
            self.assertEqual(category.slug, slugify(category.name))