from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.templatetags.static import static

# ===========================
# CATEGORY (shared)
# ===========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ===========================
# MAGAZINE ISSUE
# ===========================
class MagazineIssue(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="magazine/covers/", blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    video_preview_url = models.URLField(blank=True, null=True)
    published_date = models.DateField(default=timezone.now)
    categories = models.ManyToManyField(Category, blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:250]
            slug = base_slug
            i = 1
            while MagazineIssue.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            return reverse("magazine_detail", kwargs={"slug": self.slug})
        except Exception:
            return "#"

    @property
    def display_image(self):
        if self.cover_image:
            return self.cover_image.url
        if self.cover_image_url:
            return self.cover_image_url
        return static("images/placeholder.jpg")

# ===========================
# POPULAR ARTICLES (Sidebar)
# ===========================
class PopularArticle(models.Model):
    title = models.CharField(max_length=250)
    url = models.URLField()
    image = models.ImageField(upload_to="articles/popular/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return static("images/placeholder.jpg")



# ===========================
# COLLABORATION
# ===========================
class Collaboration(models.Model):
    GROWTH_STAGE_CHOICES = [
        (1, "Seed"),
        (2, "Sprout"),
        (3, "Growth"),
        (4, "Bloom"),
        (5, "Harvest"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    organisation = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    planted_date = models.DateTimeField(auto_now_add=True)
    growth_stage = models.IntegerField(choices=GROWTH_STAGE_CHOICES, default=1)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Stage {self.growth_stage})"


# ===========================
# CONTRIBUTION
# ===========================
class Contribution(models.Model):
    SOURCE_CHOICES = [
        ("donation", "Donation"),
        ("sponsorship", "Sponsorship"),
        ("grant", "Grant"),
        ("material", "Material Support"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contributor_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    message = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.contributor_name or (self.user.username if self.user else "Anonymous")
        return f"{name} – {self.source}"


# ===========================
# FOUNDERS LIST
# ===========================
class FoundersList(models.Model):
    email = models.EmailField(unique=True)
    joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.email


# ===========================
# ARTICLE / NEWS (KEEPING)
# ===========================
class Article(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    excerpt = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="articles/images/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    published_date = models.DateField(default=timezone.now)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    categories = models.ManyToManyField(Category, blank=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:250]
            slug = base_slug
            i = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            return reverse("article_detail", kwargs={"slug": self.slug})
        except Exception:
            return "#"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return static("images/placeholder.jpg")


# ===========================
# RESOURCE (KNOWLEDGE CENTER)
# ===========================
class Resource(models.Model):
    RESOURCE_TYPES = (
        ("highlight", "Highlight"),
        ("case_study", "Case Study"),
        ("webinar", "Webinar"),
        ("learning", "Learning"),
        ("other", "Other / Future"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
    )

    categories = models.ManyToManyField(Category, blank=True)

    image = models.ImageField(
        upload_to="resources/images/",
        blank=True,
        null=True,
    )
    image_url = models.URLField(blank=True)

    link = models.URLField(
        blank=True,
        help_text="Internal or external link (Pinterest, YouTube, Medium, etc.)",
    )

    is_featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return static("images/placeholder.jpg")
