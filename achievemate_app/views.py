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
    context={}
    all_coach_details=AiCoach.objects.all()
    context.update({'all_coach_details':all_coach_details})
    print("Session details=> ",dict(request.session))
    auth_user_id = request.session.get('_auth_user_id')  # Fetch _auth_user_id from session details
    print("_auth_user_id:", auth_user_id)
    return render(request,"achievemate/index.html",context)

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

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
def login_user(request):
    if request.method == 'POST':
        usern = request.POST.get('username')
        passw= request.POST.get('password')
        
        try:
            validate_email(usern)
            is_email = True
        except ValidationError:
            is_email = False
        print(is_email)
        if is_email:
            # Try to authenticate using email
            user = authenticate(request, email=usern, password=passw, backend='achievemate_app.backends.EmailOrUsernameModelBackend')
            print("User in email -->",user)
        else:
            # Try to authenticate using username
            user = authenticate(request, username=usern, password=passw, backend='django.contrib.auth.backends.ModelBackend')
            print("User in username -->",user)
        if user is not None:
            if user.is_verified:
                login(request, user)
                return JsonResponse({"success":True})  # Redirect to homepage after successful login
            else:
               return JsonResponse({'error': 'external_account is Inactivated , Please activate your account verifying link sent in you mail'})  # Render account inactive template
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
    # try:
    #     user_subscription = UserStripe.objects.get(user=request.user).plan
    #     print(user_subscription)
    # except UserStripe.DoesNotExist:
    #     pass
    # if user_subscription.subscription_package.package_name == 'Essential Plan':
    #     all_coach_details=AiCoach.objects.all()[:1]  # Access to 1 coach
    # if user_subscription.subscription_package.package_name == 'Achievement Accelerator':
    #     all_coach_details=AiCoach.objects.all()[:2]  # Access to 1 coach
    # if user_subscription.subscription_package.package_name == 'Professional (for Licensed coaches and Therapists)':
    #     all_coach_details=AiCoach.objects.all()  # Access to 1 coach
    all_coach_details=AiCoach.objects.all()
    context.update({'all_coach_details':all_coach_details})
    return render(request,"achievemate/our_coach.html",context)
 
def services(request):
      return render(request,"achievemate/services.html")
 
def testimonials(request):
      return render(request,"achievemate/testimonial.html")
 
def subscription(request):
    context = {}
    subscriptions = Subscription.objects.all()
    packages = SubscriptionPackage.objects.filter(subscription__in=subscriptions).distinct()
    features = SubscriptionFeatures.objects.filter(subscription_package__in=packages).distinct()

    context.update({'subscriptions': subscriptions, 'packages': packages, 'features': features})
    return render(request,"achievemate/subscription.html",context)
@login_required
def find_coach(request):
    if request.method == 'POST':
        # Loop through the submitted data to extract answers
        for key, value in request.POST.items():
            if key.startswith('answer_'):
                question_id = key.split('_')[1]
                # Create UserAnswer object and save to the database
                user_answer = UserAnswer.objects.create(user=request.user, question_id=question_id, answer=value)
                user_answer.save()
        return redirect('find_coach')  # Redirect to a success page
    else:
        context={}
        questions = FindCoachQuestions.objects.all()
        context.update({'questions' : questions})
    return render(request,"achievemate/find_coach.html",context)
@login_required   
def coach(request):
    context={}
    search_query = request.GET.get('search', '')
    if search_query:
        all_coach_details = AiCoach.objects.filter(
            Q(coach_name__icontains=search_query) |  
            Q(coach_expertise__icontains=search_query) |  
            Q(coach_experience__icontains=search_query) |  
            Q(coach_degree__icontains=search_query) |  
            Q(coaching_types__icontains=search_query) |  
            Q(target_audience__icontains=search_query) |  
            Q(languages__icontains=search_query) |  
            Q(specialities__icontains=search_query) |  
            Q(coach_about__icontains=search_query)  
        )
        context.update({'all_coach_details' : all_coach_details})
    else:
        try:
            user_subscription = UserStripe.objects.get(user=request.user).plan
            print(user_subscription)
        except UserStripe.DoesNotExist:
            return []
        if user_subscription.subscription_package.package_name == 'Essential Plan':
            all_coach_details=AiCoach.objects.all()[:1]  # Access to 1 coach
        if user_subscription.subscription_package.package_name == 'Achievement Accelerator':
            all_coach_details=AiCoach.objects.all()[:2]  # Access to 1 coach
        if user_subscription.subscription_package.package_name == 'Professional (for Licensed coaches and Therapists)':
            all_coach_details=AiCoach.objects.all()  # Access to 1 coach
        # all_coach_details=AiCoach.objects.all()
        context.update({'all_coach_details':all_coach_details})
    return render(request,"achievemate/dashboard/coach.html",context)

# @login_required
def coach_details(request,pk):
    context={}
    coach_data=AiCoach.objects.filter(id=pk)[0]
    context.update({'coach_data':coach_data})
    return render(request,"achievemate/dashboard/coach_details.html",context)

def simple_coach_details(request,pk):
    context={}
    coach_data=AiCoach.objects.filter(id=pk)[0]
    context.update({'coach_data':coach_data})
    return render(request,"achievemate/dashboard/simple_coach_details.html",context)

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
# @login_required  
# def get_messages(request):
#     uid = request.GET.get('uid')
#     cid = request.GET.get('cid')
#     # Retrieve messages from the Chat model
#     messages = Chat.objects.filter(is_deleted=0,user_id=uid,coach_id=cid).order_by('created_date')
#     print(messages)
#     message_texts = [[message.chat_text,message.user_type] for message in messages]
    
#     return JsonResponse({'messages': message_texts})
from django.shortcuts import get_object_or_404
from .models import Chat, Users, UserProfile, AiCoach
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_messages(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    try:
        current_coach=AiCoach.objects.get(id=cid)
    except:
        return JsonResponse({'None': None})
    # Retrieve messages from the Chat model
    messages = Chat.objects.filter(is_deleted=0, user_id=uid, coach_id=cid).order_by('created_date')
    if messages.count()==0:
        if current_coach.coach_expertise=="Life Coaching Experts":
            introductory_message=f"Welcome to Life Guidance with {current_coach.coach_name}! Here to support you on your journey towards personal growth and fulfillment. Feel free to ask any questions or share your concerns. Let's embark on this journey together."
        elif current_coach.coach_expertise=="Parenting Coach":
            introductory_message=f"Welcome to Parenting Pathways with {current_coach.coach_name}! I'm thrilled to be your guide as you navigate the beautiful and rewarding journey of parenthood. Whether you're seeking advice on nurturing strong family bonds, managing the ups and downs of raising children, or simply looking for a supportive ear, you're in the right place. Feel free to share your questions, joys, and concerns – together, we'll navigate this adventure with compassion, understanding, and a commitment to fostering harmony and joy in your family. Let's embark on this enriching journey together, one step at a time."
        elif current_coach.coach_expertise=="Business Idea Experts":
            introductory_message=f"Welcome to Business Insight with {current_coach.coach_name}! Here to help you brainstorm innovative ideas and strategize for success in your ventures. Let's unlock your entrepreneurial potential together."
        elif current_coach.coach_expertise=="Career Experts":
            introductory_message=f"Welcome to Career Compass with {current_coach.coach_name}! Here to guide you towards a fulfilling and successful career path. Let's explore your professional goals and aspirations together."
        
        chat = Chat.objects.create(
            chat_text=introductory_message,
            user_type='coach',
            user_id=uid,
            coach_id=cid
        )
    messages = Chat.objects.filter(is_deleted=0, user_id=uid, coach_id=cid).order_by('created_date')
    message_texts = []
    
    for message in messages:
        if message.user_type == 'user':
            user = get_object_or_404(Users, id=uid)
            user_profile = get_object_or_404(UserProfile, user_id=uid)
            user_data = {
                # 'type': 'user',
                # 'firstname': user_profile.firstname,
                # 'lastname': user_profile.lastname,
                'profilepic': str(user_profile.profilepic.url),
                # 'email': user.email,
                # 'role': user.role,
                # 'user_type': user.user_type,
                # 'google_id': user.google_id,
                # Add other user fields here
            }
            message_texts.append([message.chat_text, message.user_type,message.created_date.strftime("%d-%m-%Y %I:%M %p"), user_data,message.id])
        elif message.user_type == 'coach':
            coach = get_object_or_404(AiCoach, id=cid)
            coach_data = {
                # 'type': 'coach',
                # 'coach_name': coach.coach_name,
                # 'coach_expertise': coach.coach_expertise,
                # 'coach_experience': coach.coach_experience,
                # 'coach_about': coach.coach_about,
                # 'coach_degree': coach.coach_degree,
                'coach_profile_image': str(coach.coach_profile_image.url),
                # 'coaching_types': coach.coaching_types,
                # 'target_audience': coach.target_audience,
                # 'specialities': coach.specialities,
                # 'languages': coach.languages,
                # 'rating': str(coach.rating),
                # Add other coach fields here
            }
            message_texts.append([message.chat_text, message.user_type,message.created_date.strftime("%d-%m-%Y %I:%M %p"), coach_data, message.id])

    return JsonResponse({'messages': message_texts})

def dashboard(request):
    all_coach_ids = Tasks.objects.filter(user_id=request.user).values_list('coach_id', flat=True).distinct()
    print("All coach ID ", all_coach_ids)
    all_coaches = AiCoach.objects.filter(id__in=all_coach_ids)
    all_tasks_collection = []
    for one_id in all_coach_ids:
        all_tasks_coach = Tasks.objects.filter(coach_id=one_id)
        for task in all_tasks_coach:
            if task.due_date < timezone.now() and task.task_status != 'Delayed':
                task.task_status = 'Delayed'
                task.save()
                # Create Activity_Log object
                activity_type_label = dict(Activity_Log.ACTIVITY_TYPE_CHOICES).get('task_delayed', '')
                activity_log = Activity_Log.objects.create(
                    user=request.user,
                    tasks=task,
                    coach_id=task.coach.id,
                    activity_type='task_delayed',
                    notification_comment=f"You have marked {activity_type_label} for {task.coach.coach_name}"
                )
        all_tasks_collection.append(all_tasks_coach)
    # print(all_tasks_collection)
    context = {
        'all_tasks_collection': all_tasks_collection,
        'all_coaches': all_coaches,
    }
    
    return render(request,"achievemate/dashboard/dashboard.html",context)
from django.core import serializers

def load_activity_log(request, task_id):
    # Retrieve the activity log for the specified task
    task=Tasks.objects.get(id=task_id)
    activity_logs= Activity_Log.objects.filter(tasks=task,user=request.user)
    # Serialize the data for activity logs
    activity_log_data = serializers.serialize('json', activity_logs)

    # Serialize the data for the task
    task_data = serializers.serialize('json', [task, ])

    # Serialize the data for users related to the activity logs
    user_ids = list(activity_logs.values_list('user', flat=True))
    users = Users.objects.filter(id__in=user_ids)
    user_data = serializers.serialize('json', users)
    comments = Task_Comments.objects.filter(tasks=task)
    comment_data = serializers.serialize('json', comments)
    # Construct the JSON response
    response_data = {
        'activity_log_data': activity_log_data,
        'task_data': task_data,
        'user_data': user_data,
        'comment_data': comment_data,
    }

    # Return the JSON response
    return JsonResponse(response_data)

def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('new_status')
        
        # Update task status in the database
        task = Tasks.objects.get(pk=task_id)
        task.task_status = new_status
        task.save()
        if new_status == "In Progress":
            activity="task_in_progress"
        elif new_status=="Done":
            activity='task_completed'
        elif new_status=="Remaining":
            activity='task_remaining'
        elif new_status=="Delayed":
            activity='task_delayed'
         # Retrieve the corresponding notification comment
        activity_type_label = dict(Activity_Log.ACTIVITY_TYPE_CHOICES).get(activity, '')
        activity_log=Activity_Log.objects.create(
            user = request.user,
            tasks=task,
            coach_id= task.coach.id,
            activity_type = activity,
            notification_comment= f"You have mark {activity_type_label} for {task.coach.coach_name}"
        )
        # print("Task saved in update task status---> ",task)
        return JsonResponse({"success":True,'message': f'{activity_log.notification_comment}'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def progress_tracking(request):
    context={}
    
    user_total_tasks = Tasks.objects.filter(user=request.user)
    remaining_tasks = user_total_tasks.filter(task_status='Remaining').count()
    delayed_tasks = user_total_tasks.filter(task_status='Delayed').count()
    in_progress_tasks = user_total_tasks.filter(task_status='In Progress').count()
    done_tasks = user_total_tasks.filter(task_status='Done').count()
    # Calculate total number of tasks
    total_tasks_count = user_total_tasks.count()
    
    # Calculate percentage of each task status
    remaining_tasks_percentage = (remaining_tasks / total_tasks_count) * 100 if total_tasks_count != 0 else 0
    delayed_tasks_percentage = (delayed_tasks / total_tasks_count) * 100 if total_tasks_count != 0 else 0
    in_progress_tasks_percentage = (in_progress_tasks / total_tasks_count) * 100 if total_tasks_count != 0 else 0
    done_tasks_percentage = (done_tasks / total_tasks_count) * 100 if total_tasks_count != 0 else 0
    
    # Update context with counts and percentages
    context.update({
        'remaining_tasks': remaining_tasks,
        'delayed_tasks': delayed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'remaining_tasks_percentage': remaining_tasks_percentage,
        'delayed_tasks_percentage': delayed_tasks_percentage,
        'in_progress_tasks_percentage': in_progress_tasks_percentage,
        'done_tasks_percentage': done_tasks_percentage,
    })
    coach_status_data = {}
    # Fetch coach-wise tasks status percentages
    coaches = AiCoach.objects.all()
    for coach in coaches:
        tasks_count = Tasks.objects.filter(coach=coach,user=request.user).values('task_status').annotate(count=Count('id'))
        total_tasks = sum([count['count'] for count in tasks_count])
        percentages = {status['task_status']: (status['count'] / total_tasks) * 100 for status in tasks_count}
        coach_status_data[coach.coach_name] = percentages

    # Prepare data for chart
    labels = list(coach_status_data.keys())
    datasets = []
    status_colors = {
        'Remaining': 'rgba(255,231,140,0.7)',  # Adjusted alpha value for a darker shade
        'In Progress': 'rgba(0,149,255,0.7)',
        'Done': 'rgba(66,189,83,0.7)',
        'Delayed': 'rgba(255,102,102,0.7)' ,
    }
    for status in ['Remaining', 'In Progress', 'Done', 'Delayed']:
        dataset = {
            'label': status,
            'backgroundColor': status_colors[status],
            'data': []
        }
        for coach, percentages in coach_status_data.items():
            dataset['data'].append(percentages.get(status, 0))
        datasets.append(dataset)

    # Pass data to template
    chart_data = { 
        'labels': labels,
        'datasets': datasets
    }
    context.update({'chart_data': chart_data})
    return render(request,"achievemate/dashboard/Progress_Tracking.html",context)

import requests
from datetime import datetime,timedelta
import re
def get_task(request):
    # try:
        url = "https://api.achievemate.ai/Achievemate/task_list"
        # url="http://127.0.0.1:5000/Achievemate/task_list"
        answer=request.POST.get("answer","")
        chat_id=request.POST.get("chat_id","")
        payload = {'answer': answer}
        files=[]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        # print("response--->",response.json()["task_list"])
        chat_data=Chat.objects.filter(id=int(chat_id))[0]
        tasks=response.json()["task_list"]
        # print("Tasks--->",tasks)
        
        # tasks = re.split(r'\n(?=\d+\.)', tasks.strip())
        # tasks = [task.strip() for task in tasks if task.strip()]
        tasks=separate_tasks(tasks)
        tasks = tasks.split('\n')
        chat_tasks=Tasks.objects.filter(chat=chat_data).count()
        if chat_tasks == 0:
        # print("Tasks fetched from api ,", tasks)
        # print("tasks after spliiting from numbers--->",tasks)
            for task in tasks:
                if task != "Task List:":
                    created_task=Tasks.objects.create(
                        chat =chat_data,
                        user_id = chat_data.user_id,
                        coach_id =chat_data.coach_id,
                        task_title = str(task).capitalize(),
                        task_status = "Remaining",
                        due_date =  datetime.now() + timedelta(weeks=2)
                    )
                    activity_log=Activity_Log.objects.create(
                        user = request.user,
                        tasks=created_task,
                        coach_id= chat_data.coach_id,
                        activity_type = "task_cretated",
                        notification_comment= f"Task Added for coach {chat_data.coach.coach_name}"
                    )
        return JsonResponse({'success':True,"task_list":response.json()["task_list"],"message":f"{activity_log.notification_comment}"})
    # except:
        return JsonResponse({'success':False,"message":"Task List Coudn't be fetched, Please Try Again later"})
def add_comment(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        comment_text = request.POST.get('comment')
        
        if task_id and comment_text:
            # Get the task object
            try:
                task = Tasks.objects.get(pk=task_id)
            except Tasks.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Task does not exist'})
            
            # Create the comment
            comment = Task_Comments.objects.create(tasks=task, user=request.user, text=comment_text)
            activity_log=Activity_Log.objects.create(
                        user = request.user,
                        tasks=task,
                        coach_id= task.coach_id,
                        activity_type = "comment_added",
                        notification_comment= f"Commented on Task"
                    )
            return JsonResponse({'success': True, 'comment_id': comment.id})
        else:
            return JsonResponse({'success': False, 'error': 'Incomplete data'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
def separate_tasks(text: str) -> list:
    separated_text = re.sub(r'\d+\.', '', text)
    
    # Remove leading and trailing whitespace and replace empty lines with hyphens
    separated_text = '\n'.join(line.strip() for line in separated_text.split('\n') if line.strip())
    return separated_text

def paymentsuccess(request):
    session_id=request.GET.get("session_id")
    session_obj=stripe.checkout.Session.retrieve(session_id)
    user=User.objects.get(id=session_obj.metadata.user_id)
    active=1 if session_obj["status"]=="complete" else 0
    print("user is--active is ",user,active)
    session_details=stripe.checkout.Session.retrieve(session_id)
    print("Sessison_details",session_details)
    user_stripe_obj=None
    if UserStripe.objects.filter(user=user).exists():
        user_stripe_obj = UserStripe.objects.get(user=user)
        user_stripe_obj.is_active = 1
        user_stripe_obj.plan = session_obj['metadata']['plan_id']
        user_stripe_obj.save()
    return render(request,"achievemate/success.html")
    
def paymentfailure(request):
    print("Request of success page-->",request.GET.get("session_id"))
    session_id=request.GET.get("session_id")
    session_obj=stripe.checkout.Session.retrieve(session_id)
    user=User.objects.get(id=session_obj.metadata.user_id)
    active=1 if session_obj["status"]=="complete" else 0
    print("user is--active is ",user,active)
    session_details=stripe.checkout.Session.retrieve(session_id)
    print("Sessison_details",session_details)
    if UserStripe.objects.filter(user=user).exists():
        user_stripe_obj = UserStripe.objects.get(user=user)
        user_stripe_obj.is_active = 0
        user_stripe_obj.plan = session_obj['metadata']['plan_id']
        user_stripe_obj.save()
    
    # Payment.objects.create(               
    #             user = Users.objects.get(id=session_details["client_reference_id"]),
    #             amount =session_details["amount_total"]/100,
    #             payment_date = timezone.now(),
    #             status ='Failed',
    #         ) 
    return render(request,"achievemate/cancel.html")
    
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.contrib.sites.shortcuts import get_current_site
# @login_required
# views.py
def create_stripe_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success":"Not login","msg":"Please Login first"})
    if request.method == 'POST':
        current_site = get_current_site(request)
        domain_url = f"{current_site}/"
        current_user=User.objects.get(id=request.user.id)
        user_stripe = UserStripe.objects.filter(user=current_user)   
        print("Existsing user in stripe-->",user_stripe)
        price_id = request.POST.get('price_id')  # Assuming you pass the price_id from the frontend
        chosen_subscription=Subscription.objects.filter(id=price_id)[0]
        if user_stripe:
            user_stripe=user_stripe[0]
            print("User Exists in stripe")
            return JsonResponse({"success":False,"msg":"Already Subscribed, You can upgrade your subscription"})
        else:
            print("User not exists in Stripe")
            response=stripe.Customer.create(
                name=request.user.username,
                email=request.user.email,
                metadata={"User_id":request.user.id,"plan_id":chosen_subscription.id}
            )
            # print("Stripe Customer create Response==>",response)
            user_stripe=UserStripe.objects.create(
                stripe_customer_id=response.id,
                user=request.user,
                plan=None,
                is_active=0
                )
            print("customer Created in database")
            try:
                session = stripe.checkout.Session.create(
                    line_items=[{
                        'price': chosen_subscription.stripe_price_id,
                        'quantity': 1,
                    }],
                    client_reference_id=request.user.id,
                    metadata={"user_id":request.user.id,"user_stripe":user_stripe.id,"plan_id":chosen_subscription.id},
                    mode='subscription',
                    customer=user_stripe.stripe_customer_id,
                    success_url=domain_url+'paymentsuccess?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url+'paymentfailure',
                    # success_url='https://achievemate.ai/paymentsuccess/',
                    # cancel_url='https://achievemate.ai/paymentfailure/',  
                )
            # print(session)
                return JsonResponse({"success":True,'sessionurl': session.url})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_stripe_transaction_history(request):
    user_id = request.POST.get('id')
    users = Users.objects.filter(pk=user_id)
    if users.exists():
        print("User_Exists")
        subscription_record = UserStripe.objects.filter(user=users[0])
        subscription_history = []
        if subscription_record.exists():
            customer = stripe.Customer.retrieve(subscription_record[0].stripe_customer_id)
            subscription_history = stripe.Invoice.list(customer=customer)
        context = {'subscription_history': subscription_history, 'subscription_record': list(subscription_record.values()), 'message': 'user_found'}
    else:
        context = {'subscription_history': None, 'subscription_record': None, 'message': 'user_not_found'}
    return JsonResponse(context)

@csrf_exempt
def delete_subscription(request):
    user = Users.objects.get(pk=request.POST.get('id'))
    customer = UserStripe.objects.get(user=user)
    stripe_subscriptions = stripe.Subscription.list(customer=customer.stripe_customer_id, price=request.POST.get('price_id'))
    response = stripe.Subscription.cancel(stripe_subscriptions['data'][0]['id'])
    if response['status'] == 'canceled':
        customer.is_active = 0
        customer.save()
        context = {"message": "SUCCESS"}
    else:
        context = {"message": "ERROR"}
    return JsonResponse(context)

@csrf_exempt
def upgrade_subscription(request):
    try:
        user = Users.objects.get(pk=request.POST.get('id'))
        subscription_obj = UserStripe.objects.get(user = user)
        subscriptions = stripe.Subscription.list(customer=f'{subscription_obj.stripe_customer_id}')
        respponse = stripe.Subscription.modify(
                                    f"{subscriptions['data'][0]['id']}",
                                    items=[{"id": f"{subscriptions['data'][0]['items']['data'][0]['id']}", "price": f"{request.POST.get('price_id')}"}],
                                    )
        # if respponse['data']['items']['data'][0]['plan']['amount'] == 19900:
        #     subscription_obj.plan = 'GOLD'
        #     subscription_obj.save()
        # else:
        #     subscription_obj.plan = 'BRONZE'
        #     subscription_obj.save()

        context = {"message": "SUCCESS"}
    except Exception as e:
        print(e)
        context = {"message": "ERROR"}
    return JsonResponse(context)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY
# Replace this endpoint secret with your endpoint's unique secret
# If you are testing with the CLI, find the secret by running 'stripe listen'
# If you are using an endpoint defined with the API or dashboard, look in your webhook settings
# at https://dashboard.stripe.com/webhooks
# endpoint_secret = 'whsec_1aaeb34af8759a5f7f300c19e9577326c30f977d7f492006954a6ecfdc708871'
endpoint_secret='we_1PRBldCaOQJF93hZG6r23GNh'
from django.utils import timezone
@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        payload = request.body
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, request.META.get('HTTP_STRIPE_SIGNATURE'), endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return JsonResponse({'error': str(e)}, status=400)
        # print("EVENT==",event)
        # Handle the event
        if event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.created':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.partially_funded':
            payment_intent = event['data']['object']
        elif event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # user_id=event['data']['object']["metadata"]["user_id"]
            # print("User_id is --->",user_id)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']   
        else:
            print('Unhandled event type {}'.format(event['type']))
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
