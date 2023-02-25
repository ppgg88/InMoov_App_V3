import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix
from tqdm import tqdm
from data import get_data, wav_to_mfcc
import pickle 
import seaborn as sns

class DeepNeuralNetwork:
    def __init__(self, X, y, hidden_layers = (16, 16, 16), threshold = 0.5, from_file = None):
        self.hidden_layers = hidden_layers
        self.threshold = threshold
        self.dimensions = list(hidden_layers)
        self.dimensions.insert(0, X.shape[0])
        self.dimensions.append(y.shape[0])
        self.initialisation()

    def initialisation(self):        
        self.parametres = {}
        C = len(self.dimensions)
        for c in range(1, C):
            self.parametres['W' + str(c)] = np.random.randn(self.dimensions[c], self.dimensions[c - 1])
            self.parametres['b' + str(c)] = np.random.randn(self.dimensions[c], 1)

    def forward_propagation(self, X):
        activations = {'A0': X}
        C = len(self.parametres) // 2
        for c in range(1, C + 1):
            Z = self.parametres['W' + str(c)].dot(activations['A' + str(c - 1)]) + self.parametres['b' + str(c)]
            activations['A' + str(c)] = 1 / (1 + np.exp(-Z))
        return activations

    def back_propagation(self, y, activations):
        m = y.shape[1]
        C = len(self.parametres) // 2

        dZ = activations['A' + str(C)] - y
        gradients = {}

        for c in reversed(range(1, C + 1)):
            gradients['dW' + str(c)] = 1/m * np.dot(dZ, activations['A' + str(c - 1)].T)
            gradients['db' + str(c)] = 1/m * np.sum(dZ, axis=1, keepdims=True)
            if c > 1:
                dZ = np.dot(self.parametres['W' + str(c)].T, dZ) *activations['A' + str(c - 1)] * (1 - activations['A' + str(c - 1)])

        return gradients

    def update(self, gradients, learning_rate):
        C = len(self.parametres) // 2
        for c in range(1, C + 1):
            self.parametres['W' + str(c)] = self.parametres['W' + str(c)] - learning_rate * gradients['dW' + str(c)]
            self.parametres['b' + str(c)] = self.parametres['b' + str(c)] - learning_rate * gradients['db' + str(c)]

    def predict_proba(self, X):
        activations = self.forward_propagation(X)
        C = len(self.parametres) // 2
        Af = activations['A' + str(C)]
        return Af
    
    def predict(self, X):
        activations = self.forward_propagation(X)
        C = len(self.parametres) // 2
        Af = activations['A' + str(C)]
        return Af >= self.threshold
    
    def training(self, X_train, y_train, nb_iter=1000, learning_rate = 0.001, test = None):
        C = len(self.parametres) // 2
        training_history = np.zeros((int(nb_iter), 3))
        for i in tqdm(range(nb_iter)):
            activations = self.forward_propagation(X_train)
            gradients = self.back_propagation(y_train, activations)
            self.update(gradients, learning_rate)
            #pour afficher le logloss et l'accuracy à chaque 10 itérations
            Af = activations['A' + str(C)]
            training_history[i, 0] = (log_loss(y_train.flatten(), Af.flatten()))
            y_pred = self.predict(X_train)
            training_history[i, 1] = (accuracy_score(y_train.flatten(), y_pred.flatten()))
            if test != None:
                y_test_pred = self.predict(test[0])
                training_history[i, 2] = (accuracy_score(test[1].flatten(), y_test_pred.flatten()))
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(training_history[:, 0], label='train loss')
        plt.legend()
        plt.subplot(1, 2, 2)
        plt.plot(training_history[:, 1], label='train acc')
        plt.legend()
        if test != None:
            plt.plot(training_history[:, 2], label='test acc')
            plt.legend()
        plt.show()
        
        return training_history

    def test(self, X_test, y_test):
        y_pred = self.predict(X_test)
        #return accuracy_score(y_test.flatten(), y_pred.flatten())
        return self.accuracy(y_test, y_pred)
    
    def test_specific(self, X_test, y_test):
        y_pred = self.predict(X_test)
        responce = []
        for i in range(len(y_pred)):
            responce.append(self.accuracy(y_test, y_pred, n=i))
        return responce

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    def confusion_matrix(self, X_test, y_test):
        y_pred = self.predict(X_test)
        """affiche la matrice de confusion"""
        cnf_matrix = confusion_matrix(y_test.flatten(), y_pred.flatten())
        print(cnf_matrix)
        """affiche la matrice de confusion avec seaborn"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cnf_matrix,
            xticklabels=['hugo', 'other'],
            yticklabels=['hugo', 'other'],
            annot=True, fmt='g')
        plt.xlabel('Prediction')
        plt.ylabel('Label')
        plt.draw()

    def set_threshold(self, threshold):
        self.threshold = threshold
    
    def get_threshold(self):
        return self.threshold
                        
    def self_load(filename):
        with open(filename, 'rb') as f:
            return(pickle.load(f))
    
    def accuracy(self, y_reel, y_pred, n=None):
        if n != None:
            y_reel = y_reel[n]
            y_pred = y_pred[n]
        else :
            y_pred = y_pred.flatten()
            y_reel = y_reel.flatten()
        right = 0
        total = len(y_pred)
        for i in range(len(y_pred)):
            if y_pred[i] == y_reel[i]:
                right += 1
        return right/total

    def normalize_wav(file):
        data = wav_to_mfcc(file)[2]
        x = np.array([data])
        x = x.T
        return(x.reshape(-1, x.shape[-1])/x.max())
    
if __name__ == "__main__":
    x_train_, train_labels_, y_train_, x_test_, test_labels_, y_test_ = get_data()
    
    x_train = np.array(x_train_)
    y_train = np.array(y_train_)
    x_test = np.array(x_test_)
    y_test = np.array(y_test_)
    y_train = y_train.T
    y_test = y_test.T
    
    x_train = x_train.T
    x_train_reshape = x_train.reshape(-1, x_train.shape[-1])/x_train.max()
    
    x_test = x_test.T
    x_test_reshape = x_test.reshape(-1, x_test.shape[-1])/x_test.max()
    
    network = DeepNeuralNetwork(x_train_reshape, y_train, hidden_layers = (32,64))
    network.training(x_train_reshape, y_train, nb_iter=10000, learning_rate = 0.1, test=(x_test_reshape, y_test))
    network.confusion_matrix(x_test_reshape, y_test)
    network.save("chatbot/utile/triger.hgo")
    '''
    network = DeepNeuralNetwork.self_load("model.hgo")
    network.confusion_matrix(x_test_reshape, y_test)
    #network.training(x_train_reshape, y_train, nb_iter=500, learning_rate = 0.1, test=(x_test_reshape, y_test))
    #network.save("model.hgo")
    '''
    
    print("test accuracy Global : " + str(network.test(x_test_reshape, y_test)))
    print("test accuracy hugo : " + str(network.test_specific(x_test_reshape, y_test)[0]))
    print("test accuracy other : " + str(network.test_specific(x_test_reshape, y_test)[1]))
    
