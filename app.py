from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'mindcare_secret_key'

def get_db():
    conn = sqlite3.connect('mindcare.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                         (name, email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = 'Email already registered. Please login.'
        finally:
            conn.close()
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                            (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('chat'))
        else:
            error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        user_msg = request.form['message']
        bot_reply = get_bot_reply(user_msg)
        conn.execute('INSERT INTO chats (user_id, sender, message) VALUES (?, ?, ?)',
                     (session['user_id'], 'user', user_msg))
        conn.execute('INSERT INTO chats (user_id, sender, message) VALUES (?, ?, ?)',
                     (session['user_id'], 'bot', bot_reply))
        conn.commit()
    messages = conn.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY id',
                            (session['user_id'],)).fetchall()
    conn.close()
    return render_template('chat.html', messages=messages, name=session['user_name'])

def get_bot_reply(msg):
    msg = msg.lower()
    if any(w in msg for w in ['anxious', 'anxiety', 'nervous', 'panic']):
        return "I hear you. Anxiety can feel overwhelming. Try taking 5 slow deep breaths — inhale for 4 counts, hold for 4, exhale for 6. Would you like to talk more about what's causing it?"
    elif any(w in msg for w in ['sleep', 'insomnia', 'tired', 'exhausted']):
        return "Sleep problems really affect everything. Try keeping a consistent bedtime and avoiding screens 1 hour before bed. What does your bedtime routine look like?"
    elif any(w in msg for w in ['sad', 'depress', 'hopeless', 'empty', 'cry']):
        return "I'm sorry you're feeling this way. Your feelings are valid. Would you like to share more about what's been going on?"
    elif any(w in msg for w in ['stress', 'stressed', 'pressure']):
        return "Stress is your mind's signal that something needs attention. Regular breaks and talking about it really help. What's been most stressful lately?"
    elif any(w in msg for w in ['overwhelm', 'too much', 'cant cope']):
        return "Feeling overwhelmed is a sign you're carrying a lot. Try writing everything down, then pick just one small thing to tackle first. What's weighing on you most?"
    elif any(w in msg for w in ['motivat', 'lazy', 'stuck', 'unmotivated']):
        return "Lack of motivation often means your mind needs rest or a fresh purpose. Start tiny — just 5 minutes on something you care about. What feels most stuck?"
    elif any(w in msg for w in ['happy', 'good', 'great', 'better', 'fine']):
        return "That's wonderful to hear! Positive moments matter. What's been going well for you?"
    elif any(w in msg for w in ['hello', 'hi', 'hey']):
        return "Hello! I'm MindCare, your mental health support assistant. How are you feeling today?"
    else:
        return "Thank you for sharing that with me. I'm here to listen. Can you tell me more about how you've been feeling?"

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    result = None
    if request.method == 'POST':
        answers = [int(request.form.get(f'q{i}', 0)) for i in range(1, 6)]
        score = sum(answers)
        if score <= 5:
            risk_level = 'Low'
        elif score <= 10:
            risk_level = 'Moderate'
        else:
            risk_level = 'High'
        conn = get_db()
        conn.execute('INSERT INTO assessments (user_id, score, risk_level) VALUES (?, ?, ?)',
                     (session['user_id'], score, risk_level))
        conn.commit()
        conn.close()
        result = {'score': score, 'risk_level': risk_level}
    return render_template('assessment.html', result=result, name=session['user_name'])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)