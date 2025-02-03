from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client with your DeepSeek API key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # OpenRouter base URL for DeepSeek
    api_key=settings.DEEPSEEK_API_KEY,  # Load API key from settings
)

def generate_ai_script(prompt):
    """Generate AI script using the DeepSeek API based on the provided prompt."""
    try:
        # Create the completion request with the specified model
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional: Your site URL for rankings
                "X-Title": "<YOUR_SITE_NAME>",  # Optional: Your site title for rankings
            },
            model="openai/gpt-3.5-turbo",  # Model used by DeepSeek
            messages=[
                {
                    "role": "user",  # User prompt
                    "content": prompt,
                }
            ]
        )
        
        # Extract the generated content from the response
        ai_script = completion.choices[0].message.content.strip()  # Correct way to access content
        
        return ai_script if ai_script else "No script generated."
    
    except Exception as e:
        return f"Error: {str(e)}"
