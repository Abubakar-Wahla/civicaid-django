from django.shortcuts import render, get_object_or_404
from .models import HelpRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .forms import HelpRequestForm,RequestUpdateForm
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from .models import HelpRequest, Category
from .models import Profile
from .forms import ProfileForm,ContactForm
from .models import Category
from accounts.models import VolunteerProfile
from django.db.models import Count


def home(request):
    total_requests = HelpRequest.objects.count()
    open_requests = HelpRequest.objects.filter(status="OPEN").count()
    in_progress = HelpRequest.objects.filter(status="IN_PROGRESS").count()
    completed = HelpRequest.objects.filter(status="COMPLETED").count()

    latest_open = HelpRequest.objects.filter(status="OPEN").select_related("category","owner").order_by("-created")[:3]

    return render(request, "hub/home.html", {
        "total_requests": total_requests,
        "open_requests": open_requests,
        "in_progress": in_progress,
        "completed": completed,
        "latest_open": latest_open,
    })


def requests_list(request):
    # OPEN only (main marketplace)
    return _requests_index(request, base_status="OPEN", title="Help Requests (Open)")


def in_progress_requests(request):
    return _requests_index(request, base_status="IN_PROGRESS", title="In Progress Requests")


def completed_requests(request):
    return _requests_index(request, base_status="COMPLETED", title="Completed Requests")


def _requests_index(request, base_status, title):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    urgency = request.GET.get("urgency", "").strip()

    qs = HelpRequest.objects.select_related("category", "owner").filter(status=base_status)

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(city__icontains=q)
            | Q(category__name__icontains=q)
        )

    if category_id:
        qs = qs.filter(category_id=category_id)

    if urgency:
        qs = qs.filter(urgency=urgency)

    paginator = Paginator(qs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all().order_by("name"),
        "q": q,
        "category_id": category_id,
        "urgency": urgency,
        "page_title": title,
        "base_status": base_status,
    }
    return render(request, "hub/requests_list.html", context)


def request_detail(request, pk):
    req = get_object_or_404(HelpRequest, id=pk)

    # Base queryset (optimized)
    matches = VolunteerProfile.objects.select_related("user").prefetch_related("categories")

    filters = Q()

    if req.city:
        filters |= Q(city__iexact=req.city)

    if req.category_id:
        filters |= Q(categories__id=req.category_id)

    if filters:
        matches = matches.filter(filters).distinct()
    else:
        matches = matches.none()

    matches = matches.order_by("-created")[:6]

    context = {
        "item": req,
        "matches": matches,
    }

    return render(request, "hub/request_detail.html", context)



def offers_list(request):
    volunteers = Profile.objects.filter(role="VOLUNTEER").select_related("user").order_by("user__username")
    return render(request, "hub/offers_list.html", {"volunteers": volunteers})


def about(request):
    return render(request, "hub/about.html")


def contact(request):
    return render(request, "hub/contact.html")

@login_required
def create_request(request):
    form = HelpRequestForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            messages.success(request, "Request created successfully.")
            return redirect("request_detail", pk=obj.id)
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, "hub/request_form.html", {"form": form})


@login_required
def my_requests(request):
    requests = HelpRequest.objects.filter(owner=request.user).select_related("category").order_by("-created")
    return render(request, "hub/my_requests.html", {"requests": requests})

@login_required
def update_request(request, pk):
    obj = get_object_or_404(HelpRequest, id=pk)

    if obj.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this request.")

    form = HelpRequestForm(request.POST or None, instance=obj)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect("request_detail", pk=obj.id)
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, "hub/request_form.html", {"form": form, "is_edit": True})


@login_required
def delete_request(request, pk):
    obj = get_object_or_404(HelpRequest, id=pk)

    if obj.owner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this request.")

    if request.method == "POST":
        obj.delete()
        messages.success(request, "Request deleted.")
        return redirect("my_requests")

    return render(request, "hub/request_confirm_delete.html", {"item": obj})

@login_required
def claim_request(request, pk):
    req = get_object_or_404(HelpRequest, id=pk)

    # Block owner from claiming own request
    if request.user == req.owner:
        messages.error(request, "You cannot claim your own request.")
        return redirect("request_detail", pk=req.id)

    # Only OPEN requests can be claimed
    if req.status != "OPEN":
        messages.error(request, "Only open requests can be claimed.")
        return redirect("request_detail", pk=req.id)

    # Confirm page (GET) -> show confirm template
    if request.method == "GET":
        return render(request, "hub/request_confirm_claim.html", {"item": req})

    # Claim action (POST)
    req.assigned_to = request.user
    req.status = "IN_PROGRESS"
    req.save()
    messages.success(request, "You claimed this request. Status is now In Progress.")
    return redirect("request_detail", pk=req.id)


@login_required
def complete_request(request, pk):
    req = get_object_or_404(HelpRequest, id=pk)


    if request.user == req.owner:
        messages.error(request, "You cannot complete your own request.")
        return redirect("request_detail", pk=req.id)


    if req.assigned_to != request.user:
        messages.error(
            request,
            "Only the volunteer who claimed this request can complete it."
        )
        return redirect("request_detail", pk=req.id)


    if req.status != "IN_PROGRESS":
        messages.error(
            request,
            "Only in-progress requests can be completed."
        )
        return redirect("request_detail", pk=req.id)

    
    if request.method == "GET":
        return render(
            request,
            "hub/request_confirm_complete.html",
            {"item": req}
        )

    req.status = "COMPLETED"
    req.save()

    messages.success(request, "Request marked as completed.")
    return redirect("request_detail", pk=req.id)

@login_required
def add_update(request, pk):
    obj = get_object_or_404(HelpRequest, id=pk)

    allowed = (request.user == obj.owner) or (request.user == obj.assigned_to)
    if not allowed:
        return HttpResponseForbidden("Only owner or assigned volunteer can post updates.")

    form = RequestUpdateForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            update = form.save(commit=False)
            update.request = obj
            update.author = request.user
            update.save()
            messages.success(request, "Update posted.")
            return redirect("request_detail", pk=obj.id)
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, "hub/update_form.html", {"form": form, "item": obj})

@login_required
def my_claimed_requests(request):
    qs = HelpRequest.objects.filter(assigned_to=request.user).select_related("category", "owner")
    return render(request, "hub/my_claimed_requests.html", {"requests": qs})


@login_required
def my_completed_requests(request):
    qs = HelpRequest.objects.filter(assigned_to=request.user, status="COMPLETED").select_related("category", "owner")
    return render(request, "hub/my_completed_requests.html", {"requests": qs})

@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("offers_list")
        messages.error(request, "Please fix the errors below.")

    return render(request, "hub/profile_edit.html", {"form": form})

def contact(request):
    form = ContactForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent. We will respond soon.")
            return redirect("contact")
        messages.error(request, "Please fix the errors below.")

    return render(request, "hub/contact.html", {"form": form})

def offers_list(request):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    qs = VolunteerProfile.objects.select_related("user").prefetch_related("categories").order_by("-created")

    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(city__icontains=q)
            | Q(user__username__icontains=q)
            | Q(bio__icontains=q)
        )

    if category_id:
        qs = qs.filter(categories__id=category_id)

    paginator = Paginator(qs.distinct(), 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "hub/offers_list.html", {
        "page_obj": page_obj,
        "categories": Category.objects.all().order_by("name"),
        "q": q,
        "category_id": category_id,
    })

def volunteer_detail(request, pk):
    profile = get_object_or_404(
        VolunteerProfile.objects.select_related("user").prefetch_related("categories"),
        pk=pk
    )

    # Suggested open requests:
    # - Prefer same city if profile.city is set
    # - Also match categories
    cat_ids = list(profile.categories.values_list("id", flat=True))

    suggested = HelpRequest.objects.select_related("category", "owner").filter(status="OPEN")

    filters = Q()
    if profile.city:
        filters |= Q(city__iexact=profile.city)

    if cat_ids:
        filters |= Q(category_id__in=cat_ids)

    if filters:
        suggested = suggested.filter(filters)

    suggested = suggested.order_by("-created")[:6]

    return render(request, "hub/volunteer_detail.html", {
        "profile": profile,
        "suggested": suggested,
    })

def impact(request):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()

    qs = HelpRequest.objects.select_related("category", "owner").filter(status="COMPLETED").order_by("-updated")

    if q:
        qs = qs.filter(title__icontains=q)

    if category_id:
        qs = qs.filter(category_id=category_id)

    if city:
        qs = qs.filter(city__icontains=city)

    # small KPI cards
    totals = {
        "completed": HelpRequest.objects.filter(status="COMPLETED").count(),
        "in_progress": HelpRequest.objects.filter(status="IN_PROGRESS").count(),
        "open": HelpRequest.objects.filter(status="OPEN").count(),
    }

    top_categories = (
        HelpRequest.objects.filter(status="COMPLETED")
        .values("category__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    return render(request, "hub/impact.html", {
        "page_obj": qs[:12],  # keep it simple (no pagination yet)
        "categories": Category.objects.all().order_by("name"),
        "q": q,
        "category_id": category_id,
        "city": city,
        "totals": totals,
        "top_categories": top_categories,
    })