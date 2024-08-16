from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
import json, uuid
import os
from forms import LoginForm, RegisterForm, ChatForm, MessageForm, DeleteChatForm, BanUser
from datetime import datetime
import markdown
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'aboba'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
socketio = SocketIO(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
admin = ["kjhrd"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load users
def load_users():
    with open('data/users.json', 'r') as file:
        return json.load(file)

# Save users
def save_users(users):
    with open('data/users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Load blacklist
def load_blacklist():
    with open('data/blacklist.json', 'r') as file:
        return json.load(file)

# Save blacklist
def save_blacklist(users):
    with open('data/blacklist.json', 'w') as file:
        json.dump(users, file, indent=4)

# Load chats
def load_chats():
    with open('data/chats.json', 'r') as file:
        return json.load(file)

# Save chats
def save_chats(chats):
    with open('data/chats.json', 'w') as file:
        json.dump(chats, file, indent=4)

# Load messages
def load_messages():
    with open('data/messages.json', 'r') as file:
        return json.load(file)

# Save messages
def save_messages(messages):
    with open('data/messages.json', 'w') as file:
        json.dump(messages, file, indent=4)

# User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user = users.get(user_id)
    if user:
        return User(id=user_id, username=user['username'], password=user['password'])
    return None

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = load_users()
        banlist = load_blacklist()
        for user_id, user in users.items():
            if user['username'] == form.username.data and check_password_hash(user['password'], form.password.data) and not form.username.data in banlist['banlist']:
                login_user(User(id=user_id, username=user['username'], password=user['password']))
                return redirect(url_for('index'))
        if form.username.data in banlist['banlist']: return redirect(url_for('ban'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        users = load_users()
        new_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, form.username.data))
        if new_id in users:
            flash('Никнейм занят')
        else:
            users[new_id] = {
                'username': form.username.data,
                'password': generate_password_hash(form.password.data),
                'ip': request.remote_addr
            }
            save_users(users)
            flash('Успешная регистрация! Пожалуйста войдите.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ban')
def ban():
    return "You have been banned. You are so insignificant that you don't even have an html file allocated to you"

@app.route('/')
def index():
    chats = load_chats()
    return_chats = {}
    banlist = load_blacklist()
    for chat in chats:
        return_chats[chat]=chats[chat]
    return render_template('index.html', chats=return_chats)

@app.route('/article/<chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chats = load_chats()
    formated = markdown.markdown(chats[chat_id]["article"], extensions=['extra'])
    name = markdown.markdown(chats[chat_id]["name"], extensions=['extra'])
    messages = load_messages().get(chat_id, [])
    form = MessageForm()
    banlist = load_blacklist()
    if current_user.username in banlist['banlist']: return redirect(url_for('ban'))
    return render_template('chat.html', name=name, text=formated, chat=chats[chat_id], messages=messages, form=form, chat_id=chat_id)

@app.route('/create_article', methods=['GET', 'POST'])
@login_required
def create_chat():
    banlist = load_blacklist()
    if current_user.username in banlist['banlist']: return redirect(url_for('ban'))
    form = ChatForm()
    if form.validate_on_submit():
        chats = load_chats()
        new_id = str(uuid.uuid1())
        chats[new_id] = {
            'name': form.name.data,
            'article': form.article.data,
            'owner': current_user.username
        }
        save_chats(chats)
        return redirect(url_for('index'))
    return render_template('create_chat.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/@bm1n', methods=['GET', 'POST'])
@login_required
def admin_page():
    banlist = load_blacklist()
    if current_user.username in banlist['banlist']: return redirect(url_for('ban'))
    form = BanUser();
    if form.validate_on_submit():
        banlist = load_blacklist()
        banlist['banlist'].append(form.username.data)
        save_blacklist(banlist)
    if current_user.username in admin:
        return render_template('admin.html', form=form)
    else:
        return redirect(url_for('index'))

@app.route('/delete_chat', methods=['GET', 'POST'])
@login_required
def delete_chat():
    banlist = load_blacklist()
    if current_user.username in banlist['banlist']: return redirect(url_for('ban'))
    form = DeleteChatForm();
    if (request.args.get('id')):
        form.chat_id.data = request.args.get('id')
    chats = load_chats()
    if form.validate_on_submit():
        if (form.chat_id.data in chats and chats[form.chat_id.data]['owner'] == current_user.username) or current_user.username in admin:
            del chats[form.chat_id.data]
            save_chats(chats)
            messages = load_messages()
            if form.chat_id.data in messages:
                del messages[form.chat_id.data]
                save_messages(messages)
            if request.args.get('url'):
                return redirect(url_for(request.args.get('url')))
            else:
                return redirect(url_for('index'))
    return render_template('delete_chat.html', form=form)

# Handle file uploads
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} has sent message to the room {data['room']}: {data['message']}")
    messages = load_messages()
    if data['room'] not in messages:
        messages[data['room']] = []
    messages[data['room']].append({
        'user': data['username'],
        'content': data['message'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_messages(messages)
    emit('receive_message', data, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} has joined the room {data['room']}")
    join_room(data['room'])
    emit('join_room_announcement', data, room=data['room'])

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info(f"{data['username']} has left the room {data['room']}")
    leave_room(data['room'])
    emit('leave_room_announcement', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)
