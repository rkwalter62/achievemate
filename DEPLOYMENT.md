# AchieveMate Deployment Guide

## Repository Structure
```
achievemate_project/          # Main Django application
├── achievemate_app/         # Django app with frontend
├── api/                     # AI coaching backend (experts.py)
├── media/                   # User uploads and generated audio
└── staticfiles/            # Static assets
```

## Configuration Management Workflow

### 1. Local Development
```bash
# Work in main project directory
cd C:\Users\bobwa\Dropbox\Achievemate-Full\achievemate_project

# Make changes to coaching prompts
# Edit: api/experts.py

# Test locally first
python manage.py runserver
```

### 2. Committing Changes
```bash
# Check what changed
git status

# Stage important files (exclude temp files)
git add api/experts.py
git add other_changed_files

# Commit with descriptive message
git commit -m "Update coaching prompts with new features

- Brief description of changes
- Why the changes were made

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### 3. Deploying to Production Server

#### API Updates (experts.py)
```bash
# Copy updated file to server
scp -i ai_extert.pem api/experts.py ubuntu@api.achievemate.ai:/var/www/html/achievemate_api/

# SSH into server and restart API
ssh -i ai_extert.pem ubuntu@api.achievemate.ai
cd /var/www/html/achievemate_api
sudo pkill -f 'gunicorn.*9001'
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:9001 wsgi:app --timeout 400 &
```

#### Django App Updates
```bash
# SSH into server
ssh -i ai_extert.pem ubuntu@api.achievemate.ai

# Pull latest changes
cd /var/www/html/AI_Extert
git pull origin main

# Restart services
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

## Key Files to Track

### Critical for Coaching Quality
- `api/experts.py` - All coaching prompts and personalities
- `api/upload_training_document.py` - Document upload tools
- `api/utils.py` - Pinecone integration and document processing

### Django Application  
- `achievemate_app/views.py` - Main application logic
- `achievemate_app/consumers.py` - WebSocket handling
- `achievemate_app/tts_service.py` - Text-to-speech integration
- `settings.py` - Configuration

## Environment Variables
Ensure these are set on production:
- `OPENAI_API_KEY` - For TTS and AI responses
- `PINECONE_API_KEY` - For knowledge base
- Database credentials
- Django secret key

## Testing Deployment
1. Test each coach type after deployment
2. Verify TTS audio is working
3. Check that coaches remember conversation history
4. Ensure coaches provide balanced responses (questions + insights + action)

## Rollback Strategy
If deployment issues occur:
```bash
# Revert to previous commit
git reset --hard HEAD~1
git push --force origin main

# Or restore previous experts.py
scp -i ai_extert.pem backup/experts.py ubuntu@api.achievemate.ai:/var/www/html/achievemate_api/
```

## Coach Configuration Summary
- **Dr. Sarah Johnson**: Life Coach (life_coaching_expert_bot)
- **Jacob Jones**: Career Expert (career_expert_bot) 
- **Dr. Amelia Smith**: Parenting Coach (parenting_coach_bot)
- **Michael Williams**: Business Expert (business_expert_bot)

All coaches use balanced approach: Discovery → Insight → Action → Accountability