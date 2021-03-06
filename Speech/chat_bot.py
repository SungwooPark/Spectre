from chatterbot import ChatBot
import speech_rec
import subprocess

class ChatBotInterface:
    def __init__(self):

        self.chatbot = ChatBot(
            'Aaron Hoover',
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
        )

        self.chatbot.train("chatterbot.corpus.english")

    def say_output(self,s):
        '''
        Say an argument string using bash say command
        '''
        commands = ['say', s]
        process = subprocess.Popen(commands) 
        output, error = process.communicate()

    def chatbot_response(self,s):
        '''
        Return a response of a chatbot
        '''
        return str(self.chatbot.get_response(s))

if __name__ ==  '__main__':
    cb = ChatBotInterface()
    print cb.chatbot_response('hi, how are you doing')
    #print 'Spectre: Hi, My name is Spectre'
    #say_output('Hi, my name is Spectre')
    #prompt = speech_rec.get_microphone_output()
    #print 'You: ', prompt
    #say_output(str(chatbot.get_response(prompt)))
