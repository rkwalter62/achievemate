# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AchieveMate is a Django-based web application for goal achievement and coaching. It features user authentication, AI coaches, real-time chat, subscription management, and progress tracking.

## Development Commands

### Running the Application
```bash
python manage.py runserver
```

### Database Operations
```bash
# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser
```

### Static Files
```bash
# Collect static files for production
python manage.py collectstatic
```

### Virtual Environment
```bash
# Activate virtual environment (if using venv)
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Architecture

### Core Structure
- **achievemate_project/**: Django project configuration
- **achievemate_app/**: Main application containing models, views, templates
- **templates/achievemate/**: HTML templates organized by feature
- **static/assets/**: CSS, JavaScript, images, and other static files
- **media/**: User-uploaded files (profile pictures, etc.)

### Key Models (achievemate_app/models.py)
- **Users**: Custom user model extending AbstractBaseUser
- **AICoach**: AI coaching profiles with ratings and specializations
- **Chat**: Real-time messaging system
- **Tasks**: User goal tracking and progress
- **Subscription**: Payment and subscription management
- **ActivityLog**: User activity tracking

### Real-time Features
- Uses Django Channels with Redis for WebSocket support
- Chat system with real-time messaging
- ASGI application configured for async support

### Authentication
- Custom user model with email/username login
- Django Allauth integration for social authentication (Google)
- Custom middleware for redirects and session management

### Database
- Currently configured for SQLite (development)
- MySQL configuration available but commented out
- Uses PyMySQL as MySQL adapter

### Frontend
- Bootstrap 4 for styling
- jQuery for JavaScript interactions
- Owl Carousel for image carousels
- Custom CSS in assets/css/

### Key Features
- User registration and authentication
- AI coach selection and interaction
- Real-time chat system with Text-to-Speech responses
- Subscription management with Stripe integration
- Progress tracking and activity logs
- File uploads for profile pictures
- Responsive design

## Voice & Avatar Features

### Text-to-Speech (TTS) Integration ✅ ACTIVE
- **Service**: `achievemate_app/tts_service.py` - Multi-provider TTS service
- **Providers**: Google Cloud TTS, Azure Cognitive Services, VoiceRSS, Browser TTS fallback
- **Voice Mapping**: Different voice types per coach (male/female)
- **Caching**: Generated audio files cached in `/media/coach_audio/`
- **Integration**: WebSocket consumer generates speech for all coach responses
- **Frontend**: Auto-plays audio or uses browser TTS as fallback
- **Cost**: Free with browser TTS, minimal cost with cloud providers

### HeyGen Avatar Integration (Inactive - Requires Paid Subscription)
- **Service**: `achievemate_app/heygen_service.py` - Complete avatar video generation
- **Integration**: WebSocket consumer calls HeyGen API for video responses
- **Frontend**: Chat interface displays avatar videos with autoplay
- **Configuration**: Requires HeyGen API key (paid subscription needed for avatars)
- **Status**: Implementation complete but requires $99/month HeyGen subscription

## Environment Variables Required
- SECRET_KEY: Django secret key
- STRIPE_PUBLIC_KEY: Stripe public key for payments
- STRIPE_SECRET_KEY: Stripe secret key for payments
- Database credentials (if using MySQL):
  - DB_NAME, DB_USER, DB_PASS, DB_HOST
- Voice Features (Optional):
  - HEYGEN_API_KEY: HeyGen avatar service (requires paid subscription)
  - GOOGLE_CLOUD_TTS_API_KEY: Google Text-to-Speech API
  - AZURE_TTS_SUBSCRIPTION_KEY: Azure Cognitive Services TTS
  - AZURE_TTS_REGION: Azure region (default: eastus)
  - VOICERSS_API_KEY: VoiceRSS TTS service

## URLs Structure
- `/`: Homepage
- `/dashboard/`: User dashboard with various subpages
- `/choose_coach/`: Coach selection interface
- `/admin/`: Django admin interface
- Social auth endpoints via django-allauth