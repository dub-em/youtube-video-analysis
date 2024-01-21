from google.cloud import translate_v2 as translate
from google.cloud import speech
from google.oauth2 import service_account
import speech_recognition as sr
import warnings, time, io

# Ignore all DeprecationWarnings
warnings.filterwarnings("ignore", category=UserWarning)


def translate_text_paid(target: str, text: str) -> dict:
    """Translates text into the target language using paid google cloud translator API.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    credentials_path = 'magicweb-solution-0f16c8830e66.json'

    # Create credentials using google-auth
    credential = service_account.Credentials.from_service_account_file(credentials_path)

    translate_client = translate.Client(credentials=credential)

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result


def transcribe_audio_paid(audio_path: str):

    credential_path = 'magicweb-solution-507c34d6556a.json'
    credential = service_account.Credentials.from_service_account_file(credential_path)
    client = speech.SpeechClient(credentials=credential)

    #Load the audio file
    audio_file = audio_path

    with io.open(audio_file, 'rb') as f:
        content = f.read()
        audio = speech.RecognitionAudio(content=content)
        
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='fr-FR',
        audio_channel_count = 2,
    )

    response = client.recognize(config=config, audio=audio)
    print(response)


def trasncribe_audio_free(audio_path: str):
    recognizer = sr.Recognizer()

    try:
        # Transcribe the segment while trying the first language
        with sr.AudioFile(audio_path) as audio_file:
            audio_data = recognizer.record(audio_file)
            text = recognizer.recognize_google(audio_data, language='fr-FR')
            print(f"Segment Transcription:", text)
    except sr.UnknownValueError:
        print(f"Segment - Speech Recognition could not understand audio")
        pass
    except sr.RequestError as e:
        print(f"Segment - Could not request results from Google Speech Recognition service; {e}")
        pass


if __name__ == "__main__":
    start = time.perf_counter()

    # translated = translate_text_paid('it', 'How are you?')
    transcribe_audio_paid('temp_segment_test.wav')
    # trasncribe_audio_free('temp_segment_test.wav')

    finish = time.perf_counter()

    print(f"Finished in {round((finish-start)/60, 2)} minute(s)")