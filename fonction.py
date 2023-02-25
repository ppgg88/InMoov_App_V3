import json

def training(text, intents, valid, tag=None):
    data = json.load(open("var/data.json", "r", encoding='utf8'))
    print("la reponse corespond elle a la question ? o/n")
    valid = input()
    if valid == "o" or valid == "O":
        print(data)
        for d in data['intents']:
            if d['tag'] == intents:
                if text.lower() in d['patterns']:
                    break
                else:
                    d['patterns'].append(text.lower())
                    print(d['patterns'])
                    dat = open("var/data.json", "w", encoding='utf8')
                    json.dump(data, dat, ensure_ascii=False)
                    dat.close()
                    break
    else:
        print("entrer un tag qui corespondrais a la question :")
        tag = input()
        i = 0
        for d in data['intents']:
            if d['tag'] == tag:
                i += 1
                if text.lower() in d['patterns']:
                    break
                else:
                    d['patterns'].append(text.lower())
                    print(d['patterns'])
                    dat = open("var/data.json", "w", encoding='utf8')
                    json.dump(data, dat, ensure_ascii=False)
                    dat.close()
                    break
        if i == 0:
            print("tag inconnu nous alons le cree :")
            continu = True
            liste_q = []
            while continu:
                print("entrer une reponsse qui coresponde a la question :")
                liste_q.append(input())
                print("voulez vous ajouter une autre reponse ? o/n")
                if input() == "n":
                    continu = False
            data['intents'].append({"tag": tag, "patterns": [text.lower()], "responses":liste_q})
            dat = open("var/data.json", "w", encoding='utf8')
            json.dump(data, dat, ensure_ascii=False)
            dat.close()
