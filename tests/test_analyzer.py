import utilities, os, warnings, json, video_analyzer
from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_get_youtube_video_info():
    result = utilities.get_youtube_video_info(settings.youtube_api, 'ZPeNG-CJ2ZU')
    assert str(type(result)) == "<class 'dict'>"
    assert ('id' in result.keys()) 
    assert ('snippet' in result.keys()) 
    assert ('contentDetails' in result.keys())
    sec_result = result['snippet']
    assert ('defaultAudioLanguage' in sec_result.keys())


def test_convert_duration_to_seconds():
    result_1 = utilities.convert_duration_to_seconds('PT19M58S') 
    result_2 = utilities.convert_duration_to_seconds('PT2H9S')
    result_3 = utilities.convert_duration_to_seconds('P1DT2H1S') 
    assert int(result_1) == int(1198)
    assert int(result_2) == int(7209)
    assert int(result_3) == int(93601)


def test_get_video_transcript():
    result = utilities.get_video_transcript(['ZPeNG-CJ2ZU'], ['fr'])
    assert str(type(result)) == "<class 'list'>"
    assert 'text' in result[0].keys()
    assert 'duration' in result[0].keys()

    path = f"./tests/test_storage/test_transcript.json"
    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    assert result == transcript_dict['transcript']


def test_speech_speed():
    path = f"./tests/test_storage/test_transcript.json"
    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    video_transcript = transcript_dict['transcript']
    combined_duration, words_per_minute, audio_speed = utilities.speech_speed(video_transcript, 'fr')
    assert str(type(audio_speed)) == "<class 'str'>"
    assert str(type(words_per_minute)) == "<class 'int'>"
    assert str(type(combined_duration)) == "<class 'int'>"
    assert (audio_speed == 'Slow Speech') | (audio_speed == 'Normal Speech') | (audio_speed == 'Fast Speech')


def test_combine_transcript_translate():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    video_transcript = transcript_dict['transcript']
    correct_result = transcript_dict['combined subtitle']
    combined_subt = utilities.combine_transcript_translate(video_transcript, 'fr')
    assert combined_subt == correct_result


def test_subtitle_processing():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    combined_subt = transcript_dict['combined subtitle']
    final_combined_punct_subt, trunc_string = utilities.subtitle_processing(combined_subt)
    assert len(trunc_string) <= 13000


def test_text_set_analyzer():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)

    trunc_string = transcript_dict['truncated subtitle']
    sublist = [('sentence_construct', trunc_string),('dialogue', trunc_string)]
    result = utilities.text_set_analyzer(sublist)

    assert 'sentence_construct' in result.keys()
    assert 'dialogue' in result.keys()
    assert len(list(result.keys())) == 2


def test_video_analyzer():
    error_log = video_analyzer.video_analyzer('ZPeNG-CJ2ZU')
    assert str(type(error_log)) == "<class 'dict'>"

    contents = os.listdir(f"./video_details")
    assert 'ZPeNG-CJ2ZU.json' in contents

    with open(f"./video_details/ZPeNG-CJ2ZU.json", 'r') as file:
        video_detail = json.load(file)
    assert len(list(video_detail.keys())) == 12
    os.remove(f"./video_details/ZPeNG-CJ2ZU.json")


