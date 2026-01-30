from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("requests/", views.requests_list, name="requests_list"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("offers/", views.offers_list, name="offers_list"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("requests/new/", views.create_request, name="create_request"),
    path("my/requests/", views.my_requests, name="my_requests"),
    path("requests/<int:pk>/edit/", views.update_request, name="update_request"),
    path("requests/<int:pk>/delete/", views.delete_request, name="delete_request"),
    path("requests/<int:pk>/claim/", views.claim_request, name="claim_request"),
    path("requests/<int:pk>/complete/", views.complete_request, name="complete_request"),
    path("requests/<int:pk>/updates/new/", views.add_update, name="add_update"),
    path("my/claimed/", views.my_claimed_requests, name="my_claimed_requests"),
    path("my/completed/", views.my_completed_requests, name="my_completed_requests"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("requests/in-progress/", views.in_progress_requests, name="in_progress_requests"),
    path("requests/completed/", views.completed_requests, name="completed_requests"),
    path("volunteers/", views.offers_list, name="offers_list"),
    path("volunteers/<int:pk>/", views.volunteer_detail, name="volunteer_detail"),
    path("impact/", views.impact, name="impact"),
]
