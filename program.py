import talk 

reedSeekURL = 'http://127.0.0.1:1234'
controller = talk.TalkManager(reedSeekURL = reedSeekURL, languageSelectedId = 0)
controller.run()