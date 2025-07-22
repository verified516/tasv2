# Routes package
from flask import render_template, request

def render_template_with_htmx(template_name, **context):
    """
    Render a template with HTMX support - returns proper content for HTMX requests.
    """
    # Check if it's an HTMX request
    if request.headers.get('HX-Request'):
        # For HTMX requests, provide a simpler layout template
        context['layout'] = 'htmx_layout.html'
    
    # For normal requests, render with base template
    return render_template(template_name, **context)