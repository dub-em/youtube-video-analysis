# import pytest
import utilities, os
from config import settings

def test_search_videos_channel():
    result = utilities.search_videos_channel(settings.youtube_api, 'UCI4xp8qHD1MDErkqxb1dPbA', 3)
    assert str(type(result)) == "<class 'list'>"
    assert len(result) <= 3
    assert ('id' in result[0].keys())
    assert ('snippet' in result[0].keys())


def test_get_youtube_video_info():
    result = utilities.get_youtube_video_info(settings.youtube_api, 'ZPeNG-CJ2ZU')
    assert str(type(result)) == "<class 'dict'>"
    assert ('id' in result.keys()) 
    assert ('snippet' in result.keys()) 
    assert ('contentDetails' in result.keys())


def test_convert_duration_to_seconds():
    result_1 = utilities.convert_duration_to_seconds('PT19M58S') 
    result_2 = utilities.convert_duration_to_seconds('PT2H9S')
    result_3 = utilities.convert_duration_to_seconds('P1DT2H1S') 
    assert int(result_1) == int(1198)
    assert int(result_2) == int(7209)
    assert int(result_3) == int(93601) 


def test_download_audio():
    mp4_path, wav_path = utilities.download_audio('CH50zuS8DD0', output_path='audio_files')
    contents = os.listdir('audio_files')
    for path in [mp4_path, wav_path]:
        os.remove(path)
    assert (str(type(mp4_path)) == "<class 'str'>") 
    assert (str(type(wav_path)) == "<class 'str'>")
    assert (mp4_path.replace('audio_files/','') in contents)
    assert (wav_path.replace('audio_files/','') in contents)


def test_analyze_audio_languages_google():
    wav_path = './audio_files/Italian Conversation Practice for Beginners  Learn Italian_3.wav'
    first_language = 'English'
    second_language = 'Italian'
    percentage_transcribed, percentage_firstlang, percentage_secondlang = utilities.analyze_audio_languages_google(wav_path, first_language, second_language)
    assert (str(type(percentage_transcribed)) == "<class 'int'>") 
    assert (str(type(percentage_firstlang)) == "<class 'int'>")
    assert (str(type(percentage_secondlang)) == "<class 'int'>")


def test_delete_audios():
    mp4_path, wav_path = utilities.download_audio('CH50zuS8DD0', output_path='audio_files')
    contents = os.listdir('audio_files')
    assert (mp4_path.replace('audio_files/','') in contents)
    assert (wav_path.replace('audio_files/','') in contents)
    utilities.delete_audios([mp4_path, wav_path])
    assert ~(mp4_path.replace('audio_files/','') in contents)
    assert ~(wav_path.replace('audio_files/','') in contents)
