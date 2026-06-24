import requests, json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OPENROUTER_API_KEY = f"Bearer {os.getenv("OPENROUTER_API_KEY")}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def sparksTurn(userTopicInput: str, opponentsResponse: str = ""):
    client = genai.Client(api_key=GEMINI_API_KEY)
    interaction = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Topic: {userTopicInput}. Opponents Point of View/Debating Point: {opponentsResponse}",
        config=types.GenerateContentConfig(
        system_instruction="""You are Spark, a debater who is cocky, quick-witted, and a little unhinged. You're given a topic and, if present, your opponent's last argument. Your job: argue IN FAVOR of the topic. Rules: If your opponent made a point, directly mock or dismantle it before making your own point — don't ignore it. Be funny, sarcastic, and savage, but never genuinely mean-spirited or offensive. 2-3 short punchy sentences max. No lists, no markdown, no asterisks or hashtags. Sound like a real person trash-talking, not a formal essay. If the topic is offensive, hateful, or not a real debate-able topic, respond only with: "you seem more mad than me - atleast give a sensible topic bruh :( Respond to opponents point but don't reqrite/add it in the responses as it is. Don't expect to be given opponents point each time - you are still suppose to answer"""
        )
    )

    if interaction.text:
        return interaction.text
    else:
        print("OpenRouter Error: ", favourResponse)
        print("Spark is gaining more knowledge - let's contact his brother Sparkimini")
        favourResponse = requests.post(
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
                    "content": """You are Spark, a debater who is cocky, quick-witted, and a little unhinged. You're given a topic and, if present, your opponent's last argument. Your job: argue IN FAVOR of the topic. Rules: If your opponent made a point, directly mock or dismantle it before making your own point — don't ignore it. Be funny, sarcastic, and savage, but never genuinely mean-spirited or offensive. 2-3 short punchy sentences max. No lists, no markdown, no asterisks or hashtags. Sound like a real person trash-talking, not a formal essay. If the topic is offensive, hateful, or not a real debate-able topic, respond only with: "you seem more mad than me - atleast give a sensible topic bruh :( Respond to opponents point but don't reqrite/add it in the responses as it is. Don't expect to be given opponents point each time - you are still suppose to answer"""
                    },
                    {
                        "role": "user",
                        "content": f"Topic: {userTopicInput}. Opponents Point of View/Debating Point: {opponentsResponse}"
                    },
                ]
            })
        )
        
        favourData = favourResponse.json()
        return favourData["choices"][0]["message"]["content"]



def antiSparksTurn(userTopicInput: str, opponentsResponse: str = ""):
    client = genai.Client(api_key=GEMINI_API_KEY)
    interaction = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Topic: {userTopicInput}. Opponents Point of View/Debating Point: {opponentsResponse}",
        config=types.GenerateContentConfig(
        system_instruction="""You are Anti-Spark, a debater who is dry, deadpan, and brutally logical. You're given a topic and your opponent's last argument. Your job: argue AGAINST the topic. Rules: Directly rebut your opponent's specific point before making your own — never ignore what they said. Be funny, sarcastic, and savage, but never genuinely mean-spirited or offensive. 2-3 short punchy sentences max. No lists, no markdown, no asterisks or hashtags. Sound like a real person trash-talking, not a formal essay. If the topic is offensive, hateful, or not a real debate-able topic, respond only with: "you seem more mad than me - atleast give a sensible topic bruh :(  Respond to opponents point but don't reqrite/add it in the responses as it is. Don't expect to be given opponents point each time - you are still suppose to answer"""
        )
    )

    if interaction.text:
        return interaction.text
    else:
        print("OpenRouter Error: ", againstResponse)
        print("Anti-Spark is gaining more knowledge - let's contact his brother Anti-Sparkimini")
        againstResponse = requests.post(
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
                        "content": """You are Anti-Spark, a debater who is dry, deadpan, and brutally logical. You're given a topic and your opponent's last argument. Your job: argue AGAINST the topic. Rules: Directly rebut your opponent's specific point before making your own — never ignore what they said. Be funny, sarcastic, and savage, but never genuinely mean-spirited or offensive. 2-3 short punchy sentences max. No lists, no markdown, no asterisks or hashtags. Sound like a real person trash-talking, not a formal essay. If the topic is offensive, hateful, or not a real debate-able topic, respond only with: "you seem more mad than me - atleast give a sensible topic bruh :(  Respond to opponents point but don't reqrite/add it in the responses as it is. Don't expect to be given opponents point each time - you are still suppose to answer"""
                    },
                    {
                        "role": "user",
                        "content": f"Topic: {userTopicInput}. Opponents Point of View/Debating Point: {opponentsResponse}"
                    },
                ]
            })
        )

        againstData = againstResponse.json()
        return againstData["choices"][0]["message"]["content"]


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
                sparkResp = sparksTurn(userTopicInput)
                print("Spark: ", sparkResp, "\n")
                antSparkResp = antiSparksTurn(userTopicInput, sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n")
            else:
                sparkResp = sparksTurn(userTopicInput, antSparkResp)
                print("Spark: ", sparkResp, "\n")
                antSparkResp = antiSparksTurn(userTopicInput, sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n")
    elif turnChoice == 2:
        for i in range(3):
            if i == 0:
                antSparkResp = antiSparksTurn(userTopicInput)
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = sparksTurn(userTopicInput, antSparkResp)
                print("Spark: ", sparkResp, "\n")
            else:
                antSparkResp = antiSparksTurn(userTopicInput, sparkResp)
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = sparksTurn(userTopicInput, antSparkResp)
                print("Spark: ", sparkResp, "\n")


main()