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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            note TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_bot_reply(msg):
    msg_lower = msg.lower()
    if any(w in msg_lower for w in ['suicide', 'kill myself', 'end my life', 'want to die', 'cant go on', 'hurt myself', 'self harm']):
        return "I am very concerned about what you just shared. Please reach out to Befrienders Kenya immediately on 0800 723 253 — they are available 24/7 and are here to help you. You are not alone."
    elif any(w in msg_lower for w in ['anxious', 'anxiety', 'nervous', 'panic', 'worried', 'worry']):
        return "I hear you. Anxiety can feel overwhelming. Try taking 5 slow deep breaths — inhale for 4 counts, hold for 4, exhale for 6. Would you like to talk more about what is causing it?"
    elif any(w in msg_lower for w in ['sleep', 'insomnia', 'tired', 'exhausted', 'cannot sleep', 'cant sleep']):
        return "Sleep problems really affect everything. Try keeping a consistent bedtime, avoiding screens 1 hour before bed and keeping your room cool and dark. What does your bedtime routine look like?"
    elif any(w in msg_lower for w in ['sad', 'depress', 'hopeless', 'empty', 'cry', 'crying', 'unhappy', 'miserable']):
        return "I am sorry you are feeling this way. Your feelings are valid and it takes courage to share them. Would you like to tell me more about what has been going on?"
    elif any(w in msg_lower for w in ['stress', 'stressed', 'pressure', 'overwhelm', 'too much', 'cant cope']):
        return "Feeling stressed or overwhelmed is a sign you are carrying a lot right now. Try writing everything on your mind down, then pick just one small thing to tackle first. What is weighing on you most?"
    elif any(w in msg_lower for w in ['motivat', 'lazy', 'stuck', 'unmotivated', 'procrastinat', 'give up']):
        return "Lack of motivation often means your mind needs rest or a fresh sense of purpose. Start tiny — just 5 minutes on something you care about. What area of your life feels most stuck right now?"
    elif any(w in msg_lower for w in ['angry', 'anger', 'frustrated', 'furious', 'mad', 'rage']):
        return "Anger is a normal emotion and it is okay to feel it. Try stepping away from the situation, taking deep breaths and giving yourself time to calm down before responding. What triggered these feelings?"
    elif any(w in msg_lower for w in ['lonely', 'alone', 'isolated', 'no friends', 'nobody cares']):
        return "Feeling lonely is one of the most painful human experiences. You are not alone — I am here with you right now. Is there anyone in your life you feel you could reach out to today?"
    elif any(w in msg_lower for w in ['fear', 'scared', 'afraid', 'phobia', 'terrified']):
        return "Fear can feel very real and powerful. Acknowledging what you are afraid of is the first brave step. Would you like to share what is making you feel scared?"
    elif any(w in msg_lower for w in ['confidence', 'self esteem', 'worthless', 'not good enough', 'failure', 'loser']):
        return "You are not defined by your mistakes or your struggles. Every person has unique value and strength. What is one thing you like about yourself, no matter how small?"
    elif any(w in msg_lower for w in ['relationship', 'breakup', 'heartbreak', 'divorce', 'partner', 'boyfriend', 'girlfriend']):
        return "Relationship pain can be deeply difficult to carry. It is okay to grieve and take time to heal. Would you like to talk about what happened?"
    elif any(w in msg_lower for w in ['family', 'parents', 'mother', 'father', 'siblings', 'home']):
        return "Family situations can be complicated and emotionally draining. Your feelings about your family are valid. Would you like to share more about what is going on at home?"
    elif any(w in msg_lower for w in ['school', 'study', 'exam', 'university', 'college', 'fail', 'grades']):
        return "Academic pressure can be really tough. Remember that your grades do not define your worth. Try breaking your study into small manageable chunks and take regular breaks. What subject or task feels most overwhelming?"
    elif any(w in msg_lower for w in ['work', 'job', 'boss', 'colleague', 'fired', 'unemployed', 'career']):
        return "Work stress is very common and can really affect your mental health. It is important to set boundaries between work and personal time. What has been happening at work?"
    elif any(w in msg_lower for w in ['happy', 'good', 'great', 'better', 'fine', 'wonderful', 'amazing', 'excited']):
        return "That is wonderful to hear! Positive moments are so important. What has been going well for you lately?"
    elif any(w in msg_lower for w in ['thank', 'thanks', 'helpful', 'appreciate']):
        return "You are very welcome! I am always here whenever you need to talk. Remember, reaching out is a sign of strength."
    elif any(w in msg_lower for w in ['hello', 'hi', 'hey', 'good morning', 'good evening', 'good afternoon']):
        return "Hello! I am MindCare, your mental health support assistant. I am here to listen and support you. How are you feeling today?"
    elif any(w in msg_lower for w in ['what is', 'what are', 'how do', 'how can', 'explain', 'tell me', 'define']):
        return "That is a great question. Mental health covers our emotional, psychological and social wellbeing. I am here to help you understand and navigate any challenges you are facing. Could you tell me more specifically what you would like to know?"
    elif any(w in msg_lower for w in ['tip', 'advice', 'help', 'suggest', 'recommend']):
        return "Here are some helpful tips: practice deep breathing daily, get 7 to 9 hours of sleep, exercise for at least 30 minutes, stay connected with people you trust, and limit social media use. Which of these would you like to explore more?"
    else:
        return "Thank you for sharing that with me. I am here to listen and support you without any judgment. Could you tell me a little more about how you have been feeling lately?"
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    if request.method == 'POST':
        success = True
    return render_template('contact.html', success=success)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?',
                        (session['user_id'],)).fetchone()
    success = None
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            name = request.form['name']
            email = request.form['email']
            try:
                conn.execute('UPDATE users SET name = ?, email = ? WHERE id = ?',
                             (name, email, session['user_id']))
                conn.commit()
                session['user_name'] = name
                success = 'Profile updated successfully!'
                user = conn.execute('SELECT * FROM users WHERE id = ?',
                                    (session['user_id'],)).fetchone()
            except sqlite3.IntegrityError:
                error = 'That email is already in use.'
        elif action == 'change_password':
            current = request.form['current_password']
            new = request.form['new_password']
            confirm = request.form['confirm_password']
            if user['password'] != current:
                error = 'Current password is incorrect.'
            elif new != confirm:
                error = 'New passwords do not match.'
            else:
                conn.execute('UPDATE users SET password = ? WHERE id = ?',
                             (new, session['user_id']))
                conn.commit()
                success = 'Password updated successfully!'
        elif action == 'delete_account':
            conn.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
            conn.execute('DELETE FROM chats WHERE user_id = ?', (session['user_id'],))
            conn.execute('DELETE FROM assessments WHERE user_id = ?', (session['user_id'],))
            conn.commit()
            conn.close()
            session.clear()
            return redirect(url_for('login'))
    conn.close()
    return render_template('profile.html',
                           name=user['name'],
                           email=user['email'],
                           success=success,
                           error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    total_chats = conn.execute('SELECT COUNT(*) FROM chats WHERE user_id = ?',
                               (session['user_id'],)).fetchone()[0]
    total_assessments = conn.execute('SELECT COUNT(*) FROM assessments WHERE user_id = ?',
                                     (session['user_id'],)).fetchone()[0]
    latest = conn.execute('SELECT risk_level FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1',
                          (session['user_id'],)).fetchone()
    latest_risk = latest['risk_level'] if latest else None
    assessments = conn.execute('SELECT * FROM assessments WHERE user_id = ? ORDER BY id DESC',
                               (session['user_id'],)).fetchall()
    recent_chats = conn.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY id DESC LIMIT 5',
                                (session['user_id'],)).fetchall()
    conn.close()
    assessment_dates = [a['date'][:10] for a in reversed(list(assessments))]
    assessment_scores = [a['score'] for a in reversed(list(assessments))]
    from datetime import date
    total_days = (date.today() - date(2026, 1, 1)).days
    return render_template('dashboard.html',
                           name=session['user_name'],
                           total_chats=total_chats,
                           total_assessments=total_assessments,
                           latest_risk=latest_risk,
                           assessments=assessments,
                           recent_chats=recent_chats,
                           assessment_dates=assessment_dates,
                           assessment_scores=assessment_scores,
                           total_days=total_days)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    assessments = conn.execute(
        'SELECT * FROM assessments WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)).fetchall()
    conn.close()
    total = len(assessments)
    low_count = sum(1 for a in assessments if a['risk_level'] == 'Low')
    mod_count = sum(1 for a in assessments if a['risk_level'] == 'Moderate')
    high_count = sum(1 for a in assessments if a['risk_level'] == 'High')
    latest_risk = assessments[0]['risk_level'] if assessments else None
    return render_template('history.html',
                           assessments=assessments,
                           total=total,
                           low_count=low_count,
                           mod_count=mod_count,
                           high_count=high_count,
                           latest_risk=latest_risk)

@app.route('/mood', methods=['GET', 'POST'])
def mood():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    success = None
    if request.method == 'POST':
        mood_val = request.form.get('mood')
        note = request.form.get('note', '')
        conn.execute('INSERT INTO moods (user_id, mood, note) VALUES (?, ?, ?)',
                     (session['user_id'], mood_val, note))
        conn.commit()
        success = 'Mood logged successfully!'
    moods = conn.execute('SELECT * FROM moods WHERE user_id = ? ORDER BY id DESC',
                         (session['user_id'],)).fetchall()
    conn.close()
    mood_map = {'Amazing': 5, 'Good': 4, 'Okay': 3, 'Bad': 2, 'Terrible': 1}
    mood_dates = [m['date'][:10] for m in reversed(list(moods))]
    mood_scores = [mood_map.get(m['mood'], 3) for m in reversed(list(moods))]
    mood_counts = {
        'Amazing': sum(1 for m in moods if m['mood'] == 'Amazing'),
        'Good': sum(1 for m in moods if m['mood'] == 'Good'),
        'Okay': sum(1 for m in moods if m['mood'] == 'Okay'),
        'Bad': sum(1 for m in moods if m['mood'] == 'Bad'),
        'Terrible': sum(1 for m in moods if m['mood'] == 'Terrible')
    }
    most_common = max(mood_counts, key=mood_counts.get) if moods else None
    return render_template('mood.html',
                           moods=moods,
                           mood_dates=mood_dates,
                           mood_scores=mood_scores,
                           mood_counts=mood_counts,
                           most_common=most_common,
                           success=success)

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    users_raw = conn.execute('SELECT * FROM users').fetchall()
    users = []
    for u in users_raw:
        assessment_count = conn.execute('SELECT COUNT(*) FROM assessments WHERE user_id = ?', (u['id'],)).fetchone()[0]
        chat_count = conn.execute('SELECT COUNT(*) FROM chats WHERE user_id = ?', (u['id'],)).fetchone()[0]
        latest = conn.execute('SELECT risk_level FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1', (u['id'],)).fetchone()
        latest_risk = latest['risk_level'] if latest else None
        users.append({
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'assessment_count': assessment_count,
            'chat_count': chat_count,
            'latest_risk': latest_risk
        })
    total_users = len(users)
    total_assessments = conn.execute('SELECT COUNT(*) FROM assessments').fetchone()[0]
    total_chats = conn.execute('SELECT COUNT(*) FROM chats').fetchone()[0]
    high_risk = sum(1 for u in users if u['latest_risk'] == 'High')
    high_risk_users = [u for u in users if u['latest_risk'] == 'High']
    conn.close()
    return render_template('admin.html',
                           users=users,
                           total_users=total_users,
                           total_assessments=total_assessments,
                           total_chats=total_chats,
                           high_risk=high_risk,
                           high_risk_users=high_risk_users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)