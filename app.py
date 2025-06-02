from flask import Flask, request, render_template, send_file
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Upload SQLite DB
        db_file = request.files['db_file']
        phone = request.form['phone'].strip()
        jid = phone + '@s.whatsapp.net'

        db_path = os.path.join(UPLOAD_DIR, secure_filename(db_file.filename))
        db_file.save(db_path)

        # Connect to uploaded database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT ZISFROMME, ZTEXT, ZMESSAGEDATE
                FROM ZWAMESSAGE
                WHERE ZTOJID = ? OR ZFROMJID = ?
                ORDER BY ZMESSAGEDATE
            """, (jid, jid))

            messages = []
            for isfromme, text, ts in cur.fetchall():
                if not text:
                    continue
                sender = 'Me' if isfromme else phone
                date = datetime.utcfromtimestamp(ts + 978307200).strftime('%Y-%m-%d %H:%M:%S')
                messages.append(f"<p><b>[{date}] {sender}:</b> {text}</p>")

            # Write to HTML file
            html_path = os.path.join(UPLOAD_DIR, f'{phone}_chat.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write("<html><body>" + "\n".join(messages) + "</body></html>")

            return send_file(html_path, as_attachment=True)
        finally:
            conn.close()

    return render_template('index.html')
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render will provide PORT
    app.run(host='0.0.0.0', port=port)
