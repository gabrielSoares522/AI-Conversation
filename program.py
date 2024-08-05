import speech_recognition as sr
from datetime import date
from time import sleep
from gtts import gTTS
from playsound import playsound
import os
import pathlib
import openai
import json

class Conversation:
    def __init__(self):
        with open('openai.key', 'r') as file:
            openai.api_key = file.read().rstrip()

        self.languages=["es-ES","en-US","pt-BR"]
        self.language = self.languages[2]

        match self.language:
            case 'en-US':
                self.messages = [{"role": "system", "content": "You are a helpful assistant called Sarah."}]
            case 'es-ES':
                self.messages = [{"role": "system", "content": "Eres una asistente útil llamada Sara."}]
            case 'pt-BR':
                self.messages = [{"role": "system", "content": "Você é um assistente prestativa chamada Sarah."}]
            case _:
                self.messages = [{"role": "system", "content": "You are a helpful assistant called Sarah."}]
        
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()#device_index=2)
    
    def addMessage(self, message, role):
        self.messages.append({"role": role, "content": message})
        print(role+": "+message)

    def getAnswer(self,dummy=False):
        if dummy:
            match self.language:
                case 'en-US':
                    return json.loads('{"choices": [{"message": {"content": "Sorry, I didn\'t understand. Can you repeat?"}}]}')
                case 'es-ES':
                    return json.loads('{"choices": [{"message": {"content": "Lo siento, no entendí. ¿Puede repetir?"}}]}')
                case 'pt-BR':
                    return json.loads('{"choices": [{"message": {"content": "Desculpe, não entendi. Pode repetir?"}}]}')
                case _:
                    return json.loads('{"choices": [{"message": {"content": "Sorry, I didn\'t understand. Can you repeat?"}}]}')
        else:
            return openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                temperature=1,
                max_tokens=200
            )

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def generateNameRandom(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def setLanguage(self, languageIndex):
        self.language = self.languages[languageIndex]
        print("Language changed to "+self.language)
    
    def generateAudio(self, text):
        myobj = gTTS(text=text, lang = self.language.split("-")[0], slow=False)
        fileName = self.generateNameRandom()+".mp3"
        filePath = os.path.dirname(os.path.abspath(__file__))+"/audios/"+fileName
        myobj.save(filePath)
        return filePath
    
    def main(self):
        self.clear()
        print("Starting...")

        while True:
            words = ""
            dontSendMessage = False
            with self.mic as source:
                audio = self.r.listen(source)

            try:
                words = self.r.recognize_google(audio, language=self.language)
                self.addMessage(words, "user")
            except sr.UnknownValueError:
                dontSendMessage = True
                print("???")
            except sr.RequestError:
                print("Internet disconnected")
                dontSendMessage = True
            except sr.WaitTimeoutError:
                print("I can't hear you")
                dontSendMessage = True
            except sr.HTTPError:
                print("HTTP error")
                dontSendMessage = True
            except sr.URLError:
                print("URL error")
                dontSendMessage = True
            except sr.RequestTimeout:
                print("Timeout")
                dontSendMessage = True
            except sr.TooLargeError:
                print("Too much large")
                dontSendMessage = True
            except Exception as e:
                print(e)
                dontSendMessage = True
            
            if dontSendMessage or words == "":
                continue

            if words == "today" or words == "hoje" or words == "hoy":
                print(date.today())
            
            if words == "change to english" or words == "cambiar a inglés" or words == "mudar para inglês":
                self.setLanguage(1)
                print("Language changed to English")

            if words == "change to spanish" or words == "cambiar a español" or words == "mudar para espanhol":
                self.setLanguage(0)
                print("Language changed to Spanish")

            if words == "change to portuguese" or words == "cambiar a portugués" or words == "mudar para português":
                self.setLanguage(2)
                print("Language changed to Portuguese")
            
            if words == "exit" or words == "quit" or words =="sair" or words == "fechar" or words =="salir" or words == "cerrar":
                for i in range(3):
                    print("...")
                    sleep(1)
                
                print("Goodbye")
                break
            
            response = self.getAnswer(dummy=True)
            wordsResponse = response['choices'][0]['message']["content"]
            self.addMessage(wordsResponse, "system")
            
            filePath = self.generateAudio(wordsResponse)
            playsound(filePath)

controller = Conversation()
controller.main()