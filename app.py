from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import re
app = Flask(__name__)

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyDSNKVFGhfCCX6Onx5b8NEyk38qTH-YRXg")

# Load Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def clean_markdown(text: str) -> str:
    text = text.replace("*", "")
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    personal = data.get("personal_life")
    professional = data.get("professional_life")
    phase = data.get("life_phase")
    advisor = data.get("advisor")

    prompt = f"""
    Analyze the following personal and professional situation:

    Name: {name}
    Age: {age}
    Gender: {gender}
    Personal Life: {personal}
    Professional Life: {professional}
    Life Phase: {phase}
    Advisor Type: {advisor}

    Your response should include the following sections:

        1. Life Situation Analysis  
        Write a compassionate and thoughtful summary of the user's current situation. Combine both personal and professional aspects. Show understanding of their emotional and practical challenges. Avoid robotic tone.

        2. Personalized Advice from a {advisor}  
        Offer advice as if you are their trusted {advisor}. Use a friendly, supportive tone. Suggest perspective shifts, emotional encouragement, or mental clarity they may need. Tailor it to their age and current phase of life.

        3. Actionable Steps Forward  
        List 3 clear and realistic actions they can take now to improve or navigate their situation. Keep them practical, doable, and non-generic. These should reflect empathy and direction.

        Format your response clearly using paragraph structure and bullet points. Do not use markdown or asterisks.
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"result": f"Error occurred: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)
