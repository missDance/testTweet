#benchmarking
#https://towardsdatascience.com/language-detection-benchmark-using-production-data-8fe6c1f9f46c

import pandas as pd
import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import LSTM, Embedding, Bidirectional
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, plot_confusion_matrix
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import seaborn as sn
import matplotlib.pyplot as plt
from keras.callbacks import EarlyStopping
import os

vocab_size = 1000
embedding_dim = 128
max_length = 150
num_epochs = 15

trunc_type = 'post'
padding_type = 'post'
oov_tok = '<OOV>'


def read_all(class_names):
    max_rows = 10000
    d = dict(zip(class_names, range(0, 5)))
    print(d)
    pd.options.display.max_colwidth = 1000

    df1 = (pd.read_csv("2000_Eng_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df1 = df1.drop(index=0)
    df1 = df1.reset_index(drop=True)

    df2 = (pd.read_csv("2000_Swe_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df2 = df2.drop(index=0)
    df2 = df2.reset_index(drop=True)

    df3 = (pd.read_csv("2000_Rus_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df3 = df3.drop(index=0)
    df3 = df3.reset_index(drop=True)

    df4 = (pd.read_csv("2000_Por_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df4 = df4.drop(index=0)
    df4 = df4.reset_index(drop=True)

    df5 = (pd.read_csv("2000_Spa_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df5 = df5.drop(index=0)
    df5 = df5.reset_index(drop=True)

    df6 = (pd.read_csv("2000_Ger_tweets_label.csv", usecols=['tweets', 'language']).dropna(
        subset=['tweets', 'language']).assign(tweets=lambda x: x.tweets.str.strip()).head(max_rows))
    df6 = df6.drop(index=0)
    df6 = df6.reset_index(drop=True)

    all_data = pd.concat([df1, df2, df3, df4, df5], ignore_index=True, sort=False)

    # Clean tweet data
    for i in range(len(all_data)):
        all_data['tweets'][i] = clean_up(all_data['tweets'][i])

    all_data = all_data.sample(frac=1).reset_index(drop=True)
    all_data['language'] = all_data['language'].map(d, na_action='ignore')

    print(all_data)
    print(len(all_data))
    return all_data


def clean_up(line):
    # remove url
    line = re.sub(r'http\S+', '', line)

    # lowercase all letters
    # words = line.split()
    # words = [word.lower() for word in words]
    # line = ' '.join(words)

    # remove emojis
    line = remove_emojies(line)

    # remove excessive signs
    remove_characters = re.compile('[/(){}\[\]\|.,;:!?"<>^*&%$]')
    line = remove_characters.sub('', line)
    return line


def remove_emojies(text):
    # Ref: https://gist.github.com/Alex-Just/e86110836f3f93fe7932290526529cd1#gistcomment-3208085
    # Ref: https://en.wikipedia.org/wiki/Unicode_block
    emojies = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])")
    text = re.sub(emojies, r'', text)
    return text


def split_data(frame):
    train, validation = train_test_split(frame, test_size=0.20)
    #validation, test = train_test_split(validation, test_size=0.5)
    train = train.reset_index(drop=True)
    validation = validation.reset_index(drop=True)
    #test = test.reset_index(drop=True)
    test = validation
    return train, validation, test


def encode_ngram_text(text, n):
    text = [text[i:i + n] for i in range(len(text) - n + 1)]  # splitting up the text as n-grams
    text = [ord(text[i]) for i in range(len(text))]  # converting every character to its unicode
    return text


def pad(data, length):
    new_data = []
    for row in data:
        new_row = np.pad(row, (0, length - len(row)), constant_values=0)
        new_data.append(new_row)
    data = new_data
    return data


def decode(text):
    text = [chr(text[i]) for i in range(len(text))]  # converting every character back from unicode to its original
    return text


# returns maximum integer value in the tokenized dictionary of a character in the dataset
def max_dict_value(data):
    n = 0
    for row in data:
        for element in row:
            if element > n:
                n = element
    return n


def run_lstm(vocab_size, embedding_dim, class_names, x_train_pad, y_train, x_validation_pad, y_validation,
             x_test_pad, y_test, x_test, tokenizer, num_epochs, labels):
    model = Sequential()
    model.add(Embedding(vocab_size, embedding_dim))
    model.add(Bidirectional(LSTM(embedding_dim)))
    model.add(Dense(embedding_dim, activation='relu'))
    model.add(Dense(len(class_names), activation='softmax'))
    model.summary()
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['acc'])
    es = EarlyStopping(monitor='val_loss', min_delta=0.01, patience=240, mode='min', restore_best_weights=True)

    history = model.fit(x_train_pad, y_train, batch_size=32, epochs=num_epochs,
                        validation_data=(x_validation_pad, y_validation), verbose=1, callbacks=[es])

    # Save the entire model as a SavedModel.
    model.save('saved_model/my_model')


    loss, acc = model.evaluate(x_validation_pad, y_validation, verbose=1)
    print("Loss: %.2f" % loss)
    print("Validation Accuracy: %.2f" % acc)

    loss2, acc2 = model.evaluate(x_test_pad, y_test, verbose=1)
    print("Loss: %.2f" % loss2)
    print("Test Accuracy: %.2f" % acc2)

    # Plot training & validation accuracy values
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.axhline(y=0.9, color='r', linestyle='--')
    plt.title('Model accuracy')
    plt.rc('font', size=14)
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc='upper left')
    plt.savefig('5_lang_2000_May_06.png')
    plt.close()

    # Plot training & validation loss values
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Val'], loc='upper left')
    plt.savefig('5_lang_loss_2000_May_06.png')
    plt.close()

    #y_pred = model.predict_classes(x_test_pad)
    y_pred2 = model.predict_classes(x_validation_pad)
    #print(tf.math.confusion_matrix(labels=y_test, predictions=y_pred))
    #print(classification_report(y_test, y_pred))
    #print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_validation, y_pred2))
    cnf_matrix = confusion_matrix(y_validation, y_pred2)
    print(cnf_matrix)

    y_validation_cm = [labels[row] for row in y_validation]
    y_pred2_cm = [labels[row] for row in y_pred2]
    data_cn = {'y_Actual': y_validation_cm, 'y_Predicted': y_pred2_cm}
    df = pd.DataFrame(data_cn, columns=['y_Actual', 'y_Predicted'])
    confusion_matrix_2 = pd.crosstab(df['y_Actual'], df['y_Predicted'], rownames=['True labels'], colnames=['Predicted labels'])

    plt.title("Confusion matrix over test data")
    sn.heatmap(confusion_matrix_2, annot=True, fmt='g', xticklabels=True, yticklabels=True, cmap='Blues')
    plt.yticks(rotation=0)
    plt.xticks(rotation=0)
    plt.savefig('confusion_matrix_May_06.png')
    plt.close()

    print('\n# Generate predictions for 6 samples from the hold-out dataset (testing set)')
    predictions = model.predict(x_test_pad)
    print('prediction 1:', x_test[0], predictions[0], "Correct label:", y_test[0])
    print('prediction 2:', x_test[1], predictions[1], "Correct label:", y_test[1])
    print('prediction 3:', x_test[2], predictions[2], "Correct label:", y_test[2])
    print('prediction 4:', x_test[3], predictions[3], "Correct label:", y_test[3])
    print('prediction 5:', x_test[4], predictions[4], "Correct label:", y_test[4])
    print('prediction 6:', x_test[5], predictions[5], "Correct label:", y_test[5])
    print()

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

    print(len(count_10)+len(count_20)+len(count_30)+len(count_40)+len(count_50)+len(count_60)+len(count_70))
    #---------------RANGE 0-20 CHARACTERS-------------
    print(count_10)
    print([labels[label] for label in y_test[count_10]])
    pred_10 = model.predict(x_test_pad[count_10])
    new_pred_10 = []
    tp1 = 0 #true positives/correctly classified

    for i in range(len(pred_10)):
        a = np.argmax(pred_10[i])
        new_pred_10.append(a)
        if new_pred_10[i] == y_test[count_10[i]]:
            tp1 = tp1 + 1
    print([labels[label] for label in new_pred_10])
    print("Number of tweets of character length 0-20:", len(pred_10))
    print("Accuracy for tweet lengths 0-20 characters:", (tp1/len(pred_10)))

    # ---------------RANGE 20-40 CHARACTERS-------------
    print(count_20)
    print([labels[label] for label in y_test[count_20]])
    pred_20 = model.predict(x_test_pad[count_20])
    new_pred_20 = []
    tp2 = 0 #true positives/correctly classified
    for i in range(len(pred_20)):
        a = np.argmax(pred_20[i])
        new_pred_20.append(a)
        if new_pred_20[i] == y_test[count_20[i]]:
            tp2 = tp2 + 1
    print([labels[label] for label in new_pred_20])
    print("Number of tweets of character length 20-40:", len(pred_20))
    print("Accuracy for tweet lengths 20-40 characters:", (tp2/len(pred_20)))

    # ---------------RANGE 40-60 CHARACTERS-------------
    print(count_30)
    print([labels[label] for label in y_test[count_30]])
    pred_30 = model.predict(x_test_pad[count_30])
    new_pred_30 = []
    tp3 = 0 #true positives/correctly classified
    for i in range(len(pred_30)):
        a = np.argmax(pred_30[i])
        new_pred_30.append(a)
        if new_pred_30[i] == y_test[count_30[i]]:
            tp3 = tp3 + 1
    print([labels[label] for label in new_pred_30])
    print("Number of tweets of character length 40-60:", len(pred_30))
    print("Accuracy for tweet lengths 40-60 characters:", (tp3/len(pred_30)))

    # ---------------RANGE 60-80 CHARACTERS-------------
    print(count_40)
    print([labels[label] for label in y_test[count_40]])
    pred_40 = model.predict(x_test_pad[count_40])
    new_pred_40 = []
    tp4 = 0 #true positives/correctly classified
    for i in range(len(pred_40)):
        a = np.argmax(pred_40[i])
        new_pred_40.append(a)
        if new_pred_40[i] == y_test[count_40[i]]:
            tp4 = tp4 + 1
    print([labels[label] for label in new_pred_40])
    print("Number of tweets of character length 60-80:", len(pred_40))
    print("Accuracy for tweet lengths 60-80 characters:", (tp4/len(pred_40)))

    # ---------------RANGE 80-100 CHARACTERS-------------
    print(count_50)
    print([labels[label] for label in y_test[count_50]])
    pred_50 = model.predict(x_test_pad[count_50])
    new_pred_50 = []
    tp5 = 0 #true positives/correctly classified
    for i in range(len(pred_50)):
        a = np.argmax(pred_50[i])
        new_pred_50.append(a)
        if new_pred_50[i] == y_test[count_50[i]]:
            tp5 = tp5 + 1
    print([labels[label] for label in new_pred_50])
    print("Number of tweets of character length 80-100:", len(pred_50))
    print("Accuracy for tweet lengths 80-100 characters:", (tp5/len(pred_50)))

    # ---------------RANGE 100-120 CHARACTERS-------------
    print(count_60)
    print([labels[label] for label in y_test[count_60]])
    pred_60 = model.predict(x_test_pad[count_60])
    new_pred_60 = []
    tp6 = 0 #true positives/correctly classified
    for i in range(len(pred_60)):
        a = np.argmax(pred_60[i])
        new_pred_60.append(a)
        if new_pred_60[i] == y_test[count_60[i]]:
            tp6 = tp6 + 1
    print([labels[label] for label in new_pred_60])
    print("Number of tweets of character length 100-120:", len(pred_60))
    print("Accuracy for tweet lengths 100-120 characters:", (tp6/len(pred_60)))

    # ---------------RANGE >120 CHARACTERS-------------
    print(count_70)
    print([labels[label] for label in y_test[count_70]])
    pred_70 = model.predict(x_test_pad[count_70])
    new_pred_70 = []
    tp7 = 0 #true positives/correctly classified
    for i in range(len(pred_70)):
        a = np.argmax(pred_70[i])
        new_pred_70.append(a)
        if new_pred_70[i] == y_test[count_70[i]]:
            tp7 = tp7 + 1
    print([labels[label] for label in new_pred_70])
    print("Number of tweets of character length >120:", len(pred_70))
    print("Accuracy for tweet lengths >120 characters:", (tp7/len(pred_70)))

    #--------------------------------------------------------------
    print()
    objects = ('0-20', '20-40', '40-60', '60-80', '80-100', '100-120', '120-140')
    y_pos = np.arange(len(objects))
    performance = [(tp1/len(pred_10)), (tp2/len(pred_20)), (tp3/len(pred_30)), (tp4/len(pred_40)), (tp5/len(pred_50)),
                   (tp6/len(pred_60)), (tp7/len(pred_70))]

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Accuracy')
    plt.xlabel('Character length of tweet')
    plt.title('Accuracy for different character lengths of tweets')
    plt.savefig('bar_chart_May_06_15epochs.png')
    plt.close()


    new_line = "perfekta tweets - cool"
    new_sequences = tokenizer.texts_to_sequences([new_line])
    new_padded = pad_sequences(new_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    new_prediction = model.predict(new_padded)
    print('prediction of:', new_line, new_prediction[0], "Correct label: Svenska eller Engelska?")


def main():
    class_names = ["English", "Swedish", "Spanish", "Portuguese", "Russian"]

    all_data = read_all(class_names)

    train, validation, test = split_data(all_data)

    x_train = np.asarray([np.asarray(text) for text in train['tweets']])
    y_train = np.asarray([np.asarray(label) for label in train['language']])

    x_validation = np.asarray([np.asarray(text) for text in validation['tweets']])
    y_validation = np.asarray([np.asarray(label) for label in validation['language']])

    x_test = np.asarray([np.asarray(text) for text in test['tweets']])
    y_test = np.asarray([np.asarray(label) for label in test['language']])

    print(x_train)
    print(x_train[0])
    print(x_train[1])
    print(all_data['tweets'])
    # print(all_data['language'])

    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok, char_level=True)
    #tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
    tokenizer.fit_on_texts(train['tweets'])
    word_index = tokenizer.word_index
    print(dict(list(word_index.items())[0:10]))

    train_sequences = tokenizer.texts_to_sequences(x_train)
    x_train_pad = pad_sequences(train_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    validation_sequences = tokenizer.texts_to_sequences(x_validation)
    x_validation_pad = pad_sequences(validation_sequences, maxlen=max_length, padding=padding_type,
                                     truncating=trunc_type)
    test_sequences = tokenizer.texts_to_sequences(x_test)
    x_test_pad = pad_sequences(test_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

    print(x_train_pad[0])
    print(y_train[0])

    print(x_train_pad[1])
    print(y_train[1])

    print("Maximum integer value of a character in: training set:", max_dict_value(x_train_pad))
    print("Maximum integer value of a character in: validation set:", max_dict_value(x_validation_pad))
    print("Maximum integer value of a character in: test set:", max_dict_value(x_test_pad))

    run_lstm(vocab_size, embedding_dim, class_names, x_train_pad, y_train, x_validation_pad, y_validation, x_test_pad,
             y_test, x_test, tokenizer, num_epochs, class_names)


if __name__ == "__main__":
    main()
