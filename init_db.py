import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('homework.db')
    c = conn.cursor()

    # 1. 清理旧数据
    c.executescript('''
        DROP TABLE IF EXISTS submissions;
        DROP TABLE IF EXISTS assignments;
        DROP TABLE IF EXISTS users;
    ''')

    # 2. 创建表
    c.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('student', 'teacher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            teacher_id INTEGER REFERENCES users(id),
            due_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER REFERENCES assignments(id),
            student_id INTEGER REFERENCES users(id),
            content TEXT,
            score INTEGER CHECK(score >= 0 AND score <= 100),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(assignment_id, student_id)
        );
    ''')

    # 3. 插入示例数据
    # 默认密码统一为: 123456
    pwd = generate_password_hash('123456')
    
    # 老师
    teachers = [('teacher1', pwd, 'teacher'), ('wang_laoshi', pwd, 'teacher')]
    c.executemany('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', teachers)
    
    # 学生
    students = [(f'student{i}', pwd, 'student') for i in range(1, 6)]
    c.executemany('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', students)

    # 作业
    assignments = [
        ('SQL基础练习', '完成第三章课后习题', 1, '2025-12-31'),
        ('Python Flask入门', '实现一个Hello World网页', 1, '2025-12-25'),
        ('数据库设计', '设计电商系统ER图', 2, '2026-01-10')
    ]
    c.executemany('INSERT INTO assignments (title, description, teacher_id, due_date) VALUES (?, ?, ?, ?)', assignments)

    # 提交记录 (部分学生已交)
    submissions = [
        (1, 3, '这是我的SQL作业答案...', 85), # assignment 1, student 1 (id=3 based on insert order)
        (1, 4, '老师我不会写', 50),
        (2, 3, 'print("Hello World")', None) # 未评分
    ]
    c.executemany('INSERT INTO submissions (assignment_id, student_id, content, score) VALUES (?, ?, ?, ?)', submissions)

    conn.commit()
    conn.close()
    print("数据库初始化完成：homework.db 已生成。")

if __name__ == '__main__':
    init_db()