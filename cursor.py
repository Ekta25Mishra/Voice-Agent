from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
from pydantic import BaseModel, Field
from typing import Optional
import os
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from google import genai


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = OpenAI(
  api_key=GOOGLE_API_KEY,
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
  )

def run_command(cmd:str):
  result = os.system(cmd)
  return result


def get_weather(city:str):
  url = f"https://wttr.in/{city.lower()}?format=%C+%t"
  response = requests.get(url)

  if response.status_code == 200:
    return f"The weather in {city} is {response.text}"
  return "Something went wrong"

available_tools = {
  "get_weather":get_weather,
  "run_command":run_command
}


# Native Gemini client for TTS
tts_client = genai.Client(api_key=GOOGLE_API_KEY)


# Text to Speech
def tts(speech: str):
    print("Generating audio...")

    response = tts_client.models.generate_content(
        model="gemini-3.8-flash-tts",
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": speech,
                        "speech_metadata": {
                            "style": "Speak in a cheerful, warm, delighted and friendly manner."
                        }
                    }
                ]
            }
        ],
        config={
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "voice": "Kore"
                }
            }
        }
    )

    # Extract generated audio
    audio_data = None

    for candidate in response.candidates or []:

        # Candidate may not contain content
        if candidate.content is None:
            continue

        for part in candidate.content.parts or []:

            if part.inline_data and part.inline_data.data:
                audio_data = part.inline_data.data
                break

        if audio_data:
            break

    if not audio_data:
        raise RuntimeError("Gemini did not return any audio.")

    # Read WAV audio from memory
    audio, sample_rate = sf.read(
        BytesIO(audio_data),
        dtype="int16"
    )

    # Play audio
    print("Playing audio...")

    sd.play(
        audio,
        samplerate=sample_rate
    )

    sd.wait()

    print("Audio playback completed.")


system_instruction="""
Yor're an expert AI Assistent in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You ned to first PLAN what needs to be done. The PLAN can be of multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.
You can also call a tool if required from the list of available tools.
For every tool call wait for the observe step which is the output from the called tool.

RULES:
- Strictly follow the given JSON output format.
- Only run one step at a time.
- The sequence of steps is START (where user gives an input) , PLAN  and finally OUTPUT (which is going to the displayed to the user).
-Use the minimum number of PLAN steps necessary.
-For simple questions, use only 1 PLAN step.
-For complex questions, use multiple PLAN steps.
-Do not create unnecessary PLAN steps just to make the reasoning longer.

Output JSON Format:
{"step":"START" | "PLAN" | "OUTPUT" | "TOOL" , "content":"string", "tool":"string", "input":"string"} 

Available Tools:
- get_weather(city:str): Takes city name as input string and returns weather info about that city.
-run_command(cmd:str): Takes a system linux command as string and executes the command on the user's system and returns the output from that command.

Example 1:
START: Hey, Can you solve 2+3*5/10
PLAN: {"step":"PLAN": "content":"Seems like user is interested in maths problem"}
PLAN:{"step": "PLAN": "content":"looking at the problem, we should solve this using BODMAS method"}
PLAN:{"step":"PLAN":"content":"yes, the BODMAS is correct thing to be done here"}
PLAN:{"step":"PLAN":"output":"first we multiply 3*5 which is 15"}
PLAN:{"step":"PLAN":"content":"Now the new equation is 2+15/10"}
PLAN:{"step":"PLAN":"content":"we must perform divide that is 15/10=1.5"}
PLAN:{"step":"PLAN","content":"now the equation is 2+1.5"}
PLAN:{"step":"PLAN","content":"finally we add 2+1.5=3.5"}
OUTPUT:{"step":"OUTPUT","content":"The result of 2+3*5/10 is 3.5"}


Example 2:
START: What is the weather of Delhi?
PLAN: {"step":"PLAN": "content":"Seems like user is interested in getting weather of Delhi in India."}
PLAN:{"step": "PLAN": "content":"Lets see if we have any available tool from the list of available tools."}
PLAN:{"step":"PLAN":"content":"great, we have get_weather tool available for this query."}
PLAN:{"step":"PLAN":"output":"I need to call get_weather tool for Delhi as input for city."}
PLAN:{"step":"TOOL":"tool":"get_weather":"input":"delhi"}
PLAN:{"step":"OBSERVE":"tool":"get_weather":"output":"The temperature of Delhi is cloudy with 15 C."}
PLAN:{"step":"PLAN","content":"Great, I got the weather info about Delhi."}
OUTPUT:{"step":"OUTPUT","content":"The current weather in delhi is 15  with some cloudy sky."}
"""


print("\n\n\n")

class MyOutpurFormat(BaseModel):
  step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc.")
  content: Optional[str] = Field(None, description="The option string content of the step.")
  tool:Optional[str] = Field(None, description="The ID of the tool to call")
  input:Optional[str] = Field(None, description="The input params for the tool")



message_history= [
  {"role":"system", "content":system_instruction}
]

r = sr.Recognizer()
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    r.pause_threshold = 2

    while True:
      print("Say something...")

      try:
        audio = r.listen(
            source,
            timeout=None,
            phrase_time_limit=10
        )

        print("Processing audio...(STT)")

        user_query = r.recognize_google(audio)

        print("You:", user_query)
        
      except sr.UnknownValueError:
        print("Could not understand audio. Try again.")
        continue

      except sr.RequestError as e:
        print("Speech recognition service error:", e)
        continue

      message_history.append({
        "role": "user",
        "content": user_query
    })

      while True:
        response = client.chat.completions.parse(
        model="gemini-3.8-flash",
        response_format=MyOutpurFormat,
        messages=message_history
      )
        raw_result = response.choices[0].message.content
        print("\nRAW:", raw_result)

        try:
          parsed_result =  response.choices[0].message.parsed
        except json.JSONDecodeError:
          print("❌ Invalid JSON from model:")
          print(raw_result)
          break
        
        step = parsed_result.step  



        if step == "START":
          print("🔥", parsed_result.content)
          message_history.append(
        {
          "role":"assistant", 
          "content":raw_result
        }
      )
          continue
        if step == "PLAN":
          print("🧠", parsed_result.content)
          message_history.append({
                "role": "assistant",
                "content": raw_result
            })
          message_history.append({
                "role": "user",
                "content": "Continue to the next step."
            })
          continue
        if step == "TOOL":
          tool_to_call = parsed_result.tool
          tool_input = parsed_result.input
          print(f"⚓:{tool_to_call} ({tool_input})")

          if tool_to_call not in available_tools:
            print(f"❌ Tool {tool_to_call} not found in available tools.")
            break

          tool_response = available_tools[tool_to_call](tool_input)
          print(f"⚓:{tool_to_call} ({tool_input}) = {tool_response}")

          message_history.append({
                "role": "assistant",
                "content": raw_result
            })


          message_history.append({ "role":"user" , "content":json.dumps({
          "step":"OBSERVE", "tool":tool_to_call, "input":tool_input, "output":tool_response
        })
        })
          continue 
        if step == "OUTPUT":
          print("🤖", parsed_result.content)
          tts(speech=parsed_result.content)
          break



      print("\n\n\n")


