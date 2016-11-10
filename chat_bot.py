from chatterbot import ChatBot
import speech_rec
import subprocess

def say_output(s):
    '''
    Say an argument string using bash say command
    '''
    commands = ['say', s]
    process = subprocess.Popen(commands) 
    output, error = process.communicate()    

chatbot = ChatBot(
    'Aaron Hoover',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)

chatbot.train("chatterbot.corpus.english")

if __name__ ==  '__main__':
    print 'Spectre: Hi, My name is Spectre.'
    say_output('Hi, my name is Aaron')
    prompt = speech_rec.get_microphone_output()
    print 'You: ', prompt
    say_output(str(chatbot.get_response(prompt)))