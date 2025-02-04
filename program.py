import speech_recognition as sr
from datetime import date
from time import sleep
from gtts import gTTS
from playsound import playsound
import os
import pathlib
import json
import requests

class Conversation:
    languages = ["en-US","es-ES","pt-BR"]
    
    def __init__(self):
        self.language = self.languages[0]

        if self.language == 'en-US':
            self.messages = [{"role": "user", "content": "You are an assistant named Sarah and you must respond when spoken to."},
        {"role": "assistant", "content": "Thank you! I'm here to help with any questions or needs you may have. What do you want me to do for you?"}]
        elif self.language == 'es-ES':
            self.messages = [{"role": "system", "content": "Eres una asistente útil llamada Sara."}]
        elif self.language == 'pt-BR':
            self.messages = [{"role": "system", "content": "Eu sou um assistente prestativa chamada Sarah."}]
    
    def addMessage(self, message, role):
        self.messages.append({"role": role, "content": message})
        print(role+": "+message)

    def getAnswer(self):
        url = 'http://127.0.0.1:1234/v1/chat/completions'
        body = {
            "model": "deepseek-chat",
            "messages": self.messages,
            "stream": False
        }

        x = requests.post(url, json = body)
        return x

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
        filePath = os.path.dirname(os.path.abspath(__file__))+"\\audios\\"+fileName
        myobj.save(filePath)
        return filePath

    def main(self):
        self.clear()

        r = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            r.adjust_for_ambient_noise(source) 

        print("Starting...")

        
        while True:
            words = ""
            dontSendMessage = False

            with mic as source:
                print("listening...")
                audio = r.listen(source)
            
            try:
                words = r.recognize_google(audio, language=self.language)
                self.addMessage(words, "user")
            except sr.UnknownValueError:
                dontSendMessage = True
                print("I can't understand you")
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
                print("error: ",e)
                dontSendMessage = True
            
            if dontSendMessage or words == "":
                continue

            words = words.lower()
            
            try:
                if words.find("open") == 0:
                    programName = words[5:]
                    print("Opening "+programName+"...")
                    os.system("start "+programName)#+"://")
                    continue
                #subprocess.Popen(['C:\Program Files\Mozilla Firefox\\firefox.exe', '-new-tab'])
            except Exception as e:
                print("open error: ", e)

            if words == "today" or words == "hoje" or words == "hoy":
                print(date.today())
                continue
            
            if words == "change to english" or words == "cambiar a inglés" or words == "mudar para inglês":
                self.setLanguage(1)
                print("Language changed to English")
                continue

            if words == "change to spanish" or words == "cambiar a español" or words == "mudar para espanhol":
                self.setLanguage(0)
                print("Language changed to Spanish")
                continue

            if words == "change to portuguese" or words == "cambiar a portugués" or words == "mudar para português":
                self.setLanguage(2)
                print("Language changed to Portuguese")
                continue
            
            if words == "exit" or words == "quit" or words =="sair" or words == "fechar" or words =="salir" or words == "cerrar":
                for i in range(3):
                    print("...")
                    sleep(1)
                
                print("Goodbye")
                break
            
            response = self.getAnswer()
            wordsResponse = response.json()['choices'][0]['message']["content"]
            
            wordsAnswers = wordsResponse.split("</think>")[1]

            wordsAnswers = wordsAnswers.replace("\n","")
            
            self.addMessage(wordsAnswers, "assistant")

            filePath = self.generateAudio(wordsAnswers)
            
            playsound(os.path.abspath(filePath))

controller = Conversation()
controller.main()