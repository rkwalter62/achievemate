
from django.urls import path
from achievemate_app import views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('login/', views.login_user, name='login'),
    path('forgot_password/', views.forgot_password_user, name='forgot_password'),
    path('accounts/logout/', LogoutView.as_view(), name='google_logout'),
    path('logout/',views.logout_user,name="logout"),
    path('choose-coach/',views.choose_coach,name="choose_coach"),
    path('about_us/', views.about_us, name='about_us'),
    path('our_coach/', views.our_coach, name='our_coach'),
    path('services/', views.services, name='services'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('subscription/', views.subscription, name='subscription'),
    path('find_coach/', views.find_coach, name='find_coach'),
    path('coach/', views.coach, name='coach'),
    path('coach_details/<int:pk>', views.coach_details, name='coach_details'),
    path('profile/', views.profile, name='profile'),
    path('chat_page/', views.chat_page, name='chat_page'),
    path('chat/<int:uid>/<int:cid>', views.chat, name='chat'),
    path('dashbaord/', views.dashbaord, name='dashbaord'),
    path('progress_tracking/', views.progress_tracking, name='progress_tracking'),
    path('get_messages/', views.get_messages, name='get_messages'),
    path('send_message/', views.send_message, name='send_message'),



    # path('google/login/', views.google_signup, name='google_signup'),
]
