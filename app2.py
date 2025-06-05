from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pymongo
import re
from datetime import datetime

app = Flask(__name__)

# ---- 1. Gemini Setup ----
# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyDSNKVFGhfCCX6Onx5b8NEyk38qTH-YRXg")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")


# ---- 2. MongoDB Setup ----
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["next_move_ai_db"]
collection = db["submissions"]


# ---- 3. Clean Markdown Output ----
def clean_markdown(text: str) -> str:
    text = text.replace("*", "")
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


# ---- 4. Routes ----
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    # Extract all fields
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    personal = data.get("personal_life")
    professional = data.get("professional_life")
    phase = data.get("life_phase")
    advisor = data.get("advisor")

    prompt = f"""
    Analyze the following personal and professional situation:

    - Name: {name}
    - Age: {age}
    - Gender: {gender}
    - Personal Life: {personal}
    - Professional Life: {professional}
    - Current Life Phase: {phase}
    - Preferred Advisor Type: {advisor}

    Your response should include the following:

    1. Life Situation Analysis: Thoughtful, empathetic summary of their personal and professional situation.
    2. Personalized Advice from a {advisor}: Provide age- and gender-aware support.
    3. 3 Actionable Steps: Simple, clear things they can do right now to make progress.

    Avoid markdown formatting. Respond like a human mentor or guide.
    """

    try:
        # Gemini API
        response = model.generate_content(prompt)
        result = clean_markdown(response.text)

        # Save to MongoDB
        submission_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "personal_life": personal,
            "professional_life": professional,
            "life_phase": phase,
            "advisor": advisor,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(submission_data)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": f"Error occurred: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)
