import speech_recognition as sr


def transcribe(file_name):
    r = sr.Recognizer()
    with sr.AudioFile(file_name) as source:
        audio = r.record(source)  # read the entire audio file

        return r.recognize_google(audio)

def create_script(file_name):
        script = open('generated_script.txt', 'w+')
        text = transcribe(file_name)
        script.write(text)