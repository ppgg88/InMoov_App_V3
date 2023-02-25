from index_ia import DeepNeuralNetwork
import pyaudio
import wave
import struct
import speech_recognition as sr
import time
import json
from nltk.stem import WordNetLemmatizer 
import nltk
import json
import random
import numpy as np
import string
import pickle


class Triger:
    def __init__(self, trig_path = "chatbot/utile/triger.hgo", discuss_path = "chatbot/utile/discuss.hgo"):
        '''Initiate the chatbot with the models paths (default: triger.h5 and discuss.h5)'''
        
        self.dnn_trigeur : DeepNeuralNetwork
        
        with open(trig_path, 'rb') as f:
            self.dnn_trigeur = pickle.load(f)

        self.environment_sond_level = 0
        
        self.__p = pyaudio.PyAudio()
        # Paramètres du flux audio
        self.__FRAMES_PER_BUFFER = 1024
        self.__FORMAT = pyaudio.paInt16
        self.__CHANNELS = 1
        self.__RATE = 48000
        self.__stream = self.__p.open(
            format=self.__FORMAT,
            channels=self.__CHANNELS,
            rate=self.__RATE,
            input=True,
            frames_per_buffer=self.__FRAMES_PER_BUFFER
        )
        
    
    def __get_max_level_sound(self, data_s):
        # Décompactez les données audio en entiers signés de 16 bits
        values = struct.unpack("<{}h".format(len(data_s) // 2), data_s)
        # Renvoyez le maximum des valeurs
        return max(values)
    
    def __get_ambiance_level(self, time = 5):
        "Get the ambiance level in the room for the next time seconds (default: 5 seconds)"
        level = []
        for i in range(0, int(self.__RATE / self.__FRAMES_PER_BUFFER * time)):
            data_s = self.__stream.read(self.__FRAMES_PER_BUFFER)
            level.append(self.__get_max_level_sound(data_s))
        return (sum(level)/len(level))
    
    def set_environment_level(self, time = 5, add = 700):
        "Set the ambiance level in the room mesured during time seconds (default: 5 seconds) and add 700 to it"
        self.environment_sond_level = self.__get_ambiance_level(time)+add
    
    def save_wav(self, filename : str, frame: list):
        with wave.open(str(filename)+'.wav', 'wb') as wav_file:
            # Définissez les paramètres du fichier wave
            wav_file.setnchannels(self.__CHANNELS)
            wav_file.setsampwidth(self.__p.get_sample_size(self.__FORMAT))
            wav_file.setframerate(self.__RATE)
            # Écrivez les données audio dans le fichier wave
            wav_file.writeframes(b''.join(frame))

    def listen(self, time = 0.5, first_frame = None):
        "Listen during time seconds (default: 1 seconds)"
        if first_frame != None:
            frames = [first_frame]
        else:
            frames = []
        for i in range(0, int(self.__RATE / self.__FRAMES_PER_BUFFER * time)):
            data = self.__stream.read(self.__FRAMES_PER_BUFFER)
            frames.append(data)
        return frames
    
    def sound_start(self):
        "Listen until the sound is activated and return the first frame"
        frame = self.__stream.read(self.__FRAMES_PER_BUFFER)
        max_level = self.__get_max_level_sound(frame)
        while max_level < self.environment_sond_level:
            frame = self.__stream.read(self.__FRAMES_PER_BUFFER)
            max_level = self.__get_max_level_sound(frame)
        return frame
    
    def listen_triger(self, time = 0.5):
        "Listen during time seconds (default: 1 seconds) and return True if the triger is activated"
        frames = self.listen(time, self.sound_start())
        self.save_wav("trig", frames)
        data = DeepNeuralNetwork.normalize_wav("trig.wav")
        return (self.dnn_trigeur.predict(data)[0], frames)
    
    def listen_spoken(self, stop_time = 1):
        "Listen until the sound is under the ambiance noises and return the frames"
        curent_time = time.time()
        data = self.__stream.read(self.__FRAMES_PER_BUFFER)
        frames = [data]
        level = self.__get_max_level_sound(data)
        while time.time() - curent_time < stop_time or level > self.environment_sond_level:
            data = self.__stream.read(self.__FRAMES_PER_BUFFER)
            frames.append(data)
            level = self.__get_max_level_sound(data)
            if level > self.environment_sond_level:
                curent_time = time.time()
        return frames
    
    def main(self):
        "Main loop of the chatbot"
        self.set_environment_level()
        print("ambiance level : ", self.environment_sond_level)
        while True:
            triger, frames = self.listen_triger()
            triger = True
            if triger:
                print("triger")
                frames+=self.listen_spoken()
                self.save_wav("spoken", frames)
                r = sr.Recognizer()
                audio_wav = sr.AudioFile('spoken.wav')
                say = ""
                with audio_wav as source:
                    audio = r.listen(source)
                try:
                    say = r.recognize_google(audio, language='fr-FR')
                    return(say)
                except:
                    print("I did not understand")
            else:
                print("no triger")

if __name__ == "__main__":
    chatbot = Triger()
    chatbot.main()
    
    