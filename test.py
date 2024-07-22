import os
import wave
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
from translate import Translator


# Path to the model directory
model_path = "src/vosk-model-small-en-us-0.15"

engine = pyttsx3.init()

translator = Translator(to_lang="es")

if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)


voices = engine.getProperty('voices')
for voice in voices:
    if 'spanish' in voice.languages or 'es' in voice.id:
        engine.setProperty('voice', voice.id)
        break

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
stream.start_stream()

print("Say something!")

try:
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_dict = json.loads(result)
            print("You said: ", result_dict['text'])
            
            str_fromAudio = str(result_dict['text'])
            try:
                translated_text = translator.translate(str_fromAudio)
                print("Translated: ", translated_text)
                engine.say(translated_text)
                engine.runAndWait()
            except Exception as e:
                engine.say("Translation failed")
                engine.runAndWait()
                print(f"Translation failed: {e}")


        else:
            partial_result = recognizer.PartialResult()
            partial_result_dict = json.loads(partial_result)
            print(f"Parcial: {partial_result_dict}")
            

except KeyboardInterrupt:
    print("Exiting...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
