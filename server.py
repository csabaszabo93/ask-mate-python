from flask import Flask , render_template
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def show_list():
    questions = data_manager.get_all_questions()
    return render_template('list.html', questions=questions)


@app.route('/question/<question_id>')
def show_question(question_id):
    question = data_manager.get_question_by_id(question_id)
    answers_for_question = data_manager.get_answers_for_question(question_id)

    return render_template('maintain-question.html',
                           question=question,
                           answers_for_question=answers_for_question)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )