import seaborn as sn
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle


def load_history(file_path):
    history = np.load(file_path, allow_pickle=True).item()
    return history


def plot_graphs(history):
    # Plot training & validation accuracy values
    plt.plot(history['acc'])
    plt.plot(history['val_acc'])
    plt.axhline(y=0.9, color='r', linestyle='--')
    plt.title('Model accuracy')
    plt.rc('font', size=14)
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='upper left')
    plt.savefig('/home/myuser/testTweet/LID/figures/lstm_acc_epochs.png')
    plt.close()

    # Plot training & validation loss values
    plt.plot(history['loss'])
    plt.plot(history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Val'], loc='upper left')
    plt.savefig('/home/myuser/testTweet/LID/figures/lstm_loss_epochs.png')
    plt.close()


def plot_bar_chart(x_test, y_test, x_test_pad, labels, model):
    length_test = []
    for i in range(len(x_test)):
        length_test.append(len(x_test[i]))
    print(length_test)
    print(len(length_test))

    count_10 = []
    count_20 = []
    count_30 = []
    count_40 = []
    count_50 = []
    count_60 = []
    count_70 = []

    for i in range(len(length_test)):
        if length_test[i] <= 20:
            count_10.append(i)
        if 20 < length_test[i] <= 40:
            count_20.append(i)
        if 40 < length_test[i] <= 60:
            count_30.append(i)
        if 60 < length_test[i] <= 80:
            count_40.append(i)
        if 80 < length_test[i] <= 100:
            count_50.append(i)
        if 100 < length_test[i] <= 120:
            count_60.append(i)
        if length_test[i] > 120:
            count_70.append(i)

    print(len(count_10) + len(count_20) + len(count_30) + len(count_40) + len(count_50) + len(count_60) + len(count_70))
    # ---------------RANGE 0-20 CHARACTERS-------------
    print(count_10)
    print([labels[label] for label in y_test[count_10]])
    pred_10 = model.predict(x_test_pad[count_10])
    new_pred_10 = []
    tp1 = 0  # true positives/correctly classified

    for i in range(len(pred_10)):
        a = np.argmax(pred_10[i])
        new_pred_10.append(a)
        if new_pred_10[i] == y_test[count_10[i]]:
            tp1 = tp1 + 1
    print([labels[label] for label in new_pred_10])
    print("Number of tweets of character length 0-20:", len(pred_10))
    print("Accuracy for tweet lengths 0-20 characters:", (tp1 / len(pred_10)))

    # ---------------RANGE 20-40 CHARACTERS-------------
    print(count_20)
    print([labels[label] for label in y_test[count_20]])
    pred_20 = model.predict(x_test_pad[count_20])
    new_pred_20 = []
    tp2 = 0  # true positives/correctly classified
    for i in range(len(pred_20)):
        a = np.argmax(pred_20[i])
        new_pred_20.append(a)
        if new_pred_20[i] == y_test[count_20[i]]:
            tp2 = tp2 + 1
    print([labels[label] for label in new_pred_20])
    print("Number of tweets of character length 20-40:", len(pred_20))
    print("Accuracy for tweet lengths 20-40 characters:", (tp2 / len(pred_20)))

    # ---------------RANGE 40-60 CHARACTERS-------------
    print(count_30)
    print([labels[label] for label in y_test[count_30]])
    pred_30 = model.predict(x_test_pad[count_30])
    new_pred_30 = []
    tp3 = 0  # true positives/correctly classified
    for i in range(len(pred_30)):
        a = np.argmax(pred_30[i])
        new_pred_30.append(a)
        if new_pred_30[i] == y_test[count_30[i]]:
            tp3 = tp3 + 1
    print([labels[label] for label in new_pred_30])
    print("Number of tweets of character length 40-60:", len(pred_30))
    print("Accuracy for tweet lengths 40-60 characters:", (tp3 / len(pred_30)))

    # ---------------RANGE 60-80 CHARACTERS-------------
    print(count_40)
    print([labels[label] for label in y_test[count_40]])
    pred_40 = model.predict(x_test_pad[count_40])
    new_pred_40 = []
    tp4 = 0  # true positives/correctly classified
    for i in range(len(pred_40)):
        a = np.argmax(pred_40[i])
        new_pred_40.append(a)
        if new_pred_40[i] == y_test[count_40[i]]:
            tp4 = tp4 + 1
    print([labels[label] for label in new_pred_40])
    print("Number of tweets of character length 60-80:", len(pred_40))
    print("Accuracy for tweet lengths 60-80 characters:", (tp4 / len(pred_40)))

    # ---------------RANGE 80-100 CHARACTERS-------------
    print(count_50)
    print([labels[label] for label in y_test[count_50]])
    pred_50 = model.predict(x_test_pad[count_50])
    new_pred_50 = []
    tp5 = 0  # true positives/correctly classified
    for i in range(len(pred_50)):
        a = np.argmax(pred_50[i])
        new_pred_50.append(a)
        if new_pred_50[i] == y_test[count_50[i]]:
            tp5 = tp5 + 1
    print([labels[label] for label in new_pred_50])
    print("Number of tweets of character length 80-100:", len(pred_50))
    print("Accuracy for tweet lengths 80-100 characters:", (tp5 / len(pred_50)))

    # ---------------RANGE 100-120 CHARACTERS-------------
    print(count_60)
    print([labels[label] for label in y_test[count_60]])
    pred_60 = model.predict(x_test_pad[count_60])
    new_pred_60 = []
    tp6 = 0  # true positives/correctly classified
    for i in range(len(pred_60)):
        a = np.argmax(pred_60[i])
        new_pred_60.append(a)
        if new_pred_60[i] == y_test[count_60[i]]:
            tp6 = tp6 + 1
    print([labels[label] for label in new_pred_60])
    print("Number of tweets of character length 100-120:", len(pred_60))
    print("Accuracy for tweet lengths 100-120 characters:", (tp6 / len(pred_60)))

    # ---------------RANGE >120 CHARACTERS-------------
    print(count_70)
    print([labels[label] for label in y_test[count_70]])
    pred_70 = model.predict(x_test_pad[count_70])
    new_pred_70 = []
    tp7 = 0  # true positives/correctly classified
    for i in range(len(pred_70)):
        a = np.argmax(pred_70[i])
        new_pred_70.append(a)
        if new_pred_70[i] == y_test[count_70[i]]:
            tp7 = tp7 + 1
    print([labels[label] for label in new_pred_70])
    print("Number of tweets of character length >120:", len(pred_70))
    print("Accuracy for tweet lengths >120 characters:", (tp7 / len(pred_70)))

    # --------------------------------------------------------------
    print()
    objects = ('0-20', '20-40', '40-60', '60-80', '80-100', '100-120', '120-140')
    y_pos = np.arange(len(objects))
    performance = [(tp1 / len(pred_10)), (tp2 / len(pred_20)), (tp3 / len(pred_30)), (tp4 / len(pred_40)),
                   (tp5 / len(pred_50)),
                   (tp6 / len(pred_60)), (tp7 / len(pred_70))]

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Accuracy')
    plt.xlabel('Character length of tweet')
    plt.title('Accuracy for different character lengths of tweets')
    plt.savefig('/home/myuser/testTweet/LID/figures/bar_chart_May_18_15epochs.png')
    plt.close()


def main():
    history_lstm = load_history('/home/myuser/testTweet/LID/saved_model/history_preprocessed.npy')
    plot_graphs(history_lstm)


if __name__  == "__main__":
    main()

