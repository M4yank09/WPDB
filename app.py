import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

DB_FILE = "ChatStorage.sqlite"
DB_URL = "https://drive.google.com/uc?export=download&id=1XkD541CtKuRyJR4sZP8_dklSaRP3ybkI"

def download_db():
    if not os.path.exists(DB_FILE):
        print("Downloading database...")
        r = requests.get(DB_URL)
        with open(DB_FILE, "wb") as f:
            f.write(r.content)
        print("Download complete.")

download_db()

import sqlite3

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone = request.form.get("phone")
        if not phone:
            return "Please enter a phone number."

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Example query to get messages with this phone number in either sender or receiver
        query = """
        SELECT ZMESSAGEDATE, ZISFROMME, ZTEXT
        FROM ZWAMESSAGE
        WHERE ZFROMJID LIKE ? OR ZTOJID LIKE ?
        ORDER BY ZMESSAGEDATE
        """
        pattern = f"%{phone}%"
        cur.execute(query, (pattern, pattern))
        rows = cur.fetchall()
        conn.close()

        # Simple HTML format
        html = "<h2>Messages with {}</h2><ul>".format(phone)
        for date, isfromme, text in rows:
            # Convert Apple timestamp (seconds since 2001-01-01) to readable time
            import datetime
            timestamp = datetime.datetime.fromtimestamp(date + 978307200)
            sender = "Me" if isfromme == 1 else phone
            html += f"<li>[{timestamp}] <b>{sender}:</b> {text}</li>"
        html += "</ul>"
        return html

    return '''
        <form method="post">
            Enter phone number (e.g. 919822596818): <input name="phone" />
            <input type="submit" value="Get Chats" />
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)

    return render_template('index.html')
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
