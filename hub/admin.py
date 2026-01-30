from django.contrib import admin
from .models import Profile, Category, HelpRequest, RequestUpdate
from .models import ContactMessage


admin.site.register(ContactMessage)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(HelpRequest)
admin.site.register(RequestUpdate)
