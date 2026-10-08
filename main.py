
import os
from io import BytesIO

import speech_recognition as sr
import sounddevice as sd
import soundfile as sf

from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


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
                            "style": "Speak in a cheerful, warm, "
                                     "delighted and friendly manner."
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

    for candidate in response.candidates:
        for part in candidate.content.parts:
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
    sd.play(audio, samplerate=sample_rate)
    sd.wait()

    print("Audio playback completed.")


# Main Voice Agent
def main():
    r = sr.Recognizer()
    while True:
      with sr.Microphone() as source:
          r.adjust_for_ambient_noise(source)
          r.pause_threshold = 2

          print("Say something...")
          audio = r.listen(source)

      try:
          print("Processing audio...(STT)")

          # Speech to Text
          stt = r.recognize_google(audio)

          print("You said:", stt)

          SYSTEM_PROMPT = """
          You're an expert voice agent.
          You are given the transcript of what the user has
          said using voice.

          Respond naturally and conversationally.
          Keep your response concise and suitable for
          spoken audio.
          Respond in the same language as the user.
          """

          # Gemini LLM using OpenAI-compatible API
          response = client.chat.completions.create(
              model="gemini-3.6-flash",
              messages=[
                  {
                      "role": "system",
                      "content": SYSTEM_PROMPT
                  },
                  {
                      "role": "user",
                      "content": stt
                  }
              ]
          )

          ai_response = response.choices[0].message.content

          if not ai_response:
              print("No response generated.")
              return

          print("AI response:", ai_response)

          # Text to Speech
          tts(speech=ai_response)

      except sr.UnknownValueError:
          print("Could not understand the audio.")

      except sr.RequestError as e:
          print("Speech recognition error:", e)

      except Exception as e:
          print("Voice Agent Error:", e)


if __name__ == "__main__":
    main()