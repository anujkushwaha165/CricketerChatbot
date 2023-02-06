# import necessary libraries
from flask import Flask, request, app, jsonify, url_for, render_template
from nltk.stem import WordNetLemmatizer
import nltk
import io
import re
import docx
import random
import string  # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
nltk.download('popular', quiet=True)  # for downloading packages
# uncomment the following only the first time
# nltk.download('punkt') # first-time use only
# nltk.download('wordnet') # first-time use only


app = Flask(__name__)

# function defination for reading the word file (corpus)


def getText(filename):
    doc = docx.Document(filename)
    article_text = ''
    for para in doc.paragraphs:
        article_text += para.text
    return article_text.lower()


# function call with doc as parameter and got corpus in article text
article_text = getText('sample1.docx')


# preprocess our text to remove all the special characters and empty spaces

article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
article_text = re.sub(r'\s+', ' ', article_text)
article_sentences = nltk.sent_tokenize(article_text)
article_words = nltk.word_tokenize(article_text)
wnlemmatizer = nltk.stem.WordNetLemmatizer()

# helper functions that will remove the punctuation from the user input text and will also lemmatize the text


def perform_lemmatization(tokens):
    return [wnlemmatizer.lemmatize(token) for token in tokens]


punctuation_removal = dict((ord(punctuation), None)
                           for punctuation in string.punctuation)


def get_processed_text(document):
    return perform_lemmatization(nltk.word_tokenize(document.lower().translate(punctuation_removal)))


# Responding to Greetings

greeting_inputs = ("hey", "good morning", "good evening", "morning", "evening",
                   "hi", "whatsup", "hello", "how are you?", "hi there", "hii", "whats up")
greeting_responses = ["hey", "hey hows you?", "Howdy Partner!", "Hello", "How are you doing?",
                      "Greetings!", "How do you do?", "hello, how you doing?", "hello", "Welcome, I am good and you."]
age_input = ["how old are you?",
             "when is your birthday?", "when was you born?"]
age_output = ['I am unborn', "I am chat bot bro I never born"]
name_input = ["what's your name?",
              "what are you called?", "who are you?", 'who are you']
name_output = ["My name is Chatbot.", "I'm Chatbot."]
replygreetings = ['great', 'good', 'very good', 'awesome',
                  'not good', 'nice', "i am good", 'i am fine', 'i am feeling good', 'doing good']
reply = ["Sorry I didn't understand.", "Please try again!",
         "May be I don't know about him.", "Sorry! I think I have to learn alot.", 'Please check the spelling!']
# greeting function


def generate_greeting_response(greeting):
    if greeting.lower() in greeting_inputs:

        return random.choice(greeting_responses)
    if greeting.lower() in age_input or 'age' in greeting.lower():
        return random.choice(age_output)
    if greeting.lower() in name_input:

        return random.choice(name_output)+"I am an AI."+"\n Please ask Indian about cricketer"
    if greeting.lower() in replygreetings:
        return "sounds good ! \n Please ask about Indian cricketer"


# function that takes in user input, finds the cosine similarity of the user input and return output from corpus

def generate_response(user_input):
    Chatbot_response = ''
    article_sentences.append(user_input)

    word_vectorizer = TfidfVectorizer(
        tokenizer=get_processed_text, stop_words='english')
    all_word_vectors = word_vectorizer.fit_transform(article_sentences)
    similar_vector_values = cosine_similarity(
        all_word_vectors[-1], all_word_vectors)
    similar_sentence_number = similar_vector_values.argsort()[0][-2]

    matched_vector = similar_vector_values.flatten()
    matched_vector.sort()
    vector_matched = matched_vector[-2]

    if vector_matched == 0:
        Chatbot_response = Chatbot_response + \
            random.choice(reply)+"\n Please ask about Indian cricketer"
        return Chatbot_response
    else:
        Chatbot_response = Chatbot_response + \
            article_sentences[similar_sentence_number]
        return Chatbot_response


word_vectorizer = TfidfVectorizer(
    tokenizer=get_processed_text, stop_words='english')
all_word_vectors = word_vectorizer.fit_transform(article_sentences)
# finding similarity with input and the corpes
similar_vector_values = cosine_similarity(
    all_word_vectors[-1], all_word_vectors)
# sort the list containing the cosine similarities of the vectors
similar_sentence_number = similar_vector_values.argsort()[0][-2]

# app route will open html file


@app.route("/")
def home():
    return render_template("index.html")

# get method


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    continue_dialogue = True
    # print("Hello, I am your Chatbot. You can ask me any question regarding Cricket:")
    while (continue_dialogue == True):
        human_text = userText
        human_text = human_text.lower()
        if human_text != 'bye':
            if human_text == 'thanks' or human_text == 'thank you very much' or human_text == 'thank you':
                continue_dialogue = False
                return "Chatbot: Most welcome"
            else:
                if generate_greeting_response(human_text) != None:
                    return "Chatbot: " + generate_greeting_response(human_text)
                else:
                    # print("Chatbot: ", end="")
                    # print(generate_response(human_text))
                    x = "Chatbot: "+generate_response(human_text)
                    article_sentences.remove(human_text)
                    return x
        else:
            continue_dialogue = False
            return "Chatbot: Good bye and take care of yourself..."


if __name__ == "__main__":
    app.run(debug=True)
