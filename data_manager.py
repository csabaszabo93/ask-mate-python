import connection
import uuid
import time


def get_all_questions():
    return connection.read_file('question')


def get_question_by_id(question_id, convert_stamp = True):
    questions = connection.read_file('question', convert_stamp)
    question = [question for question in questions if question['id'] == question_id][0]
    return question


def get_answer_by_id(answer_id, convert_stamp = True):
    answers = connection.read_file('answer', convert_stamp)
    answer = [answer for answer in answers if answer['id'] == answer_id][0]
    return answer


def get_all_answers():
    return connection.read_file('answer')


def get_answers_for_question(question_id):
    answers = get_all_answers()
    answers_for_question = [answer for answer in answers if answer['question_id'] == question_id]

    return answers_for_question


def save_new_question(new_question):
    new_question['id'] = str(uuid.uuid4())
    new_question['submission_time'] = str(int(time.time()))
    new_question['view_number'] = 0
    new_question['vote_number'] = 0
    connection.add_new_data(new_question, 'question')

    return new_question['id']


def save_new_answer(new_answer, question_id):
    new_answer['id'] = str(uuid.uuid4())
    new_answer['submission_time'] = str(int(time.time()))
    new_answer['vote_number'] = 0
    new_answer['question_id'] = question_id
    connection.add_new_data(new_answer, 'answer')


def update_question(updated_question):
    questions = connection.read_file('question', convert_stamp=False)
    updated_questions = [question if question['id'] != updated_question['id'] else updated_question for question in questions ]
    connection.rewrite_data(updated_questions, 'question')


def delete_answer(answer_id):
    delete_data("answer", answer_id, False)


def delete_question_with_answers(question_id):
    delete_data('answer', question_id)
    delete_data('question', question_id)


def delete_data(type, id, is_more=True):
    all_data = connection.read_file(type, convert_stamp=False)

    data_to_keep = [data for data in all_data if data['question_id' if type == 'answer' and is_more else 'id'] != id]
    connection.rewrite_data(data_to_keep, type)


def change_vote(type, id, change=0):
    all_data = connection.read_file(type, convert_stamp=False)
    user_input = get_answer_by_id(id, False) if type == 'answer' else get_question_by_id(id, False)
    user_input['vote_number'] += change

    updated_data = [user_input if data['id'] == id else data for data in all_data]
    connection.rewrite_data(updated_data, type)
