from django.db import migrations
from django.utils.text import slugify


DEFAULT_CATEGORIES = [
    "Circular Economy",
    "Corporate Surplus",
    "Upcycling & Makers",
    "Community Initiatives",
    "Sustainability & Climate",
    "Policy & Legislation",
    "Training & Courses",
    "Resource Management",
    "Best Practices",
    "Events & Webinars",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("website", "Category")

    for name in DEFAULT_CATEGORIES:
        slug = slugify(name)

        Category.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
            },
        )


def remove_seeded_categories(apps, schema_editor):
    Category = apps.get_model("website", "Category")

    Category.objects.filter(
        slug__in=[slugify(name) for name in DEFAULT_CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0007_alter_category_options"),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_seeded_categories),
    ]