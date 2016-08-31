from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import g
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'


# DB connector
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# Query runner
def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Setting up 'sprinter' table if it doesn't exist
def setup_db():
    query_db("""
    CREATE TABLE IF NOT EXISTS sprinter(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        acceptance_criteria TEXT,
        business_value INT,
        estimation FLOAT,
        status TEXT
    )
    """)


# Closing database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# List and basic page
@app.route('/', methods=['GET'])
@app.route('/list', methods=['GET'])
def listing():
    testing_query = query_db("""SELECT * FROM sprinter ORDER BY id ASC""")
    return render_template('list.html', query=testing_query)


# Deleting selected user story - not working
@app.route('/list/<int:story_id>', methods=['GET'])
def deleting_user_story(story_id):
    query_db("DELETE FROM sprinter WHERE id={0}".format(str(story_id)))
    testing_query = query_db("""SELECT * FROM sprinter ORDER BY id ASC""")
    return render_template('list.html', query=testing_query)


# Story page with blank input boxes
@app.route('/story', methods=['GET'])
def template_test():
    return render_template('form.html', title='Add new Story', process='creating')


# Story page with adding new user stories
@app.route('/story', methods=['POST'])
def adding_user_story():
    data = {}
    data["story_title"] = request.form['story_title']
    data["story_content"] = request.form['story_content']
    data["acceptance_criteria"] = request.form['acceptance_criteria']
    data["business_value"] = request.form['business_value']
    data["estimation"] = request.form['estimation']
    data["status"] = request.form['status']

    query = """
            INSERT INTO sprinter (title, content, acceptance_criteria, business_value, estimation, status)
            VALUES ("{story_title}",
                    "{story_content}",
                    "{acceptance_criteria}",
                    "{business_value}",
                    "{estimation}",
                    "{status}")""".format(**data)
    query_db(query)
    return redirect('/')


# Selecting to edit -- not finished
@app.route('/story/<int:story_id>', methods=['GET'])
def selecting_for_edit(story_id):
    query = query_db("""SELECT * FROM sprinter WHERE id={0}""".format(str(story_id)))
    return render_template('form.html', query=query, title='Edit Story', method='post', id=story_id)

# Editing -- not finished
@app.route('/story/<int:story_id>', methods=['POST'])
def editing(story_id):
    updated_user_story = {}
    updated_user_story["story_title"] = request.form['story_title']
    updated_user_story["story_content"] = request.form['story_content']
    updated_user_story["acceptance_criteria"] = request.form['acceptance_criteria']
    updated_user_story["business_value"] = request.form['business_value']
    updated_user_story["estimation"] = request.form['estimation']
    updated_user_story["status"] = request.form['status']
    updated_user_story["id"] = story_id
    query_db("""UPDATE sprinter SET title={0}, content={1},
             acceptance_criteria={2},
             business_value={3},
             estimation={4},
             status={5} WHERE id={6}""".format(**updated_user_story))
    return redirect('/list')


if __name__ == '__main__':
    with app.app_context():
        setup_db()
        app.run(debug=True)