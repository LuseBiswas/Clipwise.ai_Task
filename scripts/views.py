from django.shortcuts import render, redirect
from .models import Script
from .utils import generate_ai_script
import PyPDF2 # type: ignore
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore


def extract_text_from_file(file):
    """Extract text from uploaded file (supports .txt and .pdf)."""
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")  # Read text file
    elif file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        return text
    return ""

def extract_text_from_link(url):
    """Fetch and extract meaningful text from a URL."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error for failed requests
        soup = BeautifulSoup(response.text, "html.parser")

        # Wikipedia-specific: Extract article content
        if "wikipedia.org" in url:
            # Wikipedia articles have content inside the 'div#bodyContent' section
            content_section = soup.find("div", {"id": "bodyContent"})
            paragraphs = content_section.find_all("p")
            extracted_content = "\n".join([p.text for p in paragraphs if p.text.strip()])  # Collect all paragraph texts
            if not extracted_content:
                extracted_content = "No article content found."
        else:
            # For non-Wikipedia pages, try extracting first few paragraphs
            paragraphs = soup.find_all("p")
            extracted_content = "\n".join([p.text for p in paragraphs if p.text.strip()][:3])  # Limit to first 3 paragraphs
            if not extracted_content:
                extracted_content = "No content extracted."

        return f"Extracted from Link:\n{extracted_content}"
    except Exception as e:
        return f"Error fetching content from link: {e}"


def home(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        uploaded_file = request.FILES.get("file")
        link = request.POST.get("link")

        # Extract text from file
        if uploaded_file:
            extracted_text = extract_text_from_file(uploaded_file)
            content += f"\n\nExtracted from File:\n{extracted_text}"

        # Extract text from link
        if link:
            link_text = extract_text_from_link(link)
            content += f"\n\nExtracted from Link:\n{link_text}"

        # Generate AI Script
        ai_script = generate_ai_script(content)

        # Save the script with AI-generated content
        Script.objects.create(title=title, content=ai_script, file=uploaded_file, link=link)
        
        # Pass the generated AI script to the template
        return render(request, "scripts/script_detail.html", {"ai_script": ai_script})


    return render(request, "scripts/home.html")

def script_list(request):
    scripts = Script.objects.all().order_by("-created_at")  # Show latest scripts first
    return render(request, "scripts/script_list.html", {"scripts": scripts})
