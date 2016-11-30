from rec_commands import get_microphone_output #speech rec program
import speech_recognition as sr
from threading import Thread
from Queue import Queue
from chat_bot import ChatBotInterface
import transcribe_streaming

class speechListener(Thread): #constantly checking on its own, outside of main thread
    #Google cloud speech api related methods
	def __init__(self, queue, newsSources):
		Thread.__init__(self)
		#self.speech_rec = sr.Recognizer() #initialize speech recognition object  
    
		self.speechQueue = queue
		self.newsSources = newsSources #dictionary[name] = id
		self.chatbot = ChatBotInterface()
		self.daemon = True #speechListener quits when fullWindow quits
		self.start()
	def run(self): #threading automatically calls the run method
		count = 0
		while True:
			print count
			count += 1
			command = get_microphone_output(self.speech_rec)
			print command
			#ASK CHATBOT QUESTION
			if "question" in command.lower():
				self.chatbot.say_output("How can I help you?")
				question = get_microphone_output(self.speech_rec)
				print question
				if "mind" in question: #I mean "never mind"
					pass
				else:
					self.chatbot.say_output(self.chatbot.chatbot_response(question))
			#SHOW/PIN A WIDGET
			elif "show" in command.lower() or "hyde" in command.lower() or "hide" in command.lower() or "add" in command.lower() or "odd" in command.lower() or "remove" in command.lower():
				command = command.lower()
				do = "show"
				if "hyde" in command or "hide" in command: #for some reason, the format
					do = "hide" #"if "Hyde" or "hide" in command:"" breaks it :(
				elif "add" in command or "odd" in command:
					do = "add"
				elif "remove" in command:
					do = "remove"
				if "weather" in command:
					self.speechQueue.put((do, "weather"))
				elif "news" in command:
					self.speechQueue.put((do, "news"))
				elif "trip" in command:
					self.speechQueue.put((do, "trip"))
				elif "direction" in command:
					self.speechQueue.put((do, "direction"))
				elif "box" in command:
					self.speechQueue.put(do, "newsbox")
			#CHANGE WEATHER LOCATION
			elif "weather" in command.lower(): #ie "get weather for Boston"
				if "for " in command:
					split_command = command.split("for ")
					city_name = split_command[len(split_command)-1] #assumes city name is last word
					self.speechQueue.put(("weather", city_name)) #assumes city is one word
					print city_name
			#CHANGE TIMEZONE				
			elif "zone" in command.lower(): #ie "change timezone to Madrid, Spain"
				if "to" in command:
					split_command = command.split("to")
					# city_name = split_command[len(split_command)-2]
					address = split_command[len(split_command)-1]
					self.speechQueue.put(("timezone", address))
			#GET TRIP INFORMATION				
			elif "trip" in command.lower(): #ie "length of trip from A to B"
				if "from" in command and "to" in command:
					from_split_command = command.split("from ")
					to_split_command = from_split_command[1].split(" to ")
					origin_address = to_split_command[len(to_split_command)-2] #item 0
					final_address = to_split_command[len(to_split_command)-1]#item 1
					print origin_address
					print final_address
					self.speechQueue.put(("trip", ((origin_address, final_address))))
			#GET CHORO MAP
			elif "box" in command.lower(): #ie "put bob in NewsBox"
				if "put " in command and " in " in command:
					put_split_command = command.split("put ")
					in_split_command = put_split_command[1].split(" in ")
					search_term = in_split_command[len(in_split_command)-2] #three word list, want middle word
					self.speechQueue.put(("newsbox", search_term))
			#CHANGE NEWS SOURCE
			elif "news" in command.lower(): #ie "get news from BBC"
				for source in self.newsSources:
					if source in command:
						self.speechQueue.put(("news", self.newsSources[source]))
			#OPEN/CLOSE MIRROR
			elif "open" in command:
				self.speechQueue.put(("direction","open"))
			elif "shut" in command:
				self.speechQueue.put(("direction","closed"))
