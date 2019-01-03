from flask import Flask , render_template, redirect, url_for, request, abort, session, make_response
import data_manager
from flask_moment import Moment
import csv
import bcrypt
import os


app = Flask(__name__)
moment = Moment(app)


@app.route('/')
def index():
    logged_in = True if authenticate_user() else False
    number_of_questions = 5

    questions = data_manager.get_all_questions()
    questions.sort(reverse=True, key=lambda question: question["submission_time"])
    questions = questions[:number_of_questions]

    return render_template('list.html', questions=questions, is_index_page=True, logged_in=logged_in)

@app.route('/list')
def show_list():
    logged_in = True if authenticate_user() else False
    first_ordering_attribute = request.args['first_attribute'] if 'first_attribute' in request.args else ''
    second_ordering_attribute = request.args['second_attribute'] if 'second_attribute' in request.args else ''
    questions = data_manager.get_all_questions(first_attribute=first_ordering_attribute, second_attribute=second_ordering_attribute)
    return render_template('list.html', questions=questions, first_ordering_attribute=first_ordering_attribute, second_ordering_attribute=second_ordering_attribute, logged_in=logged_in)


@app.route('/question/<question_id>')
def show_question(question_id,
                  is_new_answer=False,
                  is_new_comment=False,
                  answer_to_edit=False,
                  answer_to_comment=False,
                  show_modal=False,
                  comment_to_edit=None):
    question = data_manager.get_question_by_id(question_id)
    answers_for_question = data_manager.get_answers_for_question(question_id)
    comments_for_question = data_manager.get_comments(question_id)
    comments_for_answers = data_manager.get_comments_for_answers(question_id)
    tags_for_question = data_manager.get_tags_for_question(question_id)
    tags_wo_question = data_manager.get_tags_wo_question(question_id)
    logged_in = True if authenticate_user() else False

    return render_template('maintain-question.html',
                           question=question,
                           answers_for_question=answers_for_question,
                           is_new_answer=is_new_answer,
                           comments_for_question=comments_for_question,
                           comments_for_answers=comments_for_answers,
                           is_new_comment=is_new_comment,
                           answer_to_edit=answer_to_edit,
                           answer_to_comment=answer_to_comment,
                           comment_to_edit=comment_to_edit,
                           tags_for_question=tags_for_question,
                           tags_wo_question=tags_wo_question,
                           show_modal=show_modal,
                           logged_in=logged_in)


# restriction needed
@app.route('/question/<question_id>/new-answer', methods=["GET", "POST"])
def add_new_answer(question_id):
    if authenticate_user():
        if request.method == "GET":
            return show_question(question_id, is_new_answer=True)
        elif request.method == "POST":
            new_answer = request.form.to_dict()
            new_answer['question_id'] = question_id
            data_manager.save_new_answer(new_answer)
            return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    '''GET: Renders the form for the question
    POST: Adds a new question to the database'''
    if authenticate_user():
        if request.method == 'GET':
            return render_template('add-question.html', question={})
        elif request.method == 'POST':
            question_id = data_manager.save_new_question(request.form.to_dict())

            return redirect(url_for('show_question', question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
    if authenticate_user():
        question = data_manager.get_question_by_id(question_id)

        if request.method == "GET":

            return render_template('add-question.html', question=question)
        elif request.method == 'POST':
            updated_details = request.form.to_dict()

            updated_question = {}
            for key in question.keys():
                updated_question[key] = updated_details[key] if key in updated_details else question[key]

            data_manager.update_question(updated_question)

            return redirect(url_for('show_question', question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    if authenticate_user():
        data_manager.delete_question_with_answers(question_id)

        return redirect(url_for('show_list'))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/vote-up', methods=['POST'])
def vote_up(question_id):
    if authenticate_user():
        if request.form:
            answer_id = request.form['answer_id']
            data_manager.change_vote('answer', answer_id, 1)
        else:
            data_manager.change_vote('question', question_id, 1)

        return redirect(url_for('show_question', question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/vote-down', methods=['POST'])
def vote_down(question_id):
    if authenticate_user():
        if request.form:
            answer_id = request.form['answer_id']
            data_manager.change_vote('answer', answer_id, -1)
        else:
            data_manager.change_vote('question', question_id, -1)

        return redirect(url_for('show_question', question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/answer/<answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    if authenticate_user():
        data_manager.delete_answer(answer_id)
        question_id = request.form["question_id"]
        return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def add_new_comment_to_question(question_id):
    if authenticate_user():
        if request.method == "GET":
            return show_question(question_id, is_new_comment=True)
        elif request.method == "POST":
            new_comment = request.form.to_dict()
            new_comment["question_id"] = question_id
            new_comment["answer_id"] = None
            data_manager.add_comment(new_comment)
            return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def add_new_comment_to_answer(answer_id):
    if authenticate_user():
        question_id = data_manager.get_answer_by_id(answer_id)['question_id']
        comments_for_answers = data_manager.get_comments_for_answers(question_id)
        if request.method == "GET":
            return show_question(question_id, answer_to_comment=answer_id)
        elif request.method == "POST":
            new_comment = request.form.to_dict()
            new_comment["question_id"] = question_id
            new_comment["answer_id"] = answer_id
            data_manager.add_comment(new_comment)
            return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
def edit_answer(answer_id):
    if authenticate_user():
        answer = data_manager.get_answer_by_id(answer_id)
        if request.method == "GET":
            return show_question(answer['question_id'], answer_to_edit=answer_id)
        elif request.method == "POST":
            data = request.form.to_dict()
            data['id'] = answer_id
            data_manager.update_answer(data)
            return redirect(url_for("show_question", question_id=answer['question_id']))
    return redirect(url_for('login'))


@app.route('/search', methods=["GET"])
def search():
    query = request.args or {}
    questions = data_manager.get_filtered_questions({'word': '%{}%'.format(query['q'])})
    questions.sort(reverse=True, key=lambda question: question["submission_time"])
    return render_template('list.html', questions=questions)


# restriction needed
@app.route('/comments/<comment_id>/edit', methods=["GET", "POST"])
def edit_comment(comment_id):
    if authenticate_user():
        comment = data_manager.get_comment_by_id(comment_id)
        question_id = comment["question_id"]
        if request.method == "GET":
            return show_question(question_id, comment_to_edit=comment_id)
        elif request.method == "POST":
            data = request.form.to_dict()
            data['id'] = comment_id
            data_manager.update_comment(data)
            return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/new-tag', methods=["POST"])
def add_question_tag(question_id):
    if request.form:
        data = request.form.to_dict()
        tag_id = data_manager.save_new_tag(data['tag_name'], question_id)


# restriction needed
@app.route('/comments/<comment_id>/delete')
def delete_comment(comment_id):
    if authenticate_user():
        question_id = data_manager.delete_comment(comment_id)['question_id']
        return redirect(url_for("show_question", question_id=question_id))
    return redirect(url_for('login'))


# restriction needed
@app.route('/question/<question_id>/new-tag', methods=["POST"])
def edit_question_tag(question_id):
    #data #'id'] = comment_id
    #data_manager.update_comment(data)
    return redirect(url_for("show_question", question_id=question_id, show_modal=True))


def migrate_old_db():
    with open("sample_data/question.csv", "r") as oldie:
        rows = csv.DictReader(oldie)
        for row in rows:
            data_manager.save_new_answer(row)
    with open("sample_data/answer.csv", "r") as oldie:
        rows = csv.DictReader(oldie)
        for row in rows:
            data_manager.save_new_answer(row)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        user_data = request.form.to_dict()
        username = user_data["username"]
        if username in data_manager.get_users_list():
            abort(404)
        else:
            hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
            data_manager.save_new_user(username, hashed_password.decode('utf-8'))
            return redirect(url_for('index'))
    return render_template("registration.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = request.form.to_dict()
        username = user_data['username']
        if username in data_manager.get_users_list():
            user = data_manager.get_user(username)
            if bcrypt.checkpw(user_data['password'].encode('utf-8'), data_manager.get_hashed_password(username).encode('utf-8')):
                session_id = bcrypt.gensalt().decode('utf-8')
                session['session_id'] = session_id
                session['user_id'] = user['id']
                session['role'] = user['role']
                data_manager.save_session(username, session_id)
                return redirect(url_for('index'))
            else:
                render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/check')
def check():
    return '{}'.format(session['session_id'] in data_manager.get_session_ids())


def authenticate_user():
    try:
        if session['session_id'] in data_manager.get_session_ids():
            return True
    except KeyError:
        return False


@app.route('/all-user-info')
def all_user_info():
    all_user_info = data_manager.get_all_user_info()
    return render_template('list_users_info.html', all_user_info=all_user_info)


@app.route('/user-page/<user_id>')
def show_user_page(user_id):
    if authenticate_user():
        user_dependencies = data_manager.get_user_dependencies(user_id)
        return render_template('user-page.html', user_dependencies=user_dependencies)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = os.urandom(16)
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
