from flask import Flask, request, jsonify, render_template, g
from flask_moment import Moment
from datetime import datetime, timedelta
from pytz import timezone
import sqlite3
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
moment = Moment(app)
app.config['MOMENT_TIMEZONE'] = 'Asia/Ho_Chi_Minh'
DATABASE = 'database.db'
NOTIFICATIONS_TABLE = 'notifications'
correct_flags = {
    'TCIS{Soc-Flag1}', 'TCIS{Soc-Flag2}', 'TCIS{Soc-Flag3}',
    'TCIS{Soc-Flag4}', 'TCIS{Soc-Flag5}'
}
team_flags = {}

socketio = SocketIO(app, async_mode='threading')
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        script = f.read().decode('utf-8')
        if 'CREATE TABLE users' not in script:
            db.cursor().executescript(script)
            db.commit()
    db.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_notifications_table():
    db = sqlite3.connect(DATABASE)
    db.execute(f"CREATE TABLE IF NOT EXISTS {NOTIFICATIONS_TABLE} (message TEXT)")
    db.commit()
    db.close()

def store_notification(message):
    db = sqlite3.connect(DATABASE)
    db.execute(f"INSERT INTO {NOTIFICATIONS_TABLE} (message) VALUES (?)", (message,))
    db.commit()
    db.close()

def get_latest_notification():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT message FROM {NOTIFICATIONS_TABLE} ORDER BY rowid DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_flag():
    if request.method == 'POST':
        name = request.form.get('name')
        team = request.form.get('team')
        flag = request.form.get('flag')
        if not name or not team:
            return jsonify({'message': 'Name and team are required!'}), 400
        if not flag:
            return jsonify({'message': 'Flag not found!'}), 400
        flag = flag.strip()

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT COUNT(*) FROM users WHERE flag = ? AND team = ?', (flag, team))
        result = cursor.fetchone()
        if result[0] > 0:
            return jsonify({'message': 'Your team has already submitted this flag!'}), 400

        if flag in correct_flags:
            db.execute('INSERT INTO users (name, team, flag) VALUES (?, ?, ?)', (name, team, flag))
            db.commit()

            team_flags[team] = team_flags.get(team, 0) + 1

            message = f"Chúc mừng {team} đã khai thác được một lỗ hổng mới, tổng số flag hiện tại của {team} là {team_flags[team]}"
            socketio.emit('new_flag', {'team': team, 'flag_count': team_flags[team]}, broadcast=True, namespace='/')
            socketio.emit('notification', {'message': message}, broadcast=True, namespace='/')
            store_notification(message)

            return jsonify({'message': 'Correct flag!', 'flag_count': team_flags[team]}), 200
        else:
            return jsonify({'message': 'Incorrect flag!'}), 400

    return render_template('submit.html')

@app.route('/leaderboard')
def leaderboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name, team, flag, timestamp FROM users')
    users = cursor.fetchall()

    formatted_users = []
    for user in users:
        timestamp = datetime.strptime(user[3], '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        local_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        formatted_users.append((user[0], user[1], user[2], local_timestamp))

    context = {
        'users': formatted_users,
        'moment': moment  # Add the moment object to the context
    }
    return render_template('leaderboard.html', **context)

@socketio.on('connect', namespace='/')
def handle_connect():
    emit('initial_flags', team_flags, namespace='/')
    send_latest_notification()

def send_latest_notification():
    latest_notification = get_latest_notification()
    if latest_notification is not None:
        emit('notification', {'message': latest_notification}, namespace='/')

if __name__ == '__main__':
    with app.app_context():
        init_db()
        create_notifications_table()
    socketio.run(app, debug=True, port=8000)

@app.context_processor
def inject_moment():
    return {'moment': moment}