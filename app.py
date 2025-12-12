import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, g
from flask_session import Session
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_very_secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

DATABASE = 'homework.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 允许通过列名访问
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    get_db().commit()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

# --- API 接口 ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = query_db('SELECT * FROM users WHERE username = ?', [data['username']], one=True)
    if user and check_password_hash(user['password_hash'], data['password']):
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['username'] = user['username']
        return jsonify({'status': 'success', 'role': user['role'], 'username': user['username']})
    return jsonify({'status': 'fail', 'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'is_logged_in': True, 'role': session['role'], 'username': session['username']})
    return jsonify({'is_logged_in': False})

@app.route('/api/assignments', methods=['GET', 'POST'])
def handle_assignments():
    if 'user_id' not in session: return jsonify({'msg': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        # 学生查看作业列表（带提交状态），老师查看自己发布的
        if session['role'] == 'student':
            sql = '''
                SELECT a.*, u.username as teacher_name, s.score, s.content as my_submission 
                FROM assignments a 
                JOIN users u ON a.teacher_id = u.id
                LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = ?
            '''
            return jsonify(query_db(sql, [session['user_id']]))
        else:
            sql = 'SELECT * FROM assignments WHERE teacher_id = ? ORDER BY created_at DESC'
            return jsonify(query_db(sql, [session['user_id']]))

    if request.method == 'POST' and session['role'] == 'teacher':
        data = request.json
        sql = 'INSERT INTO assignments (title, description, due_date, teacher_id) VALUES (?, ?, ?, ?)'
        query_db(sql, [data['title'], data['desc'], data['date'], session['user_id']])
        return jsonify({'status': 'success'})

@app.route('/api/submissions', methods=['POST'])
def submit_homework():
    if session['role'] != 'student': return jsonify({'msg': 'Role error'}), 403
    data = request.json
    # Upsert logic: 如果已存在则更新，否则插入 (SQLite ON CONFLICT)
    sql = '''
        INSERT INTO submissions (assignment_id, student_id, content) 
        VALUES (?, ?, ?) 
        ON CONFLICT(assignment_id, student_id) DO UPDATE SET content=excluded.content, submitted_at=CURRENT_TIMESTAMP
    '''
    query_db(sql, [data['aid'], session['user_id'], data['content']])
    return jsonify({'status': 'success'})

@app.route('/api/grade', methods=['POST'])
def grade_submission():
    if session['role'] != 'teacher': return jsonify({'msg': 'Role error'}), 403
    data = request.json
    # 安全检查：确保这个作业是该老师发布的
    valid = query_db('SELECT id FROM assignments WHERE id=? AND teacher_id=?', [data['aid'], session['user_id']], one=True)
    if not valid: return jsonify({'msg': 'No permission'}), 403
    
    query_db('UPDATE submissions SET score = ? WHERE id = ?', [data['score'], data['sid']])
    return jsonify({'status': 'success'})

@app.route('/api/teacher/subs/<int:aid>', methods=['GET'])
def get_assignment_subs(aid):
    if session['role'] != 'teacher': return jsonify({'msg': 'Role error'}), 403
    sql = '''
        SELECT s.*, u.username 
        FROM submissions s 
        JOIN users u ON s.student_id = u.id 
        WHERE s.assignment_id = ?
    '''
    return jsonify(query_db(sql, [aid]))

if __name__ == '__main__':
    app.run(debug=True, port=80)