import requests, json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OPENROUTER_API_KEY = f"Bearer {os.getenv("OPENROUTER_API_KEY")}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generalBotTurn(topic: str, alignSide: str, name: str ,opponentResp: str = ""):
    SYSTEM_PROMPT = f"""You are {name}, a debater who is dry, deadpan, and brutally logical. You're given a topic and your opponent's last argument. Your job: argue {alignSide} the topic. Rules: Directly rebut your opponent's specific point before making your own — never ignore what they said. Be funny, sarcastic, and savage. 2-3 short punchy sentences max. No lists, no markdown, no asterisks or hashtags. Sound like a real person trash-talking, not a formal essay. If the topic is offensive, hateful, or not a real debate-able topic, respond only with: "you seem more mad than me - atleast give a sensible topic bruh :(  Respond to opponents point but don't reqrite/add it in the responses as it is. Don't expect to be given opponents point each time - you are still suppose to answer"""

    client = genai.Client(api_key=GEMINI_API_KEY)
    interaction = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Topic: {topic}. Opponents Point of View/Debating Point: {opponentResp}",
        config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
        )
    )

    if interaction.text:
        return interaction.text
    else:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": OPENROUTER_API_KEY,
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "cohere/north-mini-code:free",
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Topic: {topic}. Opponents Point of View/Debating Point: {opponentResp}"
                    },
                ]
            })
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

def main():
    userTopicInput = input("Enter the topic: ")
    print("\n")
    while True:
        turnChoice = int(input("""Who should start first: 
[1]: Spark (Favour)
[2]: Anti-Spark (Against): """))
        if turnChoice != 1 and turnChoice != 2:
            print("Please either choose 1 or 2!")
            pass
        else:
            break
    
    if turnChoice == 1:
        for i in range(3):
            if i == 0:
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", "")
                print("Spark: ", sparkResp, "\n")
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n")
            else:
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                print("Spark: ", sparkResp, "\n")
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n") 
    elif turnChoice == 2:
        for i in range(3):
            if i == 0:
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", "")
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                print("Spark: ", sparkResp, "\n")
            else:
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                print("Spark: ", sparkResp, "\n")

main()