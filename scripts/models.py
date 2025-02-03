from django.db import models

class Script(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    file = models.FileField(upload_to="uploads/", blank=True, null=True)  # Allow file uploads
    link = models.URLField(blank=True, null=True)  # Store external links

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
