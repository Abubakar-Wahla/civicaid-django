from django.db import models
from django.contrib.auth.models import User
from hub.models import Category


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="volunteer_profile")
    full_name = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)


    categories = models.ManyToManyField(Category, blank=True, related_name="volunteers")

    availability = models.CharField(
        max_length=80,
        blank=True,
        help_text="e.g. evenings, weekends, 2-3 hrs/day"
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username
