import connection


def get_all_questions():
    return connection.read_file('question')


def get_question_by_id(question_id):
    questions = connection.read_file('question')
    question = [question for question in questions if question['id'] == question_id][0]
    return question


def get_all_answers():
    return connection.read_file('answer')


def get_answers_for_question(question_id):
    answers = get_all_answers()
    answers_for_question = [answer for answer in answers if answer['question_id'] == question_id]

    return answers_for_question