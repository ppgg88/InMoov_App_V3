import pyaudio
import wave
import struct
import speech_recognition as sr
from chatgpt import *
import pyttsx3
import numpy as np
import time
from trig import Triger
from index_ia import DeepNeuralNetwork
from robot import Robot
#######################################################################################
# initialisation de l'IA local

import json
import string
import random 
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer 
import tensorflow as tf
from keras import Sequential 
from keras.layers import Dense, Dropout
#from data_chat import data

chatgpt_key = "sk-LfoyHJItaF665HkwNTbdT3BlbkFJgFLQjSApl0joYOURHdeE"
try :
    temp = np.load("var/voice_data.npy", allow_pickle=True)
    chatgpt_use = temp[2]
    training = temp[3]
except:
    chatgpt_use = True
    training = False

# initialisation de la librairie de synthèse vocale
engine = pyttsx3.init('sapi5')
engine.say("Démarrage de Hugo en cours")


# initialisation de lemmatizer pour obtenir la racine des mots
lemmatizer = WordNetLemmatizer()

nltk.download("punkt")
nltk.download("wordnet")

#initialisation des data pour l'IA local
da = open("var/data.json", "r", encoding="utf8")
data = json.load(da)
da.close()

da = open("var/equivalent.json", "r", encoding="utf8")
equ = json.load(da)
da.close()
"""
engine.say("Démarrage de ChatGPT")
engine.runAndWait()
engine.stop()

api = Chatbot(chatgpt_key)
resp = api.ask("Hugo est un robot français développé par la communauté InMoov sur internet et les réseau sociaux et construit entièrement en impression 3D par Paul Giroux. pour l'instant il à encore du mal à bouger. il sais répondre à presque toute les question mais fais toujours des réponse très courte et concise. il ne depasse jamais les 20 mots. répond maintenant comme si tu étais Hugo.")
engine.say("ChatGPT est prêt")
engine.runAndWait()
engine.stop()
"""
trig_engine : Triger
def set_trigger_engine(triger_engine):
    global trig_engine
    trig_engine = triger_engine
    
robot : Robot
def set_robot(Robot):
    global robot
    robot = Robot

def get_voices():    
    global engine
    voices = engine.getProperty('voices')
    voix = []
    for voice in voices:
        voix.append([voice.id, voice.name])
    return voix

def clean_text(text:str):
    text = " "+text.lower()+" "
    for i in equ['list'] :
        for j in i['equivalent']:
            text = text.replace(j, i['name'])
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def bag_of_words(text, vocab): 
    tokens = clean_text(text)
    bow = [0] * len(vocab)
    for w in tokens: 
        for idx, word in enumerate(vocab):
            if word == w: 
                bow[idx] = 1
    return np.array(bow)

def pred_class(text, vocab, labels): 
    bow = bag_of_words(text, vocab)
    print("bow : " + str(bow))
    result = model.predict(np.array([bow]))[0]
    probabilities = tf.nn.softmax(result)
    print("proba : " + str(float(max(probabilities))))
    
    if(max(probabilities) < 0.022):
        return []

    thresh = 0.2
    y_pred = [[idx, res] for idx, res in enumerate(result) if res > thresh]
    y_pred.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in y_pred:
        return_list.append(labels[r[0]])
    return return_list

def get_response(intents_list):
    tag = intents_list[0]
    for i in data["intents"]: 
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break
    return result

def ia_local(lemmatizer, data):
    engine.say("Entrainement de l'IA en cours")
    engine.runAndWait()
    engine.stop()
    # création des listes
    words = []
    classes = []
    doc_X = []
    doc_y = []
    # parcourir avec une boucle For toutes les intentions
    # tokéniser chaque pattern et ajouter les tokens à la liste words, les patterns et
    # le tag associé à l'intention sont ajoutés aux listes correspondantes
    for i in range(len(data["intents"])):
        for j in range(len(data["intents"][i]["patterns"])):
            text = data["intents"][i]["patterns"][j]
            text = " "+text.lower()+" "
            for t in range(len(equ['list'])) :
                for k in range(len(equ['list'][t]['equivalent'])):
                    text = text.replace(equ['list'][t]['equivalent'][k], equ['list'][t]['name'])
            data["intents"][i]["patterns"][j] = text
            print(data["intents"][i]["patterns"][j])
    for intent in data['intents']:
        try:
            for pattern in intent["patterns"]:
                tokens = nltk.word_tokenize(pattern)
                words.extend(tokens)
                doc_X.append(pattern)
                doc_y.append(intent["tag"])
        except:
            print(intent)
            break
        
        # ajouter le tag aux classes s'il n'est pas déjà là 
        if intent["tag"] not in classes:
            classes.append(intent["tag"])
    # lemmatiser tous les mots du vocabulaire et les convertir en minuscule
    # si les mots n'apparaissent pas dans la ponctuation
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in string.punctuation]
    # trier le vocabulaire et les classes par ordre alphabétique et prendre le
    # set pour s'assurer qu'il n'y a pas de doublons
    words = sorted(set(words))
    classes = sorted(set(classes))

    print(words)

    # liste pour les données d'entraînement
    training = []
    out_empty = [0] * len(classes)
    # création du modèle d'ensemble de mots
    for idx, doc in enumerate(doc_X):
        bow = []
        text = lemmatizer.lemmatize(doc.lower())
        for word in words:
            bow.append(1) if word in text else bow.append(0)
        #print("bow train : " + str(bow))
        # marque l'index de la classe à laquelle le pattern atguel est associé à
        output_row = list(out_empty)
        output_row[classes.index(doc_y[idx])] = 1
        # ajoute le one hot encoded BoW et les classes associées à la liste training
        training.append([bow, output_row])
    # mélanger les données et les convertir en array
    random.shuffle(training)
    training = np.array(training, dtype=object)
    # séparer les features et les labels target
    train_X = np.array(list(training[:, 0]))
    train_y = np.array(list(training[:, 1]))

    # définition de quelques paramètres
    input_shape = (len(train_X[0]),)
    output_shape = len(train_y[0])
    epochs = 200

    # modèle Deep Learning
    model = Sequential()
    model.add(Dense(254 , input_shape=input_shape, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.1))
    model.add(Dense(output_shape, activation = "softmax"))
    adam = tf.keras.optimizers.legacy.Adam(learning_rate=0.0005, decay=1e-6)
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=["accuracy"])

    print(model.summary())
    # entraînement du modèle
    model.fit(x=train_X, y=train_y, epochs=200, verbose=1)
    
    engine.say("Entrainement de l'IA terminer")
    engine.runAndWait()
    engine.stop()
    
    return model, words, classes

def get_max_level(data_s):
    # Décompactez les données audio en entiers signés de 16 bits
    values = struct.unpack("<{}h".format(len(data_s) // 2), data_s)
    # Renvoyez le maximum des valeurs
    return max(values)

def chat():
    global model, data, words, classes, training, chatgpt_key, engine, chatgpt_use, micro_on, trig_engine
    
    micro_on = False
    try: 
        micro_on = np.load('var/mute.npy', allow_pickle=True)
    except:
        pass
        
    if micro_on :
        # Créez un objet PyAudio et un objet Recognizer
        p = pyaudio.PyAudio()
        r = sr.Recognizer()

        """
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"{info['name']} (index {i})")"""

        #on attend que le niveau sonore soit superieur à un seuil de silence, en attendant on verifie que l'utilisateur n'ai pas demander une phase d'entrainement de l'ia
        text = trig_engine.main()
        
        ############################### IA Local
        intents = pred_class(text.lower(), words, classes)
        if len(intents) == 0:
            print("Je ne comprends pas")
            result = "un instant s'il vous plait, je fais une recherche"
            found = True
        else :
            print(intents)
            result = get_response(intents)
            found = False
        
        ############################### VOIX
        setings = np.load("var/voice_data.npy", allow_pickle=True)
        for i in setings[0]:
            if i[2] == "selected":
                engine.setProperty('voice', i[0])
        engine.setProperty('rate', int(setings[1]))
        print("speed : " + str(engine.getProperty('rate')))
        training = setings[3]
        print("training : " + str(training))
        temp = False
        engine.say(result)
        while temp == False :
            try :
                np.save("var/onspeek.npy", True)
                temp = True
            except :
                pass
        engine.runAndWait()
        engine.stop()
        temp = False
        while temp == False :
            try :
                np.save("var/onspeek.npy", False)
                temp = True
            except :
                pass
        ############################### Demarage de CHATGPT
        if(chatgpt_use != setings[2]) and setings[2] == True:
            if chatgpt_key != "" and chatgpt_use:
                print("Demarage de tChatte GPT...")
                api = Chatbot(chatgpt_key)
                chatgpt_use = setings[2]
                            
        ############################### RECHERCHE SUR CHATGPT
        if chatgpt_key != "" and chatgpt_use:
            if (len(intents)> 0 and intents[0] == "recherche") or found:
                resp : str
                #resp = api.ask("Hugo en 20 mots maximum : " + text)['choices'][0]['text']
                print(resp)
                resp.replace("En tant que Hugo, un robot français développé par la communauté InMoov et construit entièrement en impression 3D,", "", 1)
                engine.say(resp)
                engine.runAndWait()
                engine.stop()
                gptdata = json.load(open("var/gptdata.json", "r", encoding="utf-8"))
                list_tag = []
                for i in gptdata['intents']:
                    list_tag.append(int(i['tag']))
                maxi = max(list_tag)
                gptdata['intents'].append({
                    "tag": str(maxi + 1),
                    "patterns": [text],
                    "responses": [resp]
                })
                json.dump(gptdata, open("var/gptdata.json", "w", encoding="utf-8"), ensure_ascii=False)
                                    
        if training :
            np.save("var/training.npy", True)
            np.save("var/reponsse.npy", result)
            np.save("var/question.npy", text.lower())
            if(len(intents) > 0):
                np.save("var/tag.npy", intents[0])
            else :
                np.save("var/tag.npy", "___")
            #on attend que l'utilisateur ai fais un choix pour l'entrainement
            while np.load("var/training.npy") :
                time.sleep(1)
                try : # on regarde si il y a un entrainement demander par l'utilisateur
                    if np.load('var/trIA.npy', allow_pickle=True) == True:
                        da = open("var/data.json", "r", encoding="utf8")
                        data = json.load(da)
                        da.close()
                        model, words, classes = ia_local(lemmatizer, data)
                        np.save('var/trIA.npy', False)
                except :
                    pass
            data = json.load(open("var/data.json", "r", encoding='utf8'))
            #model, words, classes = ia_local(lemmatizer, data)

def loop_chat() :
    while True :
        chat()

model, words, classes = ia_local(lemmatizer, data)


if __name__ == '__main__':
    set_trigger_engine(Triger())
    while True :
        chat()