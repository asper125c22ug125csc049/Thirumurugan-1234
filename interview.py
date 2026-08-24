import streamlit as st
from textblob import TextBlob
import pandas as pd
import os
import PyPDF2

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Interview Analyzer", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.stButton>button {
    background-color: #00c6ff;
    color: black;
    border-radius: 8px;
    height: 3em;
    width: 200px;
    font-weight: bold;
}

.stTextArea textarea {
    border-radius: 10px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #1e293b;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------- FUNCTIONS ----------

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def generate_ai_feedback(question, answer):
    text = answer.lower()
    words = text.split()

    good = []
    bad = []

    # -------- LENGTH --------
    if len(words) < 20:
        bad.append("⚠️ Answer is too short. Add more details.")
    elif len(words) > 80:
        bad.append("⚠️ Answer is too long. Keep it concise.")
    else:
        good.append("✅ Good answer length.")

    # -------- NAME CHECK --------
    if any(x in text for x in ["my name is", "i am", "i'm"]):
        good.append("✅ Good introduction with your name.")
    else:
        bad.append("⚠️ Start with your name and introduction.")

    # -------- SKILLS --------
    if any(x in text for x in ["python", "java", "skill", "development"]):
        good.append("✅ Skills are clearly mentioned.")
    else:
        bad.append("⚠️ Add your technical skills.")

    # -------- ACTION VERBS --------
    action_words = ["developed", "built", "created", "designed"]
    found_actions = [w for w in action_words if w in text]

    if found_actions:
        good.append(f"✅ Good action verbs used: {', '.join(found_actions)}")
    else:
        bad.append("⚠️ Use strong action verbs like 'developed', 'built'.")

    # -------- CAREER GOAL --------
    if "interested" in text or "goal" in text:
        good.append("✅ Career goal is mentioned.")
    else:
        bad.append("⚠️ Mention your career goal.")

    # -------- SENTIMENT --------
    sentiment = TextBlob(answer).sentiment.polarity
    if sentiment > 0:
        good.append("✅ Tone is positive.")
    else:
        bad.append("⚠️ Try to sound more confident and positive.")

    return good, bad
def calculate_score(answer):
    score = 0

    if len(answer.split()) > 30:
        score += 2

    if len(answer.split()) > 60:
        score += 1

    if "skill" in answer.lower():
        score += 2

    if "experience" in answer.lower():
        score += 2

    if TextBlob(answer).sentiment.polarity > 0:
        score += 1

    if "." in answer:  # basic structure check
        score += 1

    if any(word in answer.lower() for word in ["project", "team", "developed"]):
        score += 1

    return min(score, 10)

def save_data(question, answer, score):
    file = "history.csv"

    new_data = pd.DataFrame({
        "Question": [question],
        "Answer": [answer],
        "Score": [score]
    })

    if os.path.exists(file):
        old_data = pd.read_csv(file)
        new_data = pd.concat([old_data, new_data], ignore_index=True)

    new_data.to_csv(file, index=False)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("📂 Menu")

    st.info("Practice interview questions and improve your answers.")

    st.subheader("💡 Tips")
    st.write("""
    - Use Win + H for voice typing  
    - Give detailed answers  
    - Mention skills & experience  
    """)

# ---------- MAIN TITLE ----------
st.title("🤖 AI Interview Analyzer")
st.markdown("### 🚀 Practice your interview with smart feedback")
st.markdown("---")

# ---------- QUESTIONS ----------
questions = [
    "Tell me about yourself",
    "Why should we hire you?",
    "Describe a challenge you faced",
    "What are your strengths and weaknesses?"
]

question = st.selectbox("📌 Select Interview Question", questions)

st.info("🎤 Click inside box and press Win + H for voice typing")

# ---------- ANSWER ----------
st.markdown("## ✍️ Your Answer")
answer = st.text_area("Type your answer here...", height=150)

# ---------- RESUME ----------
st.markdown("## 📄 Resume Upload")
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded!")

    resume_text = extract_text_from_pdf(uploaded_file)

    words = len(resume_text.split())
    st.write(f"📊 Word Count: {words}")

    keywords = ["python", "java", "skills", "experience"]
    found = [k for k in keywords if k in resume_text.lower()]

    st.write("🔑 Keywords:", found)

    if len(found) < 2:
        st.warning("⚠️ Add more skills to your resume")
    else:
        st.success("✅ Good resume")

else:
    st.info("📌 Please upload your resume to analyze")

# ---------- ANALYSIS ----------
if st.button("🚀 Analyze Answer"):
    if not answer.strip():
        st.warning("⚠️ Please enter your answer")
    else:
        st.markdown("## 📊 Analysis Result")

        # SUCCESS MESSAGE
        st.success("✅ Analysis Completed Successfully!")

        word_count = len(answer.split())
        st.write(f"📝 Word Count: {word_count}")

        score = calculate_score(answer)

        save_data(question, answer, score)

        # SCORE DISPLAY
        st.metric("Score", f"{score}/10")
        st.progress(score / 10)

        # FEEDBACK
        st.markdown("## 🧠  Feedback")
        feedback = generate_ai_feedback(question, answer)

        for f in feedback:
            st.warning(f)

        # SENTIMENT
        st.markdown("## 😊 Sentiment Score")
        sentiment = TextBlob(answer).sentiment.polarity
        st.write(round(sentiment, 2))

# ---------- HISTORY ----------
st.markdown("## 📁 Previous Answers")

if os.path.exists("history.csv"):
    data = pd.read_csv("history.csv")
    st.dataframe(data)

    csv = data.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇️ Download Report",
        data=csv,
        file_name="report.csv"
    )

    if st.button("🗑 Clear History"):
        os.remove("history.csv")
        st.success("History cleared!")

else:
    st.info("No history yet")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("👨‍💻 Developed by You | 🚀 AI Interview Analyzer")