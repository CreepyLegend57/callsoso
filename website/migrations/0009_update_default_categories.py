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


def update_categories(apps, schema_editor):
    Category = apps.get_model("website", "Category")

    # Remove the old defaults
    Category.objects.filter(
        slug__in=[
            "case-studies",
            "climate-impact",
            "community-culture",
            "design-upcycling",
            "education-learning",
            "materials-waste",
            "policy-systems",
        ]
    ).delete()

    # Ensure the new defaults exist
    for name in DEFAULT_CATEGORIES:
        slug = slugify(name)

        Category.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_seed_default_categories"),
    ]

    operations = [
        migrations.RunPython(update_categories),
    ]