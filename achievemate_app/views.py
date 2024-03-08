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
from django.db.models import Count,Q
from django.contrib.auth.hashers import make_password,check_password
User = get_user_model()
from django.http import JsonResponse
from .models import *
from django.contrib import messages


# Define the login_required decorator
def login_required(function):
    """
    Decorator for views that checks whether the user is logged in.
    Redirects to the index URL if user is not logged in.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('index')  # Assuming 'index' is the name of your index URL
        return function(request, *args, **kwargs)
    return wrapper
# Create your views here.
def index(request):
      return render(request,"achievemate/index.html")

@login_required
def choose_coach(request):
      return render(request,"achievemate/choose_coach.html")
  
@login_required
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
        UserProfile.objects.create(user=user)
        
from django.core.exceptions import ObjectDoesNotExist

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password =request.POST.get('password')
        print(username,password)
        try:
            unverified_user = User.objects.get(email=email,is_verified=False)
            unverified_user.delete()
        except:
            pass
        try:
            existing_user = User.objects.get(email=email)
            return JsonResponse({"error": "User with this email already exists."})
        except ObjectDoesNotExist:
            pass
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True  # User is inactive until email confirmation
        user.is_verified=False
        user.save()
        UserProfile.objects.create(user=user)
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

@login_required
def profile(request):
    context={}
    user_profile_data=UserProfile.objects.get(user=request.user)
    context.update({'user_profile_data':user_profile_data})
    if request.method == 'POST':
        user_profile_data.firstname=request.POST.get('firstname')
        user_profile_data.lastname=request.POST.get('lastname')
        user_profile_data.save() 
        if 'profilepic' in request.FILES:
            user_profile_data.profilepic = request.FILES['profilepic']
            user_profile_data.save() 
        if not request.POST.get('current_password') and not request.POST.get('new_password') and not request.POST.get('confirm_new_password'):
            pass
        elif True:
            if request.POST.get('current_password')  and request.POST.get('new_password') and request.POST.get('confirm_new_password'):    
                current_password = request.POST.get('current_password')
                new_password = request.POST.get('new_password')
                confirm_new_password = request.POST.get('confirm_new_password')
            #     # Check if the current password matches the user's password
                if request.user.check_password(current_password):
            #         # Check if the new password and confirm new password match
                    if new_password == confirm_new_password:
                        print("password amcthes")
                        # Update the user's password
                        request.user.password = make_password(new_password)
                        request.user.save()
                        # Redirect back to the profile page
                        return JsonResponse({"success":True,"message":"Password updated Succesfully"})
                    else:
                        return JsonResponse({"success":True,"message":"New Password And Conform New password Not Matched"})
                else:
                    return JsonResponse({"success":True,"message":"Current Password is Incorrect"})
            else:
                return JsonResponse({"success": True, "message": "Please fill out all the fields to update password"})
        return JsonResponse({"success":True,"message":"Profile Updated Succesfully"})
    return render(request,"achievemate/dashboard/profile.html",context)


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
 
# views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib import messages
import random
import string

def generate_temporary_password(length=10):
    """Generate a temporary password."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def forgot_password_user(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('username')
        user = None

        user = User.objects.filter(Q(email=email_or_username) | Q(username=email_or_username),user_type='standard').first()     
        if user:
            temporary_password = generate_temporary_password()
            
            # Set the temporary password for the user (you may need to handle password hashing if required)
            user.set_password(temporary_password)
            user.save()
            subject="Temporary Password"
            message='Your temporary password is: {}'.format(temporary_password)
            # Send email with temporary password
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email,])
            return JsonResponse({"success":True,"message":"Temporary Password Sent successfully , please check Your email ."})
        else:
            return JsonResponse({"success":False,"message":"No User Found with this email or username"})
    return render(request, 'achievemate/index.html') 
     
 
def about_us(request):
      return render(request,"achievemate/about.html")
 
def our_coach(request):
    context={}
    all_coach_details=AiCoach.objects.all()
    context.update({'all_coach_details':all_coach_details})
    return render(request,"achievemate/our_coach.html",context)
 
def services(request):
      return render(request,"achievemate/services.html")
 
def testimonials(request):
      return render(request,"achievemate/testimonial.html")
 
def subscription(request):
      return render(request,"achievemate/subscription.html")

def find_coach(request):
      return render(request,"achievemate/find_coach.html")
@login_required   
def coach(request):
    context={}
    all_coach_details=AiCoach.objects.all()
    context.update({'all_coach_details':all_coach_details})
    return render(request,"achievemate/dashboard/coach.html",context)
@login_required
def coach_details(request,pk):
    context={}
    coach_data=AiCoach.objects.filter(id=pk)[0]
    context.update({'coach_data':coach_data})
    return render(request,"achievemate/dashboard/coach_details.html",context)

@login_required
def chat_page(request):
    coach_ids = Chat.objects.filter(user=request.user).values('coach_id').annotate(total=Count('coach_id')).values_list('coach_id', flat=True)
    coaches_data = AiCoach.objects.filter(id__in=coach_ids)
    print("current_chatted coaches--->",coaches_data)
    context={}
    context.update({'coaches_data':coaches_data})
    return render(request,"achievemate/dashboard/chat.html",context)



@login_required
def chat(request,uid,cid):
    context={}
    coach_ids = Chat.objects.filter(user=request.user).values('coach_id').annotate(total=Count('coach_id')).values_list('coach_id', flat=True)
    coaches_data = AiCoach.objects.filter(id__in=coach_ids)
    context.update({'coaches_data':coaches_data})
    context.update({'uid':uid,'cid':cid})
    return render(request,"achievemate/dashboard/chat.html",context)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required
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
        # async_to_sync(channel_layer.group_send)(
        #     'chat_%s' % room_id,
        #     {
        #         'type': 'chat_message',
        #         'message': message_text
        #     }
        # )
        return JsonResponse({'status': 'Message sent successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
@login_required  
def get_messages(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    # Retrieve messages from the Chat model
    messages = Chat.objects.filter(is_deleted=0,user_id=uid,coach_id=cid).order_by('created_date')
    print(messages)
    message_texts = [[message.chat_text,message.user_type] for message in messages]
    
    return JsonResponse({'messages': message_texts})

def dashbaord(request):
    return render(request,"achievemate/dashboard/dashboard.html")

def progress_tracking(request):
    return render(request,"achievemate/dashboard/progress_tracking.html")

