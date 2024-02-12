from django.shortcuts import render,redirect
from django.contrib.auth import logout
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password,check_password
User = get_user_model()
from django.http import JsonResponse
from .models import *
# Create your views here.
def index(request):
      return render(request,"achievemate/index.html")


def choose_coach(request):
      return render(request,"achievemate/choose_coach.html")

def logout_user(request):
      logout(request)
      return redirect("index")

@receiver(user_signed_up)
def set_user_type(sender, request, user, **kwargs):
    print("Inside Signal")
    if user.socialaccount_set.filter(provider='google').exists():
        social_account = user.socialaccount_set.get(provider='google')
        user.user_type = 'google'
        user.is_verified=True
        user.google_id = social_account.uid  # Set google_id field with the Google UID
        user.save()
        
from django.core.exceptions import ObjectDoesNotExist

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password =request.POST.get('password')
        print(username,password)
        
        try:
            existing_user = User.objects.get(email=email)
            return JsonResponse({"error": "User with this email already exists."})
        except ObjectDoesNotExist:
            pass
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True  # User is inactive until email confirmation
        user.is_verified=False
        user.save()

        # Send confirmation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        message = render_to_string('achievemate/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email,])

        return JsonResponse({"success":True})  # Redirect to homepage after registration
    else:
        return render(request, 'achievemate/index.html')  # Render the sign-up form template

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('choose_coach')  # Redirect to homepage after successful activation
    else:
        return render(request, 'achievemate/activation_failed.html')  # Render activation failed template


from django.contrib.auth import authenticate, login

def login_user(request):
    if request.method == 'POST':
        usern = request.POST.get('username')
        passw= request.POST.get('password')
        
        user = authenticate(request, username=usern, password=passw, backend='django.contrib.auth.backends.ModelBackend')
        print(user)
        if user is not None:
            if user.is_verified:
                login(request, user)
                return JsonResponse({"success":True})  # Redirect to homepage after successful login
            else:
               return JsonResponse({'error': 'Account is Inactivated , Please activate your account verifying link sent in you mail'})  # Render account inactive template
        else:
            return JsonResponse({'error': 'Invalid credentials'})  # Render login form with error message
    else:
        return render(request, 'achievemate/index.html')  # Render login form template
 
 
def about_us(request):
      return render(request,"achievemate/about.html")
 
def our_coach(request):
      return render(request,"achievemate/our_coach.html")
 
def services(request):
      return render(request,"achievemate/services.html")
 
def testimonials(request):
      return render(request,"achievemate/testimonial.html")
 
def subscription(request):
      return render(request,"achievemate/subscription.html")

def find_coach(request):
      return render(request,"achievemate/find_coach.html")
    
def coach(request):
    context={}
    all_coach_details=AiCoach.objects.all()
    context.update({'all_coach_details':all_coach_details})
    return render(request,"achievemate/dashboard/coach.html",context)

def coach_details(request,pk):
    context={}
    coach_data=AiCoach.objects.filter(id=pk)[0]
    context.update({'coach_data':coach_data})
    return render(request,"achievemate/dashboard/coach_details.html",context)

def profile(request):
    return render(request,"achievemate/dashboard/profile.html")

def chat(request):
    return render(request,"achievemate/dashboard/chat.html")

def chat(request,uid,cid):
    context={}
    context.update({'uid':uid,'cid':cid})
    return render(request,"achievemate/dashboard/chat.html",context)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        # Assuming 'uid' and 'cid' are available in the context
        uid = request.POST.get('uid')
        cid = request.POST.get('cid')

        # Assuming 'user_type' is determined based on the context
        user_type = 'user'

        # Save the message to the database
        chat = Chat.objects.create(
            chat_text=message_text,
            user_type=user_type,
            user_id=uid,
            coach_id=cid
        )
        # Optionally, perform additional processing or validations here

        return JsonResponse({'status': 'Message sent successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def get_messages(request):
    # Retrieve messages from the Chat model
    messages = Chat.objects.filter(is_delete=0).order_by('created_date')
    print(messages)
    message_texts = [message.chat_text for message in messages]

    return JsonResponse({'messages': message_texts})

def dashbaord(request):
    return render(request,"achievemate/dashboard/dashboard.html")

def progress_tracking(request):
    return render(request,"achievemate/dashboard/progress_tracking.html")



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
