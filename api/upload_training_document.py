#!/usr/bin/env python
import requests
import os

def upload_training_document(pdf_path, expert_type):
    """
    Upload a PDF document to train a specific AI coach
    
    Args:
        pdf_path (str): Path to the PDF file
        expert_type (str): One of: life_coaching, parenting_coach, business_idea, career
    """
    
    # API endpoint
    url = "https://api.achievemate.ai/Achievemate/load_expert_document"
    
    # Validate expert type
    valid_types = ['life_coaching', 'parenting_coach', 'business_idea', 'career']
    if expert_type not in valid_types:
        print(f"Error: expert_type must be one of: {valid_types}")
        return
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return
    
    # Prepare the upload
    files = {
        'input_file': open(pdf_path, 'rb')
    }
    
    data = {
        'expert_type': expert_type
    }
    
    try:
        print(f"Uploading {os.path.basename(pdf_path)} for {expert_type}...")
        
        # Send the request
        response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('message', 'Document uploaded successfully')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Upload failed: {e}")
        
    finally:
        files['input_file'].close()

def upload_life_coaching_books():
    """Upload all the life coaching books found in the user's folder"""
    
    base_path = r"C:\Users\bobwa\Dropbox\Coach\Coach Types\Life or Career Coach"
    
    # Key books to upload for life coaching
    books_to_upload = [
        "Atomic_habits_-_James.pdf",
        "Mindset__The_New_Psychology_of_Success_Up_-_Carol_S_Dweck.pdf", 
        "Designing_Your_Life_-_Bill_Burnett.pdf",
        "The_Power_of_Now__A_Guide_to_Spiritual_Enl_-_Eckhart_Tolle.pdf",
        "Start With Why.pdf",
        "Coming Alive -- Barry Michels -- 2017 -- Random House Publishing Group -- 93a40d759dc5bb90023d638fa3e96014 -- Anna's Archive(1).pdf"
    ]
    
    print("Uploading Life Coaching Books to Pinecone Database...")
    print("This will enhance Jacob Jones' knowledge with expert content!\n")
    
    for book in books_to_upload:
        book_path = os.path.join(base_path, book)
        if os.path.exists(book_path):
            print(f"Uploading: {book}")
            upload_training_document(book_path, 'life_coaching')
            print()
        else:
            print(f"File not found: {book}")
    
    print("Life coaching knowledge enhancement complete!")
    print("Jacob Jones now has access to:")
    print("- Habit formation science (Atomic Habits)")
    print("- Growth mindset research (Mindset)")
    print("- Life design methodology (Designing Your Life)")
    print("- Mindfulness coaching (Power of Now)")
    print("- Purpose discovery (Start With Why)")
    print("- Energy management (Coming Alive)")

def main():
    print("=== Training Document Upload Tool ===\n")
    
    print("Available Actions:")
    print("1. Upload all life coaching books")
    print("2. Upload individual book")
    print("\nTo upload all life coaching books, run:")
    print("upload_life_coaching_books()")
    
    # Example usage
    examples = [
        {
            'coach': 'Life Coaching Expert',
            'type': 'life_coaching',
            'suggested_books': [
                'atomic_habits.pdf - Habit formation science',
                'mindset_carol_dweck.pdf - Growth mindset research',
                'designing_your_life.pdf - Life design methodology'
            ]
        },
        {
            'coach': 'Parenting Coach',
            'type': 'parenting_coach', 
            'suggested_books': [
                'whole_brain_child.pdf - Child development neuroscience',
                'how_to_talk_so_kids_listen.pdf - Communication strategies',
                'no_drama_discipline.pdf - Positive discipline methods'
            ]
        },
        {
            'coach': 'Business Expert',
            'type': 'business_idea',
            'suggested_books': [
                'lean_startup.pdf - Startup methodology',
                'good_to_great.pdf - Business strategy',
                'zero_to_one.pdf - Innovation and entrepreneurship'
            ]
        },
        {
            'coach': 'Career Expert', 
            'type': 'career',
            'suggested_books': [
                'what_color_parachute.pdf - Job search strategies',
                'so_good_they_cant_ignore_you.pdf - Career development',
                'designing_your_career.pdf - Career design methods'
            ]
        }
    ]
    
    for example in examples:
        print(f"{example['coach']} ({example['type']}):")
        for book in example['suggested_books']:
            print(f"   - {book}")
        print()
    
    print("Usage Examples:")
    print("1. upload_training_document('atomic_habits.pdf', 'life_coaching')")
    print("2. upload_training_document('whole_brain_child.pdf', 'parenting_coach')")
    print("3. upload_training_document('lean_startup.pdf', 'business_idea')")
    print("4. upload_training_document('what_color_parachute.pdf', 'career')")
    
    print("\nTo use this script:")
    print("1. Get PDF files of expert coaching books")
    print("2. Place them in a folder")
    print("3. Run: upload_training_document('path/to/book.pdf', 'expert_type')")

if __name__ == "__main__":
    main()