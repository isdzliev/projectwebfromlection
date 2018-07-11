import os
import sqlite3

from flask import Flask, render_template, g, request, redirect, url_for, jsonify

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect(os.path.join(app.root_path, 'db.sqlite'))
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.execute('SELECT id, content FROM notes')
    notes = cursor.fetchall()
    return render_template('index.html', title = 'Welcome to My Site', notes=notes)

@app.route('/create', methods=['POST'])
def create():
    with get_db() as db:
        db.execute('INSERT INTO notes(content) VALUES (?)', [request.form['content']] )
    return redirect(url_for('index'))


@app.route('/remove', methods=['POST'])
def remove():
    with get_db() as db:
        db.execute('DELETE FROM notes WHERE id = ?', [request.form['id']])
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit(id):
    db = get_db()
    cursor = db.execute('SELECT id, content FROM notes WHERE id = ?', [id])
    note = cursor.fetchone()
    return render_template('edit.html, note=note')

@app.route('/save', methods=['POST'])
def save():
    with get_db() as db:
        db.execute('UPDATE notes SET content=? WHERE id = ?', [request.form['content'], request.form['id']] )
    return redirect(url_for('index'))

@app.route('/api/v1/notes', methods=['GET'])
def api_get_all():
    db=get_db()
    cursor = db.execute('SELECT id, content FROM notes')
    notes = cursor.fetchall()
    data = list([dict((cursor.description[idx][0], value) for idx, value in enumerate(note)) for note in notes])
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
