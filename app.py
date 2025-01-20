from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit
from pytube import YouTube

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Used for securely signing the session cookie
socketio = SocketIO(app)

is_logged_in = False
video_info = {"title": "", "url": "", "current_time": 0}

import re

def parse_video_id(link):
    match = re.search(r"v=([a-zA-Z0-9_-]+)", link)
    if match:
        return match.group(1)
    return None

# Initialize the session on first load
@app.before_request
def ensure_logged_in():
    if 'logged_in' not in session:
        session['logged_in'] = False



# Simple login page to set session
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['logged_in']:  # If already logged in, redirect to the protected page
        return redirect(url_for('protected_page'))


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Replace with your own login check logic
        if username == 'aaa' and password == 'aaa' and session['logged_in'] == False:
            session['logged_in'] = True  # Set login state in session
            return redirect(url_for('protected_page'))
        else:
            return 'Invalid login', 401
    
    return render_template('login.html')


# Protected page only accessible after logging in
@app.route('/protected_page')
def protected_page():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    return render_template('protected_page.html')  # Render your protected page

# Logout route to clear session
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('logged_in', None)  # Clear the session to log out
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route("/submit", methods=["POST"])
def submit():
    global video_info
    youtube_link = request.form.get("yt_link")
    try:
        yt = YouTube(youtube_link)
        video_info["url"] = youtube_link
        video_info["current_time"] = 0
    except Exception as e:
        return f"Error: {e}", 400
    
    return redirect(url_for("sync"))

@app.route('/sync', methods=['POST', 'GET'])
def sync():
    # Extract video link from the form (POST request)
    if request.method == 'POST':
        video_link = request.form['youtube_link']

        # Parse YouTube video ID from the link
        video_id = parse_video_id(video_link)
        video_title = "Example Title"  # Replace with code to fetch video title dynamically
        current_time = 0

        # Broadcast video details to connected clients
        socketio.emit("video_details", {
            "video_id": video_id,
            "title": video_title,
            "current_time": current_time
        })

        # Render the sync page
        return render_template('sync.html')

    # If accessed via GET, just render the page
    return render_template('sync.html')


@socketio.on("time_update")
def handle_time_update(data):
    global video_info
    video_info["current_time"] = data["current_time"]
    emit("broadcast_time", video_info, broadcast=True)




if __name__ == '__main__':
    app.run(debug=True)