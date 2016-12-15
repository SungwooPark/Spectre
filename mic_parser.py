"""
This module is a microphone parser that captures speech input from an user, recognizes it using Google Cloud Speech API, and 
puts an appropriate action into a queue that is used to communicate with GUI
"""
from __future__ import division

import contextlib
import functools
import re
import signal
import sys

from google.cloud import credentials
from google.cloud.grpc.speech.v1beta1 import cloud_speech_pb2 as cloud_speech
from google.rpc import code_pb2
from grpc.beta import implementations
from grpc.framework.interfaces.face import face
import pyaudio
from six.moves import queue

from threading import Thread
from Queue import Queue
from chat_bot import ChatBotInterface

import time

class mic_input_parser(Thread):
    """
    Threaded script that parses a microphone input recognized using Google Cloud Speech API
    Records and communicates the microphone input using a queue
    """
    def __init__(self, speech_queue, newsSources):
        """
        Initializes microphone parser and all necessary components.
        
        :param speech_queue: A queue data structure used to relay the user commands to main GUI module
        :param newsSource: specifies news outlet to use for GUI news widget
        """        

        Thread.__init__(self)
        self.speechQueue = speech_queue
        self.newsSources = newsSources #dictionary[name] = id
        self.chatbot = ChatBotInterface()
        self.daemon = True #speechListener quits when fullWindow quits
        self.start()

        # Audio recording parameters
        self.RATE = 44100
        self.CHUNK = int(self.RATE / 10)  # 100ms

        # The Speech API has a streaming limit of 60 seconds of audio*, so keep the
        # connection alive for that long, plus some more to give the API time to figure
        # out the transcription.
        # * https://g.co/cloud/speech/limits#content
        self.DEADLINE_SECS = 60 * 10 + 5
        self.SPEECH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'


    def make_channel(self, host, port):
        """Creates an SSL channel with auth credentials from the environment."""
        # In order to make an https call, use an ssl channel with defaults
        ssl_channel = implementations.ssl_channel_credentials(None, None, None)

        # Grab application default credentials from the environment
        creds = credentials.get_credentials().create_scoped([self.SPEECH_SCOPE])
        # Add a plugin to inject the creds into the header
        auth_header = (
            'Authorization',
            'Bearer ' + creds.get_access_token().access_token)
        auth_plugin = implementations.metadata_call_credentials(
            lambda _, cb: cb([auth_header], None),
            name='google_creds')

        # compose the two together for both ssl and google auth
        composite_channel = implementations.composite_channel_credentials(
            ssl_channel, auth_plugin)

        return implementations.secure_channel(host, port, composite_channel)


    def _audio_data_generator(self,buff):
        """A generator that yields all available data in the given buffer.

        Args:
            buff - a Queue object, where each element is a chunk of data.
        Yields:
            A chunk of data that is the aggregate of all chunks of data in `buff`.
            The function will block until at least one data chunk is available.
        """
        stop = False
        while not stop:
            # Use a blocking get() to ensure there's at least one chunk of data.
            data = [buff.get()]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    data.append(buff.get(block=False))
                except queue.Empty:
                    break

            # `None` in the buffer signals that the audio stream is closed. Yield
            # the final bit of the buffer and exit the loop.
            if None in data:
                stop = True
                data.remove(None)

            yield b''.join(data)


    def _fill_buffer(self,buff, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        buff.put(in_data)
        return None, pyaudio.paContinue


    # [START audio_stream]
    @contextlib.contextmanager
    def record_audio(self,rate, chunk):
        """Opens a recording stream in a context manager."""
        # Create a thread-safe buffer of audio data
        buff = queue.Queue()

        audio_interface = pyaudio.PyAudio()
        audio_stream = audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=rate,
            input=True, frames_per_buffer=chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't overflow
            # while the calling thread makes network requests, etc.
            stream_callback=functools.partial(self._fill_buffer, buff),
        )

        yield self._audio_data_generator(buff)

        audio_stream.stop_stream()
        audio_stream.close()
        # Signal the _audio_data_generator to finish
        buff.put(None)
        audio_interface.terminate()
    # [END audio_stream]


    def request_stream(self,data_stream, rate, interim_results=True):
        """Yields `StreamingRecognizeRequest`s constructed from a recording audio
        stream.

        Args:
            data_stream: A generator that yields raw audio data to send.
            rate: The sampling rate in hertz.
            interim_results: Whether to return intermediate results, before the
                transcription is finalized.
        """
        # The initial request must contain metadata about the stream, so the
        # server knows how to interpret it.
        recognition_config = cloud_speech.RecognitionConfig(
            # There are a bunch of config options you can specify. See
            # https://goo.gl/KPZn97 for the full list.
            encoding='LINEAR16',  # raw 16-bit signed LE samples
            sample_rate=rate,  # the rate in hertz
            # See http://g.co/cloud/speech/docs/languages
            # for a list of supported languages.
            language_code='en-US',  # a BCP-47 language tag
            speech_context = cloud_speech.SpeechContext(
                phrases = ['Spectre', 'Hey Spectre', 'open','close', 'widget','weather','mirror','newsbox','hide','trip','add','news','timezone','change']
            )
        )
        streaming_config = cloud_speech.StreamingRecognitionConfig(
            interim_results=interim_results,
            config=recognition_config,
        )

        yield cloud_speech.StreamingRecognizeRequest(
            streaming_config=streaming_config)

        for data in data_stream:
            # Subsequent requests can all just have the content
            yield cloud_speech.StreamingRecognizeRequest(audio_content=data)


    def listen_print_loop(self,recognize_stream):
        """Iterates through server responses and prints them.

        The recognize_stream passed is a generator that will block until a response
        is provided by the server. When the transcription response comes, print it.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0

        counter = 0

        timeout = time.time() + 30
        for resp in recognize_stream:
            print('recognize_stream: ')
            print(recognize_stream)
            if resp.error.code != code_pb2.OK:
                raise RuntimeError('Server error: ' + resp.error.message)

            if not resp.results:
                print('if not resp.result part...' + str(counter))
                counter += 1
                continue

            # Display the top transcription
            result = resp.results[0]
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            if not result.is_final:
                # If the previous result was longer than this one, we need to print
                # some extra spaces to overwrite the previous result
                overwrite_chars = ' ' * max(0, num_chars_printed - len(transcript))
                print('intermediate printing step...' + str(counter))
                counter += 1

                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)
            else:
                print('final command step...' + str(counter))
                counter += 1
                print(transcript)

                #Put response into queue for use in Spectre Gui
                #print(transcript.encode('utf-8'))
                command = transcript.encode('utf-8')

                print(command)
                #ASK CHATBOT QUESTION
                if "question" in command.lower():
                    self.chatbot.say_output("How can I help you?")
                    question = get_microphone_output(self.speech_rec)
                    print(question)
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
                        print(city_name)
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
                        to_split_command = from_split_command[1].split(" to ") #split 2nd of 2
                        if "by" in command:
                            by_split_command = to_split_command[1].split(" by ")
                            origin_address = to_split_command[len(to_split_command)-2] #item 0
                            final_address = by_split_command[len(by_split_command)-2]#item 0
                            travel_mode = by_split_command[len(by_split_command)-1]#item 1
                        else:
                            origin_address = to_split_command[len(to_split_command)-2] #item 0
                            final_address = to_split_command[len(to_split_command)-1]#item 1
                            travel_mode = 'driving'
                        print(origin_address)
                        print(final_address)
                        self.speechQueue.put(("trip", [origin_address, final_address, travel_mode]))
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
                elif "close" in command:
                    self.speechQueue.put(("direction","closed"))

                if time.time() > timeout:
                    print('timeout break')
                    break

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break

                num_chars_printed = 0
        print('finished for loop')

    def run(self):
        """
        Run speech recognition script
        """
        with cloud_speech.beta_create_Speech_stub(
                self.make_channel('speech.googleapis.com', 443)) as service:
            # For streaming audio from the microphone, there are three threads.
            # First, a thread that collects audio data as it comes in
            with self.record_audio(self.RATE, self.CHUNK) as buffered_audio_data:
                # Second, a thread that sends requests with that data
                requests = self.request_stream(buffered_audio_data, self.RATE)
                # Third, a thread that listens for transcription responses
                recognize_stream = service.StreamingRecognize(
                    requests, self.DEADLINE_SECS)

                # Exit things cleanly on interrupt
                #signal.signal(signal.SIGINT, lambda *_: recognize_stream.cancel())

                # Now, put the transcription responses to use.
                try:
                    while True:
                        self.listen_print_loop(recognize_stream)
                        print('done???')
                    recognize_stream.cancel()
                except face.CancellationError:
                    # This happens because of the interrupt handler
                    pass
