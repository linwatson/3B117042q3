from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'


# 連接到數據庫
def get_db_connection():
    conn = sqlite3.connect('mydb.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM member WHERE iid = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user is None:
            return redirect(url_for('login'))
        return render_template('index.html', user=user)
    except Exception as e:
        logging.error(e, exc_info=True)
        return render_template('error.html', message="發生了例外")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM member WHERE idno = ?', (idno,)).fetchone()
            conn.close()
            if user and user['pwd'] == pwd:  # 檢查使用者帳號和密碼是否一致
                session['user_id'] = user['iid']
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="請輸入正確的帳號密碼")
        except Exception as e:
            logging.error(e, exc_info=True)
            return render_template('error.html', message="發生了例外")
    return render_template('login.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM member WHERE iid = ?', (session['user_id'],)).fetchone()
        if request.method == 'POST':
            nm = request.form['nm']
            birth = request.form['birth']
            blood = request.form['blood']
            phone = request.form['phone']
            email = request.form['email']
            idno = request.form['idno']
            pwd = request.form['pwd']
            conn.execute('UPDATE member SET nm = ?, birth = ?, blood = ?, phone = ?, email = ?, idno = ?, pwd = ? WHERE iid = ?',
                         (nm, birth, blood, phone, email, idno, pwd, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
        conn.close()
        return render_template('edit.html', user=user)
    except Exception as e:
        logging.error(e, exc_info=True)
        return render_template('error.html', message="發生了例外")
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.errorhandler(Exception)
def handle_error(error):
    # 可以在這裡記錄錯誤到日誌中
    app.logger.error(f"An error occurred: {error}")
    # 返回錯誤頁面
    return render_template('error.html'), 500
