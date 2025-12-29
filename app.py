import streamlit as st
import csv
import os
import time
import random

# ---------- File Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "dataset.csv")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    data = []
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# ---------- Logic Functions ----------
def get_all_symptoms(data):
    symptoms_set = set()
    for row in data:
        # Splitting by common delimiters to get individual keywords if necessary
        s_list = row["Symptoms"].replace(",", " ").split()
        for s in s_list:
            symptoms_set.add(s.lower().strip())
    return sorted(symptoms_set)

def find_disease(selected_symptom, data):
    results = []
    for row in data:
        if selected_symptom.lower() in row["Symptoms"].lower():
            results.append({
                "Disease": row["Disease"],
                "Medications": row["Medications"],
                "Precautions": row["Precautions"],
                "Doctor_Specialist": row["Doctor_Specialist"]
            })
    return results

# ---------- Streamlit UI Configuration ----------
st.set_page_config(page_title="MediMind AI Pro", page_icon="🩺", layout="centered")

# --- INJECT CSS ---
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("CSS file not found. Please ensure 'style.css' is in the same directory.")

# ---------- App Header ----------
st.markdown("<h1>🩺 MediMind AI Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: -20px;'>Advanced Diagnostic Intelligence</p>", unsafe_allow_html=True)

data = load_data()
symptom_list = get_all_symptoms(data)

# --- SEARCH SECTION ---
with st.container():
    st.subheader("🔍 Search by Symptom")
    selected_symptom = st.selectbox("How are you feeling today?", ["Select a symptom..."] + symptom_list)

    if st.button("Analyze Condition"):
        if selected_symptom != "Select a symptom...":
            matches = find_disease(selected_symptom, data)
            if matches:
                st.success(f"Analysis complete. Found {len(matches)} match(es).")
                for m in matches:
                    st.markdown(f"### 🦠 Disease: {m['Disease']}")
                    st.markdown(f"💊 **Medications:** {m['Medications']}")
                    st.markdown(f"🛡️ **Precautions:** {m['Precautions']}")
                    st.markdown(f"👨‍⚕️ **Specialist:** {m['Doctor_Specialist']}")
                    st.markdown("---")
            else:
                st.error("❌ No disease found in our current database.")
        else:
            st.warning("Please select a valid symptom first.")

st.divider()

# --- CHATBOT SECTION ---
st.subheader("💬 Health Assistant Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ex: I have a persistent cough..."):
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Logic to detect symptom from chat
    detected_symptom = None
    for s in symptom_list:
        if s.lower() in prompt.lower():
            detected_symptom = s
            break 

    with st.chat_message("assistant"):
        if detected_symptom:
            matches = find_disease(detected_symptom, data)
            m = matches[0] # Take the top match
            
            # Randomized Response Construction
            openings = [f"I'm sorry you're dealing with {detected_symptom}.", f"It sounds like {detected_symptom} is the issue."]
            findings = [f"This is often associated with **{m['Disease']}**.", f"My data suggests this points toward **{m['Disease']}**."]
            meds = [f"Common treatments include {m['Medications']}.", f"Standard medications for this are {m['Medications']}."]
            precautions = [f"For better recovery, try to: {m['Precautions']}.", f"You should follow these precautions: {m['Precautions']}."]
            specialists = [f"I recommend consulting a **{m['Doctor_Specialist']}**.", f"It would be best to see a **{m['Doctor_Specialist']}** for professional advice."]
            
            assistant_reply = (
                f"{random.choice(openings)} {random.choice(findings)} "
                f"{random.choice(meds)} {random.choice(precautions)} "
                f"{random.choice(specialists)} Please consult a professional for a final diagnosis."
            )
        else:
            assistant_reply = "I couldn't identify a specific symptom from that description. Could you try using a keyword like 'fever' or 'headache'?"

        # Simulated typing effect
        message_placeholder = st.empty()
        full_response = ""
        for chunk in assistant_reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
