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


# List page
@app.route("/", methods=['GET'])
def index():
    testing_query = query_db("SELECT * FROM sprinter ORDER BY id ASC")
    return render_template('list.html', query=testing_query)


# Deleting selected user story - not working
@app.route("/list", methods=['POST'])
def deleting_user_story(story_id):
    query_db("""DELETE FROM sprinter WHERE id=?""" + str(story_id))
    return redirect('/')


# Story page with blank input boxes
@app.route('/story', methods=['GET'])
def template_test():
    return render_template('form.html')


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


# Editing selected user stories
@app.route('/story/<int:story_id>', methods=['GET', 'POST'])
def selecting_for_edit(story_id):
    if request.method == 'GET':
        query = query_db("SELECT * FROM sprinter WHERE id = " + str(story_id))
        return render_template('form.html', query=query)
    elif request.method == 'POST':
        updated_user_story = {}
        updated_user_story["story_title"] = request.form['story_title']
        updated_user_story["story_content"] = request.form['story_content']
        updated_user_story["acceptance_criteria"] = request.form['acceptance_criteria']
        updated_user_story["business_value"] = request.form['business_value']
        updated_user_story["estimation"] = request.form['estimation']
        updated_user_story["status"] = request.form['status']
        query_db("UPDATE sprinter SET title=?,"
                 "content=?, "
                 "acceptance_criteria=?, "
                 "business_value=?, "
                 "estimation=?, "
                 "status=? WHERE id=?", (updated_user_story))
        return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        setup_db()
        app.run(debug=True)