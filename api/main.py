import os
import traceback
from experts import AiExpert, llm
from flask import request, jsonify,Blueprint
from utils import DocumentProcessor, tasks_extractor
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()   

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "langchainvector"

openai_embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
aiexperts_bp = Blueprint("aiexperts", __name__)


@aiexperts_bp.route('/load_expert_document', methods=['POST'])
def load_expert_document():
    global parenting_coach_bot_expert, life_coaching_expert, business_expert, career_expert
    try:
        expert_type = request.form.get('expert_type')
        if expert_type not in ['parenting_coach', 'life_coaching', 'business_idea', 'career']:
            return jsonify({'error': 'Invalid expert type'})

        file = request.files.get('input_file')
        if not file:
            return jsonify({'error': f'No file part for {expert_type}'})

        if file.filename == '':
            return jsonify({'error': f'No selected file for {expert_type}'})

        documents_dir = "documents"
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        file_path = os.path.join(documents_dir, file.filename)
        file.save(file_path)

        document_processor = DocumentProcessor(file_path)
        document_processor.split_text(expert_type)

        return jsonify({'message': f'{expert_type} expert document loaded successfully'})


    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500


@aiexperts_bp.route('/parenting_coach', methods=['POST'])

def parenting_coach_bot_expert():
    question = request.form.get('question')
    if not question:
            return jsonify({'error': 'Invalid input'})
    try:
        parenting_coach = AiExpert(index_name=INDEX_NAME,namespace="Parenting_coach", llm=llm)
        result = parenting_coach.parenting_coach_bot(question)
        return jsonify({'answer': result})

    except Exception as e:
        traceback.print_exc(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@aiexperts_bp.route('/life_coaching_expert', methods=['POST'])
def life_coaching_expert():
    question = request.form.get('question')
    if not question:
            return jsonify({'error': 'Invalid input'})
    try:
        lifecoachExpert = AiExpert(index_name=INDEX_NAME,namespace="Life_coaching_expert", llm=llm)
        result = lifecoachExpert.life_coaching_expert_bot(question)
        return jsonify({'answer': result})

    except Exception as e:
        traceback.print_exc(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@aiexperts_bp.route('/business_expert', methods=['POST'])
def business_expert():
    question = request.form.get('question')
    if not question:
        return jsonify({'error': 'Invalid input'})
    try:
        businessExpert = AiExpert(index_name=INDEX_NAME,namespace="Business_idea_expert", llm=llm)
        result = businessExpert.business_expert_bot(question)
        return jsonify({'answer': result })
    except Exception as e:
        traceback.print_exc(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@aiexperts_bp.route('/Career_expert', methods=['POST'])
def career_expert():
    question = request.form.get('question')
    if not question:
            return jsonify({'error': 'Invalid input'})
    try:
        careerExpert = AiExpert(index_name=INDEX_NAME,namespace="Career_expert", llm=llm)
        result = careerExpert.career_expert_bot(question)
        return jsonify({'answer': result})

    except Exception as e:
        traceback.print_exc(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@aiexperts_bp.route('/task_list', methods=['POST'])   
def task_list():
    txt = request.form.get('answer')
    task_list = tasks_extractor(txt)
    return jsonify({'task_list': task_list})

