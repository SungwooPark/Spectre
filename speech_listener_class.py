from rec_commands import get_microphone_output #speech rec program
import speech_recognition as sr
from threading import Thread
from Queue import Queue
from chat_bot import ChatBotInterface

class speechListener(Thread): #constantly checking on its own, outside of main thread
	def __init__(self, queue, newsSources):
		Thread.__init__(self)
		self.speech_rec = sr.Recognizer() #initialize speech recognition object
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
			if "question" in command:
				self.chatbot.say_output("How can I help you?")
				question = get_microphone_output(self.speech_rec)
				print question
				if "mind" in question: #I mean "never mind"
					pass
				else:
					self.chatbot.say_output(self.chatbot.chatbot_response(question))
			#CHANGE WEATHER LOCATION
			elif "weather" in command: #ie "get weather for Boston"
				split_command = command.split(" ")
				city_name = split_command[len(split_command)-1] #assumes city name is last word
				self.speechQueue.put(("weather", city_name)) #assumes city is one word
			#CHANGE NEWS SOURCE
			elif "news" in command: #ie "get news from BBC"
				for source in self.newsSources:
					if source in command:
						self.speechQueue.put(("news", self.newsSources[source]))
			#CHANGE TIMEZONE				
			elif "zone" in command: #ie "change timezone to Madrid, Spain"
				split_command = command.split(" ")
				city_name = split_command[len(split_command)-2]
				country_name = split_command[len(split_command)-1]
				self.speechQueue.put(("timezone", ((city_name, country_name))))
			#GET TRIP INFORMATION				
			elif "trip" in command: #ie "length of trip from A to B"
				from_split_command = command.split("from ")
				to_split_command = from_split_command[1].split(" to ")
				origin_address = to_split_command[len(to_split_command)-2] #item 0
				final_address = to_split_command[len(to_split_command)-1]#item 1
				print origin_address
				print final_address
				self.speechQueue.put(("trip", ((origin_address, final_address))))
			#OPEN/CLOSE MIRROR
			elif "open" in command:
				self.speechQueue.put(("direction","open"))
			elif "shut" in command:
				self.speechQueue.put(("direction","closed"))