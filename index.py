import gui # Path: gui.py
import threading
import voice # Path: voice.py
from robot import Robot # Path: robot/__init__.py
from index_ia import DeepNeuralNetwork # Path: index_ia.py
from trig import Triger
import numpy as np
allstop = False

InMoov = Robot()

def thread_gui():
    global allstop, InMoov
    gui.setup(voice.get_voices(), InMoov)
    gui.setup([['', ''], ['', ''], ['', '']], InMoov)
    gui.app.run()


if __name__ == '__main__':
    print("Starting threads...")
    voice.set_trigger_engine(Triger())
    voice.set_robot(InMoov)
    np.save('var/onspeek.npy', False)
    voice_thread = threading.Thread(target=InMoov.head.speek)
    voice_thread.start()
    gui_thread = threading.Thread(target=thread_gui)
    gui_thread.start()
    InMoov.head.home()
    InMoov.right_arm.home()
    voice.loop_chat()
    
