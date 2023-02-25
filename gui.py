from flask import Flask, request,  render_template
import win32api
import win32gui
import numpy as np
from robot import Robot
import json
import time

InMoov:Robot

def setup(voix, robot : Robot):
    global voices, voice_speed, chat_gpt, micro_on, InMoov, training_
    
    micro_on = True
    training_ = False
    
    voice_speed = 150
    chat_gpt = False
    
    voices = voix
    InMoov = robot
    
    for i in voices:
        i.append('')
    voices[2][2] = 'selected'
    try :
        voices, voice_speed, chat_gpt, training_ = np.load('var/voice_data.npy', allow_pickle=True)
    except :    
        np.save('var/voice_data.npy', np.array([voices, voice_speed, chat_gpt, training_], dtype=object))
    np.save("var/mute.npy", micro_on)
    
    np.save("var/training.npy", False)
    np.save("var/question.npy", "")
    np.save("var/reponse.npy", "")
    np.save("var/tag.npy", "")
    

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', micro_on = micro_on)


@app.route('/head')
def head():
    global InMoov
    pin = [InMoov.head.Rotation.getPin(), InMoov.head.UpDown.getPin(), InMoov.head.Mouth.getPin(), InMoov.head.EyeX.getPin(), InMoov.head.EyeY.getPin()]
    carte = [InMoov.head.Rotation.getCarte(), InMoov.head.UpDown.getCarte(), InMoov.head.Mouth.getCarte(), InMoov.head.EyeX.getCarte(), InMoov.head.EyeY.getCarte()]
    return render_template('head.html',micro_on = micro_on, pin = pin, carte = carte)

@app.route('/right_arm')
def right_arm():
    global InMoov
    pin = [InMoov.right_arm.epaulex.getPin(), InMoov.right_arm.epauley.getPin(), InMoov.right_arm.epaulez.getPin(), InMoov.right_arm.coude.getPin()]
    carte = [InMoov.right_arm.epaulex.getCarte(), InMoov.right_arm.epauley.getCarte(), InMoov.right_arm.epaulez.getCarte(), InMoov.right_arm.coude.getCarte()]
    return render_template('right_arm.html',micro_on = micro_on, pin = pin, carte = carte)

@app.route('/chatbot')
def chatbot():
    if chat_gpt :
        gpt = 'checked'
    else:
        gpt = ''
    question = ''
    reponse = ''
    tag = ''
    print("training = ", training_)
    return render_template('chatbot.html', voices = voices, voice_speed = voice_speed, gpt = gpt, micro_on = micro_on, training = training_, question = question, reponse = reponse, tag = tag)

@app.route('/moteur_settings', methods=['GET'])
def moteur_settings():
    global modifing_motor
    name = request.args.get('name', 0, type=str)
    where = request.args.get('where', 0, type=str)
    
    if name == "tetex":
        modifing_motor = InMoov.head.Rotation
    elif name == "tetey":
        modifing_motor = InMoov.head.UpDown
    elif name == "bouche":
        modifing_motor = InMoov.head.Mouth
    elif name == "yeuxx":
        modifing_motor = InMoov.head.EyeX
    elif name == "yeuxy":
        modifing_motor = InMoov.head.EyeY
    else :
        return ("error go back to <a href='/"+where+"'>"+where+"</a>")
    
    return render_template('moteur_setings.html', name = name, position = modifing_motor.getPosition(), micro_on = micro_on, pin = modifing_motor.getPin(), carte = modifing_motor.getCarte(), limit = modifing_motor.getLimit(), where = where)

@app.route('/head_moov', methods=['GET'])
def get_range():
    global InMoov
    # Récupération des valeurs de début et de fin de l'intervalle
    #ajax request : 'tetex': tetex, 'tetey': tetey, 'bouche': bouche, 'yeuxx': yeuxx, 'yeuxy': yeuxy
    tetex = request.args.get('tetex', 0, type=int)
    tetey = request.args.get('tetey', 0, type=int)
    bouche = request.args.get('bouche', 0, type=int)
    yeuxx = request.args.get('yeuxx', 0, type=int)
    yeuxy = request.args.get('yeuxy', 0, type=int)
    try :
        InMoov.head.Rotation.move(tetex)
        InMoov.head.UpDown.move(tetey)
        InMoov.head.Mouth.move(bouche)
        InMoov.head.EyeX.move(yeuxx)
        InMoov.head.EyeY.move(yeuxy)
    except :
        pass
    # Traitement des données de l'intervalle
    return "ok"

@app.route('/get_head_position')
def get_head_position():
    global InMoov
    return [InMoov.head.Rotation.getPosition(), InMoov.head.UpDown.getPosition(), InMoov.head.Mouth.getPosition(), InMoov.head.EyeX.getPosition(), InMoov.head.EyeY.getPosition()]

@app.route('/get_right_arm_position')
def get_right_arm_position():
    global InMoov
    return [InMoov.right_arm.epaulex.getPosition(), InMoov.right_arm.epauley.getPosition(), InMoov.right_arm.epaulez.getPosition(), InMoov.right_arm.coude.getPosition()]

@app.route('/right_arm_moov', methods=['GET'])
def get_range_ra():
    global InMoov
    # Récupération des valeurs de début et de fin de l'intervalle
    #ajax request : 'tetex': tetex, 'tetey': tetey, 'bouche': bouche, 'yeuxx': yeuxx, 'yeuxy': yeuxy
    epaulex = request.args.get('epaulex', 0, type=int)
    epauley = request.args.get('epauley', 0, type=int)
    epaulez = request.args.get('epaulez', 0, type=int)
    coude = request.args.get('coude', 0, type=int)
    try :
        InMoov.right_arm.epaulex.move(epaulex)
        InMoov.right_arm.epauley.move(epauley)
        InMoov.right_arm.epaulez.move(epaulez)
        InMoov.right_arm.coude.move(coude)
    except :
        pass
    # Traitement des données de l'intervalle
    return "ok"



@app.route('/voice_parameters', methods=['POST'])
def voice_parameters():
    global voice_speed, voices, chat_gpt, training_
    voice_speed = request.form['speed']
    print("speed = ", voice_speed)
    voice = request.form['voice']
    chat_gpt = request.form['gpt']
    if chat_gpt == 'true':
        chat_gpt = True
    else:
        chat_gpt = False
    training_ = False
    training_ = request.form['training']
    if training_ == 'true':
        training_ = True
    else:
        training_ = False
    print("training = ", training_)
    print("chat_gpt = ", chat_gpt)
    for v in voices:
        if v[0] == voice:
            v[2] = 'selected'
            print(v)
        else:
            v[2] = ''
    np.save('var/voice_data.npy', np.array([voices, voice_speed, chat_gpt, training_], dtype=object))
    return "ok"

@app.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@app.route('/mute_microphone')
def mute_microphone():
    global micro_on
    """WM_APPCOMMAND = 0x319
    APPCOMMAND_MICROPHONE_VOLUME_MUTE = 0x180000
    hwnd_active = win32gui.GetForegroundWindow()
    win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)"""
    if micro_on:
        micro_on = False
        np.save("var/mute.npy", micro_on)
        return 'Microphone muted'
    else:
        micro_on = True
        np.save("var/mute.npy", micro_on)
        return 'Microphone unmuted'

@app.route('/pin_update', methods=['GET'])
def pin_update():
    global InMoov
    where = request.args.get('where', 0, type=str)
    if where == 'head':
        tetex = request.args.get('tetex', 0, type=int)
        tetey = request.args.get('tetey', 0, type=int)
        bouche = request.args.get('bouche', 0, type=int)
        yeuxx = request.args.get('yeuxx', 0, type=int)
        yeuxy = request.args.get('yeuxy', 0, type=int)
        
        InMoov.head.Rotation.setPin(tetex)
        InMoov.head.UpDown.setPin(tetey)
        InMoov.head.Mouth.setPin(bouche)
        InMoov.head.EyeX.setPin(yeuxx)
        InMoov.head.EyeY.setPin(yeuxy)
        
        data = json.load(open('config.json'))
        data['head']['rotation']['pin'] = tetex
        data['head']['UpDown']['pin'] = tetey
        data['head']['Mouth']['pin'] = bouche
        data['head']['EyeX']['pin'] = yeuxx
        data['head']['EyeY']['pin'] = yeuxy
        
        json.dump(data, open('config.json', 'w', encoding='utf-8'), ensure_ascii=False)
        
        print("tetex = ", tetex)
        print("tetey = ", tetey)
        print("bouche = ", bouche)
        print("yeuxx = ", yeuxx)
        print("yeuxy = ", yeuxy)
        
    return "ok"

@app.route('/carte_update', methods=['GET'])
def carte_update():
    global InMoov
    where = request.args.get('where', 0, type=str)
    if where == 'head':
        tetex = request.args.get('tetex', 0, type=int)
        tetey = request.args.get('tetey', 0, type=int)
        bouche = request.args.get('bouche', 0, type=int)
        yeuxx = request.args.get('yeuxx', 0, type=int)
        yeuxy = request.args.get('yeuxy', 0, type=int)
        
        carte = InMoov.getCarte()
        
        InMoov.head.Rotation.setCarte(carte[tetex])
        InMoov.head.UpDown.setCarte(carte[tetey])
        InMoov.head.Mouth.setCarte(carte[bouche])
        InMoov.head.EyeX.setCarte(carte[yeuxx])
        InMoov.head.EyeY.setCarte(carte[yeuxy])
        
        data = json.load(open('config.json'))
        data['head']['rotation']['carte'] = tetex
        data['head']['UpDown']['carte'] = tetey
        data['head']['Mouth']['carte'] = bouche
        data['head']['EyeX']['carte'] = yeuxx
        data['head']['EyeY']['carte'] = yeuxy
        
        json.dump(data, open('config.json', 'w', encoding='utf-8'), ensure_ascii=False)
        
        print("tetex = ", tetex)
        print("tetey = ", tetey)
        print("bouche = ", bouche)
        print("yeuxx = ", yeuxx)
        print("yeuxy = ", yeuxy)
        
    return "ok"

@app.route('/training', methods=['POST'])
def training():
    data = json.load(open('var/data.json', "r", encoding='utf-8'))
    trainingok = request.form['training_ok']
    if trainingok == 'true':
        tag = str(np.load("var/tag.npy"))
        if tag == '': return "tag vide"
        question = str(np.load("var/question.npy"))
        for d in data['intents']:
            if d['tag'] == tag:
                for q in d['patterns']:
                    temp = True
                    if q == question: temp = False
                if temp == True:  
                    d['patterns'].append(question)
                    print("reponse OK")
    else :
        tag = request.form['tag']
        question = str(np.load("var/question.npy"))
        if question == '': return "question vide"
        pattern_r = request.form['pattern']
        if pattern_r != '':
            pattern_r = pattern_r.split(';')
        print('pattern = ', pattern_r)
        find = False
        for d in data['intents']:
            if d['tag'] == tag:
                print("tag exist : " + tag)
                find = True
                d['patterns'].append(question)
                for p in pattern_r:
                    d['responses'].append(p)
        if find == False:
            print("new tag : " + tag)
            data['intents'].append({
                'tag': tag,
                'patterns': [question.lower()],
                'responses': pattern_r
            })
    print(data)
    json.dump(data, open('var/data.json', 'w', encoding='utf-8'), ensure_ascii=False)
    np.save("var/training.npy", False)
    np.save("var/question.npy", '')
    np.save("var/reponsse.npy", '')
    return "ok"

@app.route('/get_training', methods=['GET'])
def get_training():
    if training_ == True:
        return "True"
    else :
        return "False"

@app.route('/qandr')
def qandr():
    try :
        question = str(np.load("var/question.npy"))
        reponse = str(np.load("var/reponsse.npy"))
    except :
        return("<p>Pas de question ou de reponse : parle avec le robot pour comencer à l'entrainer !</p>")
    return ("<p>Question : " + question + "</p><p>Reponsse : "+ reponse +"</p>")

@app.route('/get_tag')
def get_tag():
    data = json.load(open('var/data.json', "r", encoding='utf-8'))
    option = []
    for d in data['intents']:
        option.append(d['tag'])
    return option
        
@app.route('/trainIA')
def trainIA():
    np.save("var/trIA.npy", True)
    return "ok"

@app.route('/train_not')
def train_not():
    np.save("var/training.npy", False)
    np.save("var/question.npy", '')
    np.save("var/reponsse.npy", '')
    return "ok"

@app.route('/rstc1')
def resetc1():
    global InMoov
    InMoov.carte0.reset()
    return("ok")
    
@app.route('/rstc2')
def resetc2():
    global InMoov
    InMoov.carte1.reset()
    return("ok")

if __name__ == '__main__':
    setup([['', '', ''], ['', '', ''], ['', '', '']], Robot())
    app.run()