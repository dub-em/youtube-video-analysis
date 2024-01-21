# import pytest
import utilities, os, json
from config import settings
import variables

def test_execute_function_wrapper():
    def add_two(number):
        return number+2
    result = utilities.execute_function_wrapper(add_two, 2)
    assert result == 4


def test_search_videos_keyword():
    result = utilities.search_videos_keyword(settings.youtube_api, 'English Tutorial', 3)
    assert str(type(result)) == "<class 'list'>"
    assert len(result) <= 3
    result = utilities.search_videos_keyword(settings.youtube_api, 'English Tutorial')
    assert str(type(result)) == "<class 'list'>"
    assert len(result) <= 5


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


def test_subt_sing_translator():
    input_set = (1, "Elle nous entend Elisa ?", 'fr')
    result = utilities.subt_sing_translator(input_set)
    assert str(type(result)) == "<class 'tuple'>"
    assert len(result) == 2
    assert result[0] == 1
    assert str(type(result[1])) == "<class 'str'>"


def test_subt_set_translator():
    sublist = [(1, "Elle nous entend Elisa ?", 'fr'), (2, "Oui, oui, c'est bon, je vous entends.\nIl y a quelques mois,", 'fr')]
    result = utilities.subt_set_translator(sublist)
    assert str(type(result)) == "<class 'dict'>"
    assert len(list(result.keys())) == 2
    assert (1 in result.keys()) & (2 in result.keys())
    for value in list(result.values()):
        assert str(type(value)) == "<class 'str'>"


def test_combine_transcript_translate():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    video_transcript = transcript_dict['transcript']
    correct_result = transcript_dict['combined subtitle']
    combined_subt = utilities.combine_transcript_translate(video_transcript, 'fr')
    assert combined_subt == correct_result


def test_subt_sing_punctuator():
    part_sub = (1, "Elle nous entend Elisa")
    result = utilities.subt_sing_punctuator(part_sub)
    assert str(type(result)) == "<class 'tuple'>"
    assert len(result) == 2
    assert result[0] == 1
    assert str(type(result[1])) == "<class 'str'>"


def test_subt_set_punctuator():
    sublist = [(1, "Elle nous entend Elisa"), (2, "Oui oui c'est bon je vous entends.\nIl y a quelques mois")]
    result = utilities.subt_set_punctuator(sublist)
    assert str(type(result)) == "<class 'dict'>"
    assert len(list(result.keys())) == 2
    assert (1 in result.keys()) & (2 in result.keys())
    for value in list(result.values()):
        assert str(type(value)) == "<class 'str'>"


def test_subtitle_processing():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    combined_subt = transcript_dict['combined subtitle']
    final_combined_punct_subt, trunc_string = utilities.subtitle_processing(combined_subt)
    assert len(trunc_string) <= 13000


def test_gpt_punctuator():
    information = "Elle nous entend Elisa"
    result = utilities.gpt_punctuator(information)
    assert str(type(result)) == "<class 'str'>"


def test_gpt_categorizer():
    # information = "Elle nous entend, Elisa ? Oui, oui, c'est bon, je vous entends.\nIl y a quelques mois, j'ai fait une vid\u00e9o qui s'appelle \"Why French People don't Understand you\". Pourquoi les Fran\u00e7ais ne vous comprennent pas ? Dans cette vid\u00e9o, j'ai essay\u00e9 d'expliquer que parfois, certaines erreurs de prononciation rendent la compr\u00e9hension plus compliqu\u00e9e pour les francophones qui vous \u00e9coutent."
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_categorizer(information)
    assert str(type(result)) == "<class 'str'>"
    assert ('Basic' in result) | ('Medium' in result) | ('Advanced' in result)


def test_gpt_summarizer():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_summarizer(information)
    assert str(type(result)) == "<class 'str'>"
    sentence = list(result.split('.'))
    assert len(sentence) <= 10


def test_gpt_topicmodeller():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_topicmodeller(information)
    assert str(type(result)) == "<class 'str'>"


def test_gpt_qualitycheck():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_qualitycheck(information)
    assert str(type(result)) == "<class 'str'>"
    assert ('Poorly articulated' in result) | ('Moderately articulated' in result) | ('Very articulated' in result)


def test_gpt_vocabularycheck():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_vocabularycheck(information)
    assert str(type(result)) == "<class 'str'>"
    assert ('Basic' in result) | ('Intermediate' in result) | ('Advanced' in result)


def test_gpt_sentenceconstruct():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_sentenceconstruct(information)
    assert str(type(result)) == "<class 'str'>"
    assert ('Basic' in result) | ('Intermediate' in result) | ('Advanced' in result)


def test_gpt_dialogue():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)
    information = transcript_dict['truncated subtitle']
    result = utilities.gpt_dialogue(information)
    assert str(type(result)) == "<class 'str'>"
    assert ('Present' in result) | ('Not Present' in result)


def test_text_sing_analyzer():
    path = f"./tests/test_storage/test_transcript.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        transcript_dict = json.load(file)

    trunc_string = transcript_dict['truncated subtitle']
    input_set = ('sentence_construct', trunc_string)
    result = utilities.text_sing_analyzer(input_set)
    assert str(type(result)) == "<class 'tuple'>"
    assert len(result) == 2
    assert result[0] == 'sentence_construct'
    assert str(type(result[0])) == "<class 'str'>"
    assert str(type(result[1])) == "<class 'str'>"


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


def test_download_audio():
    mp4_path, wav_path = utilities.download_audio('CH50zuS8DD0', output_path='audio_files')
    contents = os.listdir('audio_files')
    for path in [mp4_path, wav_path]:
        os.remove(path)
    assert (str(type(mp4_path)) == "<class 'str'>") 
    assert (str(type(wav_path)) == "<class 'str'>")
    assert (mp4_path.replace('audio_files/','') in contents)
    assert (wav_path.replace('audio_files/','') in contents)


def test_analyze_audio_speed():
    path = f"./tests/test_storage/temp_segment_test.wav"

    result = utilities.analyze_audio_speed(path)
    assert (str(type(result)) == "<class 'numpy.float64'>")    


def test_audiolang_sing_processor_google():
    audio_path = './audio_files/Italian Conversation Practice for Beginners  Learn Italian_3.wav'
    first_language = 'English'
    second_language = 'Italian'
    language_isocode = variables.language_isocode
    language_list = []
    for language in [first_language.lower(), second_language.lower()]:
        language_list.append(language_isocode[language])
    print(language_list)
    input_set = (1, [0, 5000], audio_path, language_list)
    result = utilities.audiolang_sing_processor_google(input_set)
    assert str(type(result)) == "<class 'tuple'>"
    assert len(result) == 4
    assert (str(type(result[0])) == "<class 'int'>") & (result[0] == 1)
    assert (str(type(result[1])) == "<class 'int'>") & (result[1] <= 1)
    assert (str(type(result[2])) == "<class 'int'>") & (result[2] <= 1)
    assert (str(type(result[3])) == "<class 'int'>") & (result[3] <= 1)


def test_audiolang_set_processor_google():
    audio_path = './audio_files/Italian Conversation Practice for Beginners  Learn Italian_3.wav'
    first_language = 'English'
    second_language = 'Italian'
    language_isocode = variables.language_isocode
    language_list = []
    for language in [first_language.lower(), second_language.lower()]:
        language_list.append(language_isocode[language])
    print(language_list)
    sublist = [(1, [0, 5000], audio_path, language_list),(2, [5001, 10000], audio_path, language_list)]
    result = utilities.audiolang_set_processor_google(sublist)
    assert str(type(result)) == "<class 'tuple'>"
    assert len(result) == 4
    assert (str(type(result[0])) == "<class 'int'>") & (result[0] == 2)
    assert (str(type(result[1])) == "<class 'int'>") & (result[1] <= 2)
    assert (str(type(result[2])) == "<class 'int'>") & (result[2] <= 2)
    assert (str(type(result[3])) == "<class 'int'>") & (result[3] <= 2)


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


def test_list_files_in_folder():
    folder_path = f"./tests/test_storage"
    result = utilities.list_files_in_folder(folder_path)
    assert str(type(result)) == "<class 'list'>"
    assert len(result) == 2

