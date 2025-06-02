from flask import Flask, request, render_template, send_file
import sqlite3
from datetime import datetime
import os
import traceback  # ✅ Add this

app = Flask(__name__)
DB_PATH = 'ChatStorage.sqlite'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone = request.form['phone'].strip()
        jid = phone + '@s.whatsapp.net'

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            cur.execute("""
                SELECT ZISFROMME, ZTEXT, ZMESSAGEDATE
                FROM ZWAMESSAGE
                WHERE ZTOJID = ? OR ZFROMJID = ?
                ORDER BY ZMESSAGEDATE ASC
            """, (jid, jid))

            messages = []
            for isfromme, text, ts in cur.fetchall():
                if not text:
                    continue
                sender = 'Me' if isfromme else phone
                try:
                    date = datetime.utcfromtimestamp(ts + 978307200).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date = 'Unknown'
                messages.append(f"<p><b>[{date}] {sender}:</b> {text}</p>")

            html_path = f'{phone}_chat.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write("<html><body>" + "\n".join(messages) + "</body></html>")

            return send_file(html_path, as_attachment=True)

        except Exception as e:
            print("🔥 Error:", e)
            traceback.print_exc()  # ✅ Show full traceback
            return "Internal Server Error", 500

        finally:
            conn.close()

    return render_template('index.html')


    return render_template('index.html')
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
