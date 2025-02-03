from django.shortcuts import render, redirect
from .models import Script
import PyPDF2 # type: ignore


def extract_text_from_file(file):
    """Extract text from uploaded file (supports .txt and .pdf)."""
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")  # Read text file
    elif file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    return ""

def home(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            extracted_text = extract_text_from_file(uploaded_file)
            content += "\n\n" + extracted_text  # Append extracted text to user input

        Script.objects.create(title=title, content=content, file=uploaded_file)
        return redirect("script_list")

    return render(request, "scripts/home.html")

def script_list(request):
    scripts = Script.objects.all().order_by("-created_at")  # Show latest scripts first
    return render(request, "scripts/script_list.html", {"scripts": scripts})
