import speech_recognition as sr

r = sr.Recognizer()

def get_microphone_output():
    '''Runs a speech recognition library and returns a string of user's phrase after an user stops talking
    '''
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print "Which city's weather information do you want to get?"
        audio = r.listen(source)


    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Google doesn't understand audio"
    except sr.RequestError as e:
        return e

if __name__ == '__main__':
    print get_microphone_output()
