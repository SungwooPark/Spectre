import speech_recognition as sr

# r = sr.Recognizer()

def get_microphone_output(r):
	'''Runs a speech recognition library and returns a string of user's phrase after an user stops talking
	'''
	with sr.Microphone() as source:
		r.adjust_for_ambient_noise(source)
		print "How can I help you?"
		audio = r.listen(source)


	try:
		return r.recognize_google(audio)
	except sr.UnknownValueError:
		return "Nothing"
	except sr.RequestError as e:
		return e
