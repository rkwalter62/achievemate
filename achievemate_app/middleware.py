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
# middlearwe to check chatsessions so that allow according to user subscription plan

from django.http import JsonResponse
from django.utils import timezone
from .models import DailyChatSession, UserStripe

class ChatSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            today = timezone.now().date()
            try:
                user_stripe = UserStripe.objects.get(user=request.user, is_active=True)
                
                max_sessions = user_stripe.plan.max_sessions_per_day
                chat_session, created = DailyChatSession.objects.get_or_create(user=request.user, date=today)

                if chat_session.session_count >= max_sessions:
                    return JsonResponse({'error': 'Daily chat session limit exceeded'}, status=403)
            except UserStripe.DoesNotExist:
                return JsonResponse({'error': 'Subscription not found or inactive'}, status=403)

        response = self.get_response(request)
        return response
