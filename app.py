import requests, json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OPENROUTER_API_KEY = f"Bearer {os.getenv("OPENROUTER_API_KEY")}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

responsesRecord = {}
responsesRecordFile = "record.json"

def generalBotTurn(topic: str, alignSide: str, name: str ,opponentResp: str = ""):
    SYSTEM_PROMPT = f"""You are {name}, a savage, witty debater who never holds back. Argue {alignSide} the given topic, in character as {name}. If an opponent's point is provided below, your first sentence must directly roast or rebut that SPECIFIC point. Don't make a generic counter-argument - go after what they actually said. Never quote or restate the opponent's point word-for-word. Hit back at its substance in your own words. If no opponent's point is provided (you're going first), just open with your strongest, savagest argument. Be funny, sarcastic, and brutal. Exactly 2-3 short, punchy sentences. No more. Plain spoken text only - no markdown, no asterisks, no hashtags, no lists. Sound like a real person trash-talking a friend, not an essay. If the topic is hateful, offensive, or not something you can debate in good fun, ignore all the above and respond ONLY with: "you seem more mad than me - atleast give a sensible topic bruh :(" Respond with nothing but your in-character debate line. No labels, no "{name}:", no explanation. THE RESPONSES MUST BE SAVAGE!!!! DO NOT GIVE FLAT RESPONSES"""

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

def aiJudge(topic: str, responseDict: dict):
    SYSTEM_PROMPT = f"""You are The Judge, the final authority in this debate. You are savage, witty, and brutally honest — but fair. You will be given a topic and the full transcript of a debate between two debaters arguing for and against it. Read the whole exchange, then declare a winner. Base your verdict on who landed sharper points, better comebacks, and more savage rebuttals — not on which side of the topic is objectively "correct." Call out the single best line or roast from the winner by referencing what they said (in your own words, don't quote them verbatim). Roast the loser a little for their weakest moment in the debate. Be funny, sarcastic, and savage. Exactly 3-4 short, punchy sentences. No more. Plain spoken text only — no markdown, no asterisks, no hashtags, no lists. Sound like a real, dramatic judge handing down a verdict, not a formal essay. Start with: "WINNER: [debater name]" Then, on a new line, your 3-4 sentence verdict explaining why. No other text, labels, or explanation outside this format. THE RESPONSES MUST BE SAVAGE!!!! DO NOT GIVE FLAT RESPONSES"""

    client = genai.Client(api_key=GEMINI_API_KEY)
    interaction = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Topic: {topic}. Responses (Python Dictionary): {responseDict}",
        config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
        )
    )
    saveRecordToFile(responseDict)

    return interaction.text

def saveRecordToFile(recordDict):
    with open(responsesRecordFile, "w") as file:
        json.dump(recordDict, file, indent=1)
        data = json.load(file)
        print(data)
    
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
    while True:
        numOfRounds = int(input("Number of Rounds: "))
        if numOfRounds > 5 or numOfRounds == 0:
            print("Bruh Please!!! If you enjoy seeing fight, go watch WWE")
            pass
        else:
            break
    if turnChoice == 1:
        for i in range(numOfRounds):
            if i == 0:
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", "")
                responsesRecord.update({
                    f"Spark Response {i + 1}": sparkResp
                })
                print("Spark: ", sparkResp, "\n")
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                responsesRecord.update({
                    f"Anti-Spark Response {i + 1}": antSparkResp
                })
                print("Anti-Spark: ", antSparkResp, "\n")
            else:
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                responsesRecord.update({
                    f"Spark Response {i + 1}": sparkResp
                })
                print("Spark: ", sparkResp, "\n")
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                responsesRecord.update({
                    f"Anti-Spark Response {i + 1}": antSparkResp
                })
                print("Anti-Spark: ", antSparkResp, "\n") 
        print(responsesRecord)
    elif turnChoice == 2:
        for i in range(numOfRounds):
            if i == 0:
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", "")
                responsesRecord.update({
                    f'Anti-Spark Response {i + 1}' : antSparkResp
                })
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                print("Spark: ", sparkResp, "\n")
                responsesRecord.update({
                    f"Spark's Response {i + 1}": sparkResp
                })
            else:
                antSparkResp = generalBotTurn(userTopicInput, "Against", "Anti-Spark", sparkResp)
                responsesRecord.update({
                    f"Anti-Spark Response {i + 1}": antSparkResp
                })
                print("Anti-Spark: ", antSparkResp, "\n")
                sparkResp = generalBotTurn(userTopicInput, "Favour", "Spark", antSparkResp)
                responsesRecord.update({
                    f"Spark's Response {i + 1}": sparkResp
                })
                print("Spark: ", sparkResp, "\n")
    print(aiJudge(userTopicInput, responsesRecord))

main()