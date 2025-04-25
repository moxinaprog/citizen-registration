from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Создание базы данных и таблицы, если не существует
def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS citizens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                birth_year TEXT,
                passport_number TEXT,
                house_number TEXT,
                mahalla TEXT,
                phone_number TEXT,
                passport_file TEXT
            )
        """)

@app.route('/')
def form():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM citizens")
        data = cur.fetchall()
    return render_template('form.html', data=data)

@app.route('/submit', methods=["POST"])
def submit():
    data = request.form
    file = request.files['passport_file']

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        with sqlite3.connect("database.db") as conn:
            conn.execute("""
                INSERT INTO citizens (
                    first_name, last_name, middle_name, birth_year,
                    passport_number, house_number, mahalla, phone_number, passport_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['first_name'],
                data['last_name'],
                data['middle_name'],
                data['birth_year'],
                data['passport_number'],
                data['house_number'],
                data['mahalla'],
                data['phone_number'],
                filename
            ))
    return redirect(url_for('form'))

# Доступ к загруженным файлам
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Панель администратора
@app.route('/admin')
def admin_panel():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM citizens")
        data = cur.fetchall()
    return render_template('admin.html', data=data)

# Запуск сервера
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    init_db()
    app.run(debug=True)
