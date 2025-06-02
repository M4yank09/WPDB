from flask import Flask, render_template, request, send_file
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        db_file = request.files['db_file']
        phone = request.form['phone'].strip()
        jid = phone + '@s.whatsapp.net'

        db_path = os.path.join(UPLOAD_FOLDER, secure_filename(db_file.filename))
        db_file.save(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT ZISFROMME, ZTEXT, ZMESSAGEDATE
            FROM ZWAMESSAGE
            WHERE ZTOJID = ? OR ZFROMJID = ?
            ORDER BY ZMESSAGEDATE
        """, (jid, jid))

        messages = []
        for isfromme, text, timestamp in cursor.fetchall():
            if not text:
                continue
            sender = 'Me' if isfromme else phone
            date = datetime.utcfromtimestamp(timestamp + 978307200).strftime('%Y-%m-%d %H:%M:%S')
            messages.append(f"<p><b>[{date}] {sender}:</b> {text}</p>")

        conn.close()

        html = "<html><body>" + "\n".join(messages) + "</body></html>"
        out_path = os.path.join(OUTPUT_FOLDER, f"{phone}_chat.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return send_file(out_path, as_attachment=True)

    return render_template('index.html')
