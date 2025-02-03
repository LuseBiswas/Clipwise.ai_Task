import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Script
from .utils import generate_ai_script
import PyPDF2 # type: ignore
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from reportlab.pdfgen import canvas
from io import BytesIO


def index(request):
    return render(request, 'index.html')

def generate_script(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt')

            if prompt:
                ai_script = generate_ai_script(prompt)
                return JsonResponse({'script': ai_script})
            else:
                return JsonResponse({'error': 'Prompt is required.'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
        content = request.POST.get("content", "")
        language = request.POST.get("language", "en")
        uploaded_file = request.FILES.get("file")
        link = request.POST.get("link")

        # Auto-generate title from content
        title = content.split()[:5]
        title = " ".join(title) + ("..." if len(content.split()) > 5 else "")
        
        # Extract text from file
        if uploaded_file:
            extracted_text = extract_text_from_file(uploaded_file)
            content += f"\n\nExtracted from File:\n{extracted_text}"

        # Extract text from link
        if link:
            link_text = extract_text_from_link(link)
            content += f"\n\nExtracted from Link:\n{link_text}"

        # Generate AI Script with language parameter
        prompt = f"Generate a script in {dict(Script.LANGUAGE_CHOICES)[language]}:\n{content}"
        ai_script = generate_ai_script(prompt)

        # Save the script
        Script.objects.create(
            title=title,
            content=ai_script,
            language=language,
            file=uploaded_file,
            link=link
        )

        return render(request, "scripts/script_detail.html", {
            "ai_script": ai_script,
            "language": language
        })

    return render(request, "scripts/home.html")

def script_list(request):
    search_query = request.GET.get('q', '')
    
    # Filter scripts based on search query
    scripts = Script.objects.all()
    if search_query:
        scripts = scripts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(scripts, 10)  # Show 10 scripts per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "scripts/script_list.html", {
        "scripts": page_obj,
        "search_query": search_query
    })

def export_script_txt(request, script_id):
    script = Script.objects.get(pk=script_id)
    response = HttpResponse(script.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{script.title}.txt"'
    return response

def export_script_pdf(request, script_id):
    script = Script.objects.get(pk=script_id)
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add content to PDF
    y = 800  # Starting y position
    for line in script.content.split('\n'):
        if y < 50:  # Check if we need a new page
            p.showPage()
            y = 800
        p.drawString(50, y, line)
        y -= 15  # Move down for next line
    
    p.showPage()
    p.save()
    
    # FileResponse
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{script.title}.pdf"'
    
    return response