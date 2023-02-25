
from os import listdir
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from random import randint
import numpy as np

def load_data(path='datasets'):
    """Load data from datasets folder"""
    possible_labels = listdir(path)
    data_brut = []
    for i in possible_labels:
        data_temp = listdir(path+'/'+i)
        data_brut.append(data_temp)
    return data_brut, possible_labels

def wav_to_mfcc(file_path):
    """Convert wav to mfcc"""
    sample_rate, samples = wavfile.read(file_path)
    samples = samples[:48000]
    if len(samples) < 48000:
        for i in range(48000-len(samples)):
            samples = np.append(samples,0.0000000001)
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

    spectrogram = spectrogram/spectrogram.max()
    
    return frequencies, times, spectrogram

def plot_spectrogram(frequencies, times, spectrogram):
    """Plot spectrogram"""
    plt.pcolormesh(times, frequencies, spectrogram)
    plt.imshow(spectrogram)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
    

def get_mfcc_data(data_brut, labels):
    """Get mfcc data from wav files"""
    mfcc_data = []
    for i in labels: mfcc_data.append([])
    for i in range(len(labels)):
        for j in range(len(data_brut[i])):
            mfcc_data[i].append(wav_to_mfcc('datasets/'+labels[i]+"/"+data_brut[i][j])[2])
    return mfcc_data

def get_data(train=0.8):
    """Get data from datasets folder train and test"""
    if train > 1 or train < 0:
        print("Train must be between 0 and 1")
        return
    data_brut, labels = load_data()
    mfcc_data = get_mfcc_data(data_brut, labels)
    print(mfcc_data[0][0].shape)
    train_data = []
    train_labels = []
    y_train = []
    y_test = []
    test_data = []
    test_labels = []
    temp = []
    for t in range(len(labels)):
        temp.append(0)
    for t in range(len(labels)):
        inital_len = len(mfcc_data[t])
        for i in reversed(range(int(inital_len*train))): #on prend 'train'% des données pour l'entrainement
            y_train.append(temp.copy())
            y_train[int(inital_len*train)-i-1][t] = 1
            
            train_data.append(mfcc_data[t][i])
            train_labels.append(labels[t])
            mfcc_data[t].pop(i)
    
    for t in range(len(labels)):
        for i in range(len(mfcc_data[t])):
            y_test.append([0,0])
            y_test[i][t] = 1
            test_data.append(mfcc_data[t][i])
            test_labels.append(labels[t])
    
    return train_data, train_labels, y_train, test_data, test_labels, y_test


if __name__ == '__main__':
    train_data, train_labels, y_train, test_data, test_labels, y_test = get_data()
    print(len(train_data))
    
    