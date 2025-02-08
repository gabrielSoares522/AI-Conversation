import speech_recognition as sr
from datetime import date
from time import sleep
from playsound import playsound
import os
import pathlib
import json
import requests
import asyncio
from io import BytesIO
from aiogtts import aiogTTS

class TalkManager:
    languages = ["en-US","es-ES","pt-BR"]
    
    def __init__(self, reedSeekURL="http://127.0.0.1:1234", languageSelectedId = 0):
        self.LanguageSelected = self.languages[languageSelectedId]
        self.ReedSeekURL = reedSeekURL

        if self.LanguageSelected == 'en-US':
            self.messages = [{"role": "user", "content": "You are an assistant named Sarah and you must respond when spoken to."},
        {"role": "assistant", "content": "Thank you! I'm here to help with any questions or needs you may have. What do you want me to do for you?"}]
        elif self.LanguageSelected == 'es-ES':
            self.messages = [{"role": "system", "content": "Eres una asistente útil llamada Sara."}]
        elif self.LanguageSelected == 'pt-BR':
            self.messages = [{"role": "system", "content": "Eu sou um assistente prestativa chamada Sarah."}]
    
    def addMessage(self, message, role):
        self.messages.append({"role": role, "content": message})
        print(role+": "+message)

    def getAnswer(self):
        url = self.ReedSeekURL+'/v1/chat/completions'
        body = {
            "model": "deepseek-chat",
            "messages": self.messages,
            "stream": False
        }

        try:
            x = requests.post(url, json = body)
        except Exception as e:
            raise(e)
        
        return x

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def generateNameRandom(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def setLanguage(self, languageIndex):
        self.LanguageSelected = self.languages[languageIndex]
        print("Language changed to "+self.LanguageSelected)
    
    async def generateAudio(self, text, autoPlay=False):
        fileName = self.generateNameRandom()+".mp3"
        filePath = os.path.dirname(os.path.abspath(__file__))+"\\audios\\"+fileName

        #fileGenerator = gTTS(text=text, lang = self.LanguageSelected.split("-")[0], slow=False)
        #fileGenerator.save(filePath)
        
        aiogtts = aiogTTS()
        #io = BytesIO()
        await aiogtts.save(text, filePath, lang=self.LanguageSelected.split("-")[0])
        #await aiogtts.write_to_fp(text, io, slow=True, lang=self.LanguageSelected.split("-")[0])
        if autoPlay:
            playsound(filePath)

    def run(self):
        self.clear()

        reco = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            reco.adjust_for_ambient_noise(source) 

        print("Starting...")

        while True:
            words = ""
            dontSendMessage = False

            with mic as source:
                print("listening...")
                audio = reco.listen(source)
            
            try:
                words = reco.recognize_google(audio, language=self.LanguageSelected)
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
            
            try:
                response = self.getAnswer()
            except Exception as e:
                print("Error: Faile to connect to AI model server!")
                continue

            wordsResponse = response.json()['choices'][0]['message']["content"]
            
            wordsAnswers = wordsResponse.split("</think>")[1]

            wordsAnswers = wordsAnswers.replace("\n","")
            
            self.addMessage(wordsAnswers, "assistant")
            
            loop = asyncio.get_event_loop()

            loop.run_until_complete(self.generateAudio(wordsAnswers,True))
            
            
