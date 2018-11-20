from flask import Flask , render_template
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def show_list():
    questions = data_manager.read_file("question")
    return render_template('list.html', questions=questions)



if __name__ == '__main__':
    app.run(debug=True)