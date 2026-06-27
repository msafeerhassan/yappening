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
debatingPeopleChoice = st.sidebar.radio("Should it be You VS AI or AI VS AI?", ("You VS AI", "AI VS AI"))
numOfRounds = st.sidebar.slider("Number of Rounds", min_value=1, max_value=5, value=2)

if "debate_transcript" not in st.session_state:
    st.session_state.debate_transcript = []
if "verdict" not in st.session_state:
    st.session_state.verdict = None
if "setup_step" not in st.session_state:
    st.session_state.setup_step = False

next = st.sidebar.button("Next >", use_container_width=True)


if next:
    if not userTopicInput.strip():
        st.sidebar.error("Please enter a topic first :(")
    else:
        st.session_state.setup_step = True
        st.session_state.debate_transcript = []
        st.session_state.verdict = None
if st.session_state.setup_step and userTopicInput.strip():
    st.subheader(f"Debate Topic: *{userTopicInput}*")
    st.divider()
    responsesRecord = {}
    if "AI VS AI" in debatingPeopleChoice:
        turnChoice = st.sidebar.radio("Who should start first?", ("Spark(Favour)", "Anti-Spark (Against)"))
        start = st.sidebar.button("Start Debate", use_container_width=True)

        if start:
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
    else:
        if "user_transcript" not in st.session_state:
            st.session_state.user_transcript = []
    
        for chat in st.session_state.user_transcript:
            with st.chat_message(chat["role"]):
                st.write(chat["text"])
                if "score" in chat:
                    st.caption(f"**Argument Strength:** {chat['score']}/10")
    
        if len(st.session_state.user_transcript) < (numOfRounds * 2):
            userInput = st.chat_input("Enter your debating point...")
            if userInput:
                with st.chat_message("user"):
                    st.write(userInput)
                    with st.spinner("Judging Your Response Strength..."):
                        if st.session_state.user_transcript:
                            prevAItext = st.session_state.user_transcript[-1]["text"]
                        else:
                            prevAItext = ""
                        userScore = rankEachResp(userTopicInput, userInput, prevAItext)
                    st.caption(f"**Argument Strength:** {userScore}/10")
            
                st.session_state.user_transcript.append({
                    "role": "user",
                    "text": userInput,
                    "score": userScore
                })

                with st.chat_message("assistant"):
                    aiResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", userInput)
                    with st.spinner("Judging Response Strength..."):
                        aiScore = rankEachResp(userTopicInput, aiResp, userInput)
                    st.caption(f"**Argument Strength:** {aiScore}/10")
            
                st.session_state.user_transcript.append({
                    "role": "assistant",
                    "text": aiResp,
                    "score": aiScore
                })

                st.rerun()
        else:
            if not st.session_state.verdict:
                st.subheader("The Verdict")
                formattedRecords = {}
                for idx, chat in enumerate(st.session_state.user_transcript):
                    if chat['role'] == "user":
                        speakerName = "You"
                    else:
                        speakerName = "Anti-Spark"
                    formattedRecords[f"{speakerName} Turn {idx + 1}"] = {
                        "text": chat['text'],
                        "score": chat['score']
                    }
                with st.chat_message("court"):
                    verdict = aiJudge(userTopicInput, formattedRecords)
                if verdict:
                    st.session_state.verdict = verdict
                    saveRecordToFile(formattedRecords, verdict)
            else:
                st.subheader("The Verdict")
                with st.chat_message("court"):
                    st.write(st.session_state.verdict)
elif st.session_state.debate_transcript:
    st.subheader(f"Past Debate: *{userTopicInput}*")
    for key, value in st.session_state.debate_transcript.items():
        if "Spark" in key and "Anti-Spark" not in key:
            speaker = "Spark"
        else:
            speaker = "Anti-Spark"
        
        if speaker == "Spark":
            role = "user"
        else:
            role = "assistant"
        with st.chat_message(role):
            st.write(f"**{key}:** {value['text']}")
            st.caption(f"**Argument Stength:** {value['score']}/10")
    st.divider()

    st.subheader("Saved Verdict")
    with st.chat_message("court"):
        st.write(st.session_state.verdict)