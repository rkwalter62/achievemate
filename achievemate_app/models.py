from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone

# Create your models here.
class BaseModel(models.Model):
    TEST_DATA_CHOICES = (('0', 'no'), ('1', 'yes'),('2', 'default'))
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_testdata = models.CharField(max_length=1,default='1',choices=TEST_DATA_CHOICES,blank=True, null=True)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
class SubscriptionPackage(BaseModel):
    package_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'subscription_package'
class SubscriptionFeatures(BaseModel):
    subscription_package = models.ForeignKey(SubscriptionPackage, models.CASCADE, blank=True, null=True)
    feature_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed =True
        db_table = 'subscription_features'
class Subscription(BaseModel):
    subscription_package = models.ForeignKey(SubscriptionPackage, models.DO_NOTHING, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    class Meta:
        managed =True
        db_table = 'subscription'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(email=email, username=username, **extra_fields)
        # user.set_password(password)
        user.password=make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(email, username, password, **extra_fields)

class Users(BaseModel,AbstractBaseUser, PermissionsMixin):
    email = models.EmailField()
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  
    role = models.CharField(max_length=255, choices=[('coach', 'coach'), ('user', 'user')], default='user')
    user_type = models.CharField(max_length=255, choices=[('standard', 'standard'), ('google', 'google')], default='standard')
    google_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_package =  models.ForeignKey(Subscription, models.DO_NOTHING, blank=True, null=True)
    subscription_status = models.CharField(max_length=255, choices=[('active', 'active'), ('inactive', 'inactive')], default='inactive')
    subscription_expiry = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups'  # Changed related_name for groups field
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions'  # Changed related_name for user_permissions field
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    class Meta:
        managed = True
        db_table = 'users'

class UserProfile(BaseModel):
    firstname = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
    profilepic = models.FileField(upload_to='user_profile_pic/',blank=True, null=True,default='user_profile_pic/anonymous.png')
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_profile'


class AiCoach(BaseModel):
    coach_name = models.CharField(max_length=255, blank=True, null=True)
    coach_expertise = models.CharField(max_length=255, blank=True, null=True)
    coach_experience = models.CharField(max_length=255, blank=True, null=True)
    coach_about = models.TextField(blank=True, null=True)
    coach_degree = models.CharField(max_length=255, blank=True, null=True)
    coach_profile_image =models.FileField(upload_to='coach_profile_pic/',blank=True, null=True)
    coaching_types = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    specialities = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ai_coach'

class Chat(BaseModel):
    USER_TYPE_CHOICES = [
        ('coach', 'coach'),
        ('user', 'user'),
    ]
    chat_text = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES,blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    coach = models.ForeignKey('AiCoach', models.DO_NOTHING,blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'chat'



class FindCoachQuestions(BaseModel):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'MCQ'),
        ('textual', 'Textual'),
    ]
    question = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=7,choices=QUESTION_TYPE_CHOICES, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'find_coach_questions'

class UserAnswer(BaseModel):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey('FindCoachQuestions', models.DO_NOTHING, blank=True, null=True)
    answer = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_answer'

        
class Tasks(BaseModel):
    TASK_STATUS_CHOICES = [
        ('started', 'started'),
        ('in_progress', 'in_progress'),
        ('need_attention', 'need_attention'),
        ('completed', 'completed'),
    ]
    chat = models.ForeignKey('Chat', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    coach = models.ForeignKey('AiCoach', models.DO_NOTHING,blank=True, null=True)
    task_title = models.TextField(max_length=255, blank=True, null=True)
    task_status = models.CharField(max_length=14, choices=TASK_STATUS_CHOICES,blank=True, null=True,default="started")
    due_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tasks'
