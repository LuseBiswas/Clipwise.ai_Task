from django.shortcuts import render, redirect
from .models import Script

def home(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            Script.objects.create(title=title, content=content)
            return redirect("script_list")  # Redirect to the list of scripts

    return render(request, "scripts/home.html")

def script_list(request):
    scripts = Script.objects.all().order_by("-created_at")  # Show latest scripts first
    return render(request, "scripts/script_list.html", {"scripts": scripts})
