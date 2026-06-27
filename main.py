import requests, json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
from app import generalBotTurn, aiJudge, saveRecordToFile, rankEachResp

load_dotenv()

OPENROUTER_API_KEY = f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
responsesRecordFile = "record.json"

st.set_page_config("Yappening", "🗣️", layout="centered")
st.title("Yappening")
st.caption("Debating Platform for AI Bots")

st.sidebar.header("Debate Setup")
userTopicInput = st.sidebar.text_area("Enter Debate Topic", placeholder="Pizza, School, Iron Man etc")
turnChoice = st.sidebar.radio("Who should start first?", ("Spark(Favour)", "Anti-Spark (Against)"))
numOfRounds = st.sidebar.slider("Number of Rounds", min_value=1, max_value=5, value=2)

startDebate = st.sidebar.button("Launch Debate", use_container_width=True)

if "debate_transcript" not in st.session_state:
    st.session_state.debate_transcript = []
if "verdict" not in st.session_state:
    st.session_state.verdict = None

if startDebate:
    if not userTopicInput.strip():
        st.sidebar.error("Please enter a topic first :(")
    else:
        st.session_state.debate_transcript = []
        st.session_state.verdict = None
        responsesRecord = {}

        st.subheader(f"Debate Topic: *{userTopicInput}*")
        st.divider()

        sparkResp = ""
        antSparkResp = ""

        if "Favour" in turnChoice:
            firstSpeaker = "Spark"
            firstSide = "Favour"
            secondSpeaker = "Anti-Spark"
            secondSide = "Against"
        else:
            firstSpeaker = "Anti-Spark"
            firstSide = "Against"
            secondSpeaker = "Spark"
            secondSide = "Favour"
        
        for i in range(numOfRounds):
            st.markdown(f"### Round {i + 1}")

            if firstSpeaker == "Spark":
                opponentInp = antSparkResp
            else:
                opponentInp = sparkResp

            if firstSpeaker == "Spark":
                with st.chat_message("user"):
                    resp1 = generalBotTurn(userTopicInput, firstSide, firstSpeaker, opponentInp)
                    with st.spinner("Judging Response Strength..."):
                        score1 = rankEachResp(userTopicInput, resp1, opponentInp)
                    st.caption(f"**Argument Strength:** {score1}/10")
            else:
                with st.chat_message("assistant"):
                    resp1 = generalBotTurn(userTopicInput, firstSide, firstSpeaker, opponentInp)
                    with st.spinner("Judging Response Strength..."):
                        score1 = rankEachResp(userTopicInput, resp1, opponentInp)
                    st.caption(f"**Argument Strength:** {score1}/10")

            responsesRecord[f"{firstSpeaker} Response {i + 1}"] = {
                "text": resp1,
                "score": score1
            }

            if firstSpeaker == "Spark":
                sparkResp = resp1
            else:
                antSparkResp = resp1
            
            if secondSpeaker == "Anti-Spark":
                opponentInp = sparkResp
            else:
                opponentInp = antSparkResp
            
            if secondSpeaker == "Spark":
                with st.chat_message("user"):
                    resp2 = generalBotTurn(userTopicInput, secondSide, secondSpeaker, opponentInp)
                    with st.spinner("Judging Response Strength..."):
                        score2 = rankEachResp(userTopicInput, resp2, opponentInp)
                    st.caption(f"**Argument Strength:** {score2}/10")
            else:
                with st.chat_message("assistant"):
                    resp2 = generalBotTurn(userTopicInput, secondSide, secondSpeaker, opponentInp)
                    with st.spinner("Judging Response Strength..."):
                        score2 = rankEachResp(userTopicInput, resp2, opponentInp)
                    st.caption(f"**Argument Strength:** {score2}/10")
            
            responsesRecord[f"{secondSpeaker} Response {i + 1}"] = {
                "text": resp2,
                "score": score2
            }

            if secondSpeaker == "Anti-Spark":
                antSparkResp = resp2
            else:
                sparkResp = resp2
            
            st.divider()
        
        st.subheader("The Verdict")
        with st.chat_message("court"):
            verdict = aiJudge(userTopicInput, responsesRecord)
        
        if verdict:
            saveRecordToFile(responsesRecord, verdict)
            st.success(f"Debate Save at `{responsesRecordFile}`")
            st.session_state.debate_transcript = responsesRecord
            st.session_state.verdict = verdict

elif st.session_state.debate_transcript:
    st.subheader(f"Past Debate: *{userTopicInput}*")

    for key, value in st.session_state.debate_transcript.items():
        if "Spark" in key:
            speaker = "Spark"
        else:
            speaker = "Anti-Spark"
        
        if speaker == "Spark":
            with st.chat_message("user"):
                st.write(f"**{key}:** {value['text']}")
                st.caption(f"**Argument Strength:** {value['score']}/10")
        else:
            with st.chat_message("assistant"):
                st.write(f"**{key}:** {value['text']}")
                st.caption(f"**Argument Strength:** {value['score']}/10")

    st.divider()
    st.subheader("Saved Verdict")
    with st.chat_message("court"):
        st.write(st.session_state.verdict)