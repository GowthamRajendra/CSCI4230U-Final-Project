from flask import request, Blueprint, jsonify, make_response
import requests

from datetime import datetime 

# import models
from models.user_model import User
from models.quiz_model import Quiz
from models.question_model import Question
from models.quiz_model import AnsweredQuestion

# import service functions
from services.auth_service import access_token_required
from services.quiz_service import store_questions, create_quiz_questions

custom_quiz_bp = Blueprint('custom_quiz_bp', __name__)

@custom_quiz_bp.after_request
def cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@custom_quiz_bp.route("/custom-quiz", methods=["POST"])
@access_token_required 
def custom_quiz(user_data):
    print(request.method)
    questions = request.json.get('questions', [])
    title = request.json.get('title', "")

    # store questions in the database (can use same function as random quiz)
    questions = store_questions(questions)

    # create quiz
    quiz = Quiz(title=title, score=0, timestamp=datetime.now(), total_questions=len(questions), questions=questions, user_created=True)
    quiz.save()

    # add quiz to user's created_quizzes
    user = User.objects(pk=user_data['sub']).first()
    user.created_quizzes.append(quiz)
    user.active_quiz = quiz
    user.save()

    # create quiz questions (same function as random quiz)
    quiz_questions = create_quiz_questions(questions)

    return make_response(jsonify(quiz_questions), 200)

@custom_quiz_bp.route("/get-custom-quizzes", methods=["GET"])
@access_token_required
def get_custom_quizzes(user_data):
    quizzes = Quiz.objects(user_created=True)

    results = [
        {
            "title": quiz.title,
            "timestamp": quiz.timestamp,
            "total_questions": quiz.total_questions,
            "questions": create_quiz_questions(quiz.questions)
        } for quiz in quizzes
    ]

    response_data = {
        "quizzes": results
    }

    return make_response(jsonify(response_data), 200)
    