from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return True, ""
    
    user_answers = session.get("user_answers", {})
    
    if 0 <= current_question_id < len(PYTHON_QUESTION_LIST):
        current_question = PYTHON_QUESTION_LIST[current_question_id]
        
        if answer in current_question["options"]:
            user_answers[str(current_question_id)] = answer
            session["user_answers"] = user_answers
            return True, ""
        else:
            return False, "Please select one of the provided options."
    
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1
    
    if next_question_id < len(PYTHON_QUESTION_LIST):
        question_data = PYTHON_QUESTION_LIST[next_question_id]
        
        formatted_question = f"{question_data['question_text']}\n\n"
        for i, option in enumerate(question_data["options"]):
            formatted_question += f"{i+1}. {option}\n"
        
        return formatted_question.strip(), next_question_id
    else:
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("user_answers", {})
    correct_count = 0
    total_questions = len(PYTHON_QUESTION_LIST)
    
    for question_id, user_answer in user_answers.items():
        question_index = int(question_id)
        if question_index < total_questions:
            correct_answer = PYTHON_QUESTION_LIST[question_index]["answer"]
            if user_answer == correct_answer:
                correct_count += 1
    
    percentage = (correct_count / total_questions) * 100
    
    if percentage >= 90:
        feedback = "Amazing! You have a strong hold on Python fundamentals."
    elif percentage >= 70:
        feedback = "Great going! You're familiar with a lot of Python basics. Some more practice and you'll be great."
    elif percentage >= 50:
        feedback = "Not good but not bad either. You currently have a basic understanding of Python."
    else:
        feedback = "You might want to work on revising python fundamentals a bit more."
    
    final_response = f"Quiz finished!\n\nYour score: {correct_count}/{total_questions} ({percentage:.1f}%)\n\n{feedback}"
    
    return final_response