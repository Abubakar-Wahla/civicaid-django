from django import forms
from .models import HelpRequest
from .models import RequestUpdate
from .models import Profile
from .models import ContactMessage

class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ["title", "description", "category", "city", "urgency"]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g., Need urgent blood donor (O+)", "class": "form-input"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Explain the situation clearly...", "class": "form-input"}),
            "city": forms.TextInput(attrs={"placeholder": "e.g., Lahore", "class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "urgency": forms.Select(attrs={"class": "form-input"}),
        }

class RequestUpdateForm(forms.ModelForm):
    class Meta:
        model = RequestUpdate
        fields = ["message"]
        widgets = {
            "message": forms.TextInput(attrs={
                "placeholder": "Post an update (e.g., Volunteer is on the way)…",
                "class": "form-input"
            })
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "city", "bio"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g., Lahore"}),
            "bio": forms.Textarea(attrs={"class": "form-input", "rows": 4, "placeholder": "How can you help?"}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"}),
            "subject": forms.TextInput(attrs={"class": "form-input", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-input", "rows": 5, "placeholder": "Write your message..."}),
        }