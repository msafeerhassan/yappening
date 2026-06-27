import requests, json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
from openrouter import OpenRouter

load_dotenv()

OPENROUTER_API_KEY = f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

responsesRecord = {}
responsesRecordFile = "record.json"

def generalBotTurn(topic: str, alignSide: str, name: str , personality, opponentResp: str = ""):
    SYSTEM_PROMPT = f"""You are {name}. YOUR MAIN PERSONALITY IS {personality}.Argue {alignSide} the given topic, in character as {name}. If an opponent's point is provided below, your first sentence must directly rebut that SPECIFIC point. Don't make a generic counter-argument - go after what they actually said. Never quote or restate the opponent's point word-for-word. Hit back at its substance in your own words. If no opponent's point is provided (you're going first), just open with your strongest argument. Be as per your personality: {personality}. Exactly 2-3 short, punchy sentences. No more. Plain spoken text only - no markdown, no asterisks, no hashtags, no lists. Sound like a real person trash-talking a friend, not an essay. If the topic is hateful, offensive, or not something you can debate in good fun, ignore all the above and respond ONLY with: "you seem more mad than me - atleast give a sensible topic bruh :(" Respond with nothing but your in-character debate line. No labels, no "{name}:", no explanation."""

    try:
        client = OpenRouter(
            api_key=OPENROUTER_API_KEY,
            server_url="https://ai.hackclub.com/proxy/v1"
        )

        response = client.chat.send(
            model="google/gemini-3.1-flash-lite",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Topic: {topic}. Opponents Point of View/Debating Point: {opponentResp}"
                }
            ],
            stream=True
        )

        placeholder = st.empty()
        fullResp = ""

        for chunk in response:
            fullResp += chunk.text
            placeholder.markdown(f"**{name}:** {fullResp}")
        
        return fullResp
    except Exception:
        client = genai.Client(api_key=GEMINI_API_KEY)
        interaction = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite",
            contents=f"Topic: {topic}. Opponents Point of View/Debating Point: {opponentResp}",
            config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
            )
        )
        placeholder = st.empty()
        fullResp = ""

        for chunk in interaction:
            fullResp += chunk.text
            placeholder.markdown(f"**{name}:** {fullResp}")
        return fullResp

def aiJudge(topic: str, responseDict: dict):
    SYSTEM_PROMPT = f"""You are The Judge, the final authority in this debate. You are savage, witty, and brutally honest — but fair. You will be given a topic and the full transcript of a debate between two debaters arguing for and against it. Read the whole exchange, then declare a winner. Base your verdict on who landed sharper points, better comebacks, and more savage rebuttals — not on which side of the topic is objectively "correct." Call out the single best line or roast from the winner by referencing what they said (in your own words, don't quote them verbatim). Roast the loser a little for their weakest moment in the debate. Be funny, sarcastic, and savage. Exactly 3-4 short, punchy sentences. No more. Plain spoken text only — no markdown, no asterisks, no hashtags, no lists. Sound like a real, dramatic judge handing down a verdict, not a formal essay. Start with: "WINNER: [debater name]" Then, on a new line, your 3-4 sentence verdict explaining why. No other text, labels, or explanation outside this format. THE RESPONSES MUST BE SAVAGE!!!! DO NOT GIVE FLAT RESPONSES"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        interaction = client.models.generate_content_stream(
            model="gemini-3.1-flash-lite",
            contents=f"Topic: {topic}. Responses (Python Dictionary): {responseDict}",
            config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
            )
        )

        placeholder = st.empty()
        fullResp = ""
        for chunk in interaction:
            fullResp += chunk.text
            placeholder.markdown(f"**Judge:** {fullResp}")
        return fullResp
    except Exception as e:
        st.error(f"AI Judge absent :( : {e}")
        return None

def saveRecordToFile(recordDict: dict, verDict):
    dataToSave = {
        "debate_history": recordDict,
        "judge_verdict": verDict
    }
    with open(responsesRecordFile, "w") as file:
        json.dump(dataToSave, file, indent=1)

def rankEachResp(topic, resp, opponentResp):
    SYSTEM_PROMPT = "You are an AI Judge. You will be given an AI Bot response in a debate on a specific topic and you will be also given opponent's response in some cases. You will analyze the response from every perspective acting totally neutral - you will have to analyze on the basis of the strength of argument rather than logic because it's fun debate. Then you will JUST RETURN INTEGER VALUE RANKING THE RESPONSE OUT OF 10 - NOTHING ELSE. No markdown, no asterisks, no hashtags, no lists. Just a simple integer from 1 - 10!!!!!. Example Response: '4'"
    try:
        client = OpenRouter(
            api_key=OPENROUTER_API_KEY,
            server_url="https://ai.hackclub.com/proxy/v1"
        )

        response = client.chat.send(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Topic: {topic} | AI Bot Response: {resp} | Opponent's Previous Response: {opponentResp}"
                }
            ],
            stream=False
        )

        content = response.choices[0].message.content

        return content.strip()
    except:
        client = genai.Client(api_key=GEMINI_API_KEY)
        interaction = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=f"Topic: {topic} | AI Bot Response: {resp} | Opponent's Previous Response: {opponentResp}",
            config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
            )
        )
        return interaction.text.strip()