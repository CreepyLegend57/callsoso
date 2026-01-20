from django.contrib import admin
from .models import (
    Article,
    Resource,
    Category,
    Collaboration,
    Contribution,
    FoundersList,
    MagazineIssue, 
    PopularArticle
)
 

# ===========================
# CATEGORY
# ===========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)

# ===========================
# MAGAZINE ISSUE
# ===========================
@admin.register(MagazineIssue)
class MagazineIssueAdmin(admin.ModelAdmin):
    list_display = ("title", "published_date", "is_featured", "is_published")
    list_filter = ("is_featured", "is_published", "published_date", "categories")
    search_fields = ("title", "description")
    filter_horizontal = ("categories",)
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ("-published_date",)

    fieldsets = (
        ("Core", {
            "fields": ("title", "slug", "description", "categories"),
        }),
        ("Media", {
            "fields": ("cover_image", "cover_image_url", "video_preview_url"),
            "description": "Upload a cover image or paste external URL. Optionally add a video preview.",
        }),
        ("Publishing", {
            "fields": ("published_date", "is_featured", "is_published"),
        }),
    )

# ===========================
# POPULAR ARTICLES
# ===========================
@admin.register(PopularArticle)
class PopularArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "date")
    search_fields = ("title",)
    ordering = ("-date",)


# ===========================
# ARTICLE / NEWS
# ===========================
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published_date",
        "is_published",
        "is_featured",
    )
    list_filter = (
        "is_published",
        "is_featured",
        "published_date",
        "categories",
    )
    search_fields = (
        "title",
        "body",
        "excerpt",
        "summary",
    )
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    date_hierarchy = "published_date"
    ordering = ("-published_date",)

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "excerpt", "summary", "body"),
        }),
        ("Media", {
            "fields": ("image", "image_url"),
            "description": "Upload an image OR paste an external image URL (Pinterest, Unsplash, etc.)",
        }),
        ("Metadata", {
            "fields": (
                "author",
                "categories",
                "published_date",
                "is_featured",
                "is_published",
            ),
        }),
    )


# ===========================
# RESOURCE (Knowledge Center)
# ===========================
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "resource_type",
        "published",
        "is_featured",
        "created_at",
    )
    list_filter = (
        "resource_type",
        "published",
        "is_featured",
        "categories",
    )
    search_fields = (
        "title",
        "description",
    )
    filter_horizontal = ("categories",)
    ordering = ("-created_at",)

    fieldsets = (
        ("Core", {
            "fields": (
                "title",
                "description",
                "resource_type",
                "categories",
            ),
        }),
        ("Media", {
            "fields": ("image", "image_url"),
            "description": "Upload an image OR paste an external image URL (Pinterest, YouTube thumbnails, etc.)",
        }),
        ("Linking", {
            "fields": ("link",),
            "description": "Internal or external link (article, webinar page, YouTube, Medium, etc.)",
        }),
        ("Publishing", {
            "fields": (
                "published",
                "is_featured",
            ),
        }),
    )


# ===========================
# COLLABORATION
# ===========================
@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "growth_stage", "is_active", "planted_date")
    list_filter = ("growth_stage", "is_active")
    search_fields = ("name", "organisation", "description")
    ordering = ("-planted_date",)


# ===========================
# CONTRIBUTION
# ===========================
@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("contributor_name", "source", "amount", "date")
    list_filter = ("source", "date")
    search_fields = ("contributor_name", "email", "message")
    ordering = ("-date",)


# ===========================
# FOUNDERS LIST
# ===========================
@admin.register(FoundersList)
class FoundersListAdmin(admin.ModelAdmin):
    list_display = ("email", "joined")
    search_fields = ("email",)
    ordering = ("-joined",)
