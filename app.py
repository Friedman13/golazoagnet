import os
from flask import Flask, request, jsonify, render_template
import urllib.request
import json

app = Flask(__name__)

SYSTEM = """אתה סוכן תיירות ספורט של Goalzo — חברה ישראלית המתמחה בחבילות ספורט לאירועים בחו"ל.
אתה עונה בעברית בלבד, בטון חם, מקצועי ונלהב מספורט.

השירותים שאתה מציע:
- כרטיסים למשחקי כדורגל, טניס, F1 ועוד
- חבילות טיסה + מלון + כרטיסים
- סיורים ומדריכים
- VIP ולאונג'ים

אסוף בשיחה טבעית — שאלה אחת בכל פעם:
1. שם מלא
2. מספר טלפון
3. איזה אירוע או יעד
4. תאריכים משוערים
5. מספר משתתפים
6. תקציב משוער

תן טווחי מחיר כשמתאים. לדוגמה: חבילה לצ'מפיונס ליג מתחילה בסביבות 2,500-4,000 דולר לאדם.
כשיש לך את כל 6 הפרטים — סיים בהודעה חמה שנציג יחזור אליהם בקרוב.
התחל בברכת שלום חמה."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        print(f"API key status: {'found' if api_key else 'MISSING'}")

        if not api_key:
            return jsonify({"error": "API key missing"}), 500

        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 1000,
            "system": SYSTEM,
            "messages": messages
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode("utf-8"))

        message = result["content"][0]["text"]
        return jsonify({"message": message})

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
