from flask import Flask , render_template, redirect, url_for, request
import data_manager
from flask_moment import Moment


app = Flask(__name__)
moment = Moment(app)


@app.route('/')
def index():
    number_of_questions = 5

    questions = data_manager.get_all_questions()
    questions.sort(reverse=True, key=lambda question: question["submission_time"])
    questions = questions[:number_of_questions]

    return render_template('list.html', questions=questions, is_index_page=True)

@app.route('/list')
def show_list():
    questions = data_manager.get_all_questions()
    questions.sort(reverse=True, key=lambda question: question["submission_time"])
    return render_template('list.html', questions=questions)


@app.route('/question/<question_id>')
def show_question(question_id, is_new_answer=False, is_new_comment=False, answer_to_edit=False):
    question = data_manager.get_question_by_id(question_id)
    answers_for_question = data_manager.get_answers_for_question(question_id)
    comments_for_question = data_manager.get_comments(question_id)

    return render_template('maintain-question.html',
                           question=question,
                           answers_for_question=answers_for_question,
                           is_new_answer=is_new_answer,
                           comments_for_question=comments_for_question,
                           is_new_comment=is_new_comment,
                           answer_to_edit=answer_to_edit)


@app.route('/question/<question_id>/new-answer', methods=["GET", "POST"])
def add_new_answer(question_id):
    if request.method == "GET":
        return show_question(question_id, is_new_answer=True)
    elif request.method == "POST":
        data_manager.save_new_answer(request.form.to_dict(), question_id)
        return redirect(url_for("show_question", question_id=question_id))


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    '''GET: Renders the form for the question
    POST: Adds a new question to the database'''
    if request.method == 'GET':
        return render_template('add-question.html', question={})
    elif request.method == 'POST':
        question_id = data_manager.save_new_question(request.form.to_dict())

        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
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


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question_with_answers(question_id)

    return redirect(url_for('show_list'))


@app.route('/question/<question_id>/vote-up', methods=['POST'])
def vote_up(question_id):
    if request.form:
        answer_id = request.form['answer_id']
        data_manager.change_vote('answer', answer_id, 1)
    else:
        data_manager.change_vote('question', question_id, 1)

    return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/vote-down', methods=['POST'])
def vote_down(question_id):
    if request.form:
        answer_id = request.form['answer_id']
        data_manager.change_vote('answer', answer_id, -1)
    else:
        data_manager.change_vote('question', question_id, -1)

    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    data_manager.delete_answer(answer_id)
    question_id = request.form["question_id"]
    return redirect(url_for("show_question", question_id=question_id))


@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def add_new_comment_to_question(question_id):
    if request.method == "GET":
        return show_question(question_id, is_new_comment=True)
    elif request.method == "POST":
        new_comment = request.form.to_dict()
        new_comment["question_id"] = question_id
        new_comment["answer_id"] = None
        data_manager.add_comment(new_comment)
        return redirect(url_for("show_question", question_id=question_id))


@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def add_new_comment_to_answer(answer_id):
    question_id = data_manager.get_answer_by_id(answer_id)['question_id']
    if request.method == "GET":
        return show_question(question_id, is_new_answer_comment=True)
    elif request.method == "POST":
        new_comment = request.form.to_dict()
        new_comment["question_id"] = question_id
        new_comment["answer_id"] = answer_id
        data_manager.add_comment(new_comment)
        return redirect(url_for("show_question", question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = data_manager.get_answer_by_id(answer_id)
    if request.method == "GET":
        return show_question(answer['question_id'], answer_to_edit=answer_id)
    elif request.method == "POST":
        data_manager.save_new_answer(request.form.to_dict(), question_id)
        return redirect(url_for("show_question", question_id=question_id))


@app.route('/search', methods=["GET"])
def search():
    query = request.args or {}
    questions = data_manager.get_filtered_questions({'word': '%{}%'.format(query['q'])})
    questions.sort(reverse=True, key=lambda question: question["submission_time"])
    return render_template('list.html', questions=questions)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
