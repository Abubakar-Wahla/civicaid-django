from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import VolunteerProfile
from hub.models import Category


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply same class to all inputs
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "auth-input"})

        # Optional: placeholders (looks more premium)
        self.fields["username"].widget.attrs.update({"placeholder": "Username"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm password"})

class VolunteerProfileForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = VolunteerProfile
        fields = ("full_name", "city", "bio","contact_email", "availability", "categories")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Premium input styling
        for name, field in self.fields.items():
            if name == "categories":
                continue
            field.widget.attrs.update({"class": "auth-input"})
        self.fields["bio"].widget.attrs.update({"rows": 4})