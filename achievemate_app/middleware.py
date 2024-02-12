# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the requested URL matches the specified URL
        if request.path == '/accounts/social/signup/':
            # Redirect to the index page
            # return redirect('index')  # Replace 'index' with the name of your index view or URL pattern
            return redirect('{}?message=User already exists. Please login with your existing account.'.format(reverse('index')))
            
        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response
