import cv2
import dlib
import imutils
from scipy.spatial import distance
from imutils import face_utils
from pygame import mixer
import pyttsx3
import speech_recognition as sr
import pyjokes
import webbrowser
import wikipedia
import pywhatkit
import smtplib
import datetime
import requests
import json
import random
import time
import datetime


# Initialize the mixer for sound alert
mixer.init()
mixer.music.load("C:/Users/harinijayanth/Desktop/prajwal/music.wav")  # Ensure the file exists

# Initialize the pyttsx3 engine for voice alerts and recognition
engine = pyttsx3.init()

# Initialize recognizer and set properties for voice assistant
recognizer = sr.Recognizer()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 150)  # Speech speed

# API keys (Replace with actual keys)
WEATHER_API_KEY = "92c4e8f7ec622b2703216fc2c7e365d8"
NEWS_API_KEY = "d006f57bdbf54737b569e42014591098"

# Mouth Aspect Ratio (MAR) calculation for yawning detection
def mouth_aspect_ratio(mouth):
    A = distance.euclidean(mouth[3], mouth[9])  # Vertical distance
    B = distance.euclidean(mouth[2], mouth[10])  # Vertical distance
    C = distance.euclidean(mouth[4], mouth[8])  # Vertical distance
    D = distance.euclidean(mouth[0], mouth[6])  # Horizontal distance
    mar = (A + B + C) / (3.0 * D)
    return mar

# Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_weather():
    city = 'Bengaluru'  # Replace with your city
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            return "Sorry, I couldn't fetch the weather information."
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return f"The current temperature is {temperature}°C with {weather_description}."
    except:
        return "Sorry, I couldn't fetch the weather right now."

def get_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] == 'ok':
            top_articles = data['articles'][:3]
            headlines = [article['title'] for article in top_articles]
            news_summary = ". ".join(headlines)
            return f"Here are the top news headlines: {news_summary}"
        else:
            return "Sorry, I couldn't fetch the news right now."
    except:
        return "Sorry, I couldn't fetch the news at the moment."

def take_command():
    with sr.Microphone() as source:
        print("Listening for 30 seconds...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=10)
            print("Recognizing...")
            command = recognizer.recognize_google(audio, language='en-US')
            print(f"You said: {command}")
        except sr.WaitTimeoutError:
            print("Listening timed out after 30 seconds.")
            return "None"
        except Exception as e:
            print("Sorry, I didn't catch that. Please repeat.")
            return "None"
        return command.lower()

def assistant():
    speak("Hello! You seem a bit drowsy. How are you feeling?")
    last_small_talk_time = time.time()

    while True:
        command = take_command()

        if 'how are you' in command:
            speak("I'm just a voice assistant, but thank you for asking! How are you feeling?")
        elif 'feeling good' in command or 'fine' in command:
            speak("That's great! Stay alert, stay safe!")
        elif 'tired' in command or 'sleepy' in command:
            speak("It’s important to stay alert. Do you need some music or a joke to wake you up?")
        elif 'play song' in command:
            song = command.replace('play', '').strip()
            speak(f"Playing {song} on YouTube")
            pywhatkit.playonyt(song)
        elif 'joke' in command:
            joke = pyjokes.get_joke()
            speak(joke)
        elif 'weather' in command:
            speak("Let me check the weather for you.")
            weather_info = get_weather()
            speak(weather_info)
        elif 'news' in command:
            speak("Fetching the latest news for you.")
            news = get_news()
            speak(news)
        elif 'time' in command:
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The current time is {now}.")
        elif 'date' in command:
            now = datetime.datetime.now().strftime("%Y-%m-%d")
            speak(f"The current date is {now}.")


            
            
        elif 'reminder' in command:
            speak("Don't forget to take breaks and stay hydrated while driving.")
        elif 'exit' in command or 'stop' in command:
            speak("Goodbye! Stay safe!")
            break
        current_time = time.time()
        if current_time - last_small_talk_time > random.randint(300, 600):
            small_talk = random.choice([
                "Did you know that staying hydrated can help improve concentration?",
                "Remember to take regular breaks while driving to stay alert.",
                "Fun fact: Honey never spoils.",
                "Want to hear an interesting fact? Bananas are berries, but strawberries are not.",
                "Safety first! Keep your eyes on the road.",
                "How are you feeling right now? Do you need a break?",
            ])
            speak(small_talk)
            last_small_talk_time = current_time

# Constants for MAR thresholds
MOUTH_AR_THRESHOLD = 0.5
MOUTH_AR_CONSEC_FRAMES = 9

# Initialize counters
MOUTH_COUNTER = 0

# Load Dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:/Users/harinijayanth/Desktop/prajwal/shape_predictor_68_face_landmarks.dat")

# Start video stream
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=640)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray, 0)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        mouth = shape[face_utils.FACIAL_LANDMARKS_IDXS["mouth"][0]:face_utils.FACIAL_LANDMARKS_IDXS["mouth"][1]]

        mar = mouth_aspect_ratio(mouth)

        if mar > MOUTH_AR_THRESHOLD:
            MOUTH_COUNTER += 1
            if MOUTH_COUNTER >= MOUTH_AR_CONSEC_FRAMES:
                cv2.putText(frame, "YAWNING DETECTED!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                assistant()
        else:
            MOUTH_COUNTER = 0

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
