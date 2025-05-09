import speech_recognition as sr
from datetime import date
from time import sleep
from playsound import playsound
import os
import pathlib
import json
import requests
import asyncio
import io
from aiogtts import aiogTTS
from pydub import AudioSegment
from pydub.playback import play
import keyboard
from gtts import gTTS

class TalkManager:
    languages = ["en-US","es-ES","pt-BR"]
    
    def __init__(self, reedSeekURL="http://127.0.0.1:1234", languageSelectedId = 0):
        self.LanguageSelected = self.languages[languageSelectedId]
        self.ReedSeekURL = reedSeekURL

        self.messages = []

        with open("data\\"+self.LanguageSelected+"\\messages.json", 'r', encoding='utf8') as messageHistoryFile:
            self.messages = json.load(messageHistoryFile)

    def addMessage(self, message, role):
        newMessage = {"role": role, "content": message}
        self.messages.append(newMessage)
        
        #with open("data\\"+self.LanguageSelected+"\\messages.json", 'w', encoding='utf8') as messageHistoryFile:
        #    messageHistoryFile.write(json.dumps(self.messages, indent=2))
        
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
    
    async def generateAudioAsync(self, textAudio):
        fileName = self.generateNameRandom()+".mp3"
        filePath = os.path.dirname(os.path.abspath(__file__))+"\\audios\\"+fileName

        #fileGenerator = gTTS(text=textAudio, lang = self.LanguageSelected, slow=False)
        #fileGenerator.save(filePath)
        
        aiogtts = aiogTTS()
        
        #await aiogtts.save(textAudio, filePath, lang=self.LanguageSelected)
        #playsound(filePath)
        
        ioData = io.BytesIO()
        await aiogtts.write_to_fp(text=textAudio, fp=ioData, slow=True, lang=self.LanguageSelected)
        song = AudioSegment.from_file(ioData, format="mp3")
        play(song)

    def generateAudio(self, textAudio):
        fileName = self.generateNameRandom()+".mp3"
        filePath = os.path.dirname(os.path.abspath(__file__))+"\\audios\\"+fileName

        tts = gTTS(textAudio, lang = self.LanguageSelected)
        tts.save(filePath)
        playsound(filePath)

    def run(self):
        self.clear()
        print(self.messages[0])

        reco = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            reco.adjust_for_ambient_noise(source) 

        print("Starting...")

        while True:
            loop = asyncio.get_event_loop()
            
            words = ""
            dontSendMessage = False
          
            try:
                with mic as source:                        
                    reco.adjust_for_ambient_noise(source)
                    #print("Listening....")
                    audio = reco.listen(source, timeout = 5, phrase_time_limit = 7)

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
                
                loop.run_until_complete(self.generateAudio("Goodbye"))
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
            
            self.generateAudio(wordsAnswers)
            #loop.run_until_complete(self.generateAudioAsync(wordsAnswers))#,True))
            
            
