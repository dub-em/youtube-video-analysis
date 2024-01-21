import  json, time, warnings
import librosa, librosa.display
import utilities
import concurrent.futures
from config import settings

#Run command: python video_analyzer.py

# Ignore all UserWarnings
warnings.filterwarnings("ignore")
# warnings.filterwarnings("ignore", category=UserWarning)
# warnings.filterwarnings("ignore", category=RuntimeWarning)

# Function to analyze the  video content, given a video ID
def video_analyzer(videoid, errorlog={}):
    '''This function takes in a video ID and extracts and analyses its content,
    and then stores this content in a file'''

    overall_dictionary = {}
    errorlog = errorlog

    #------------------------------------------------------------------------------------------------------
    # Extract video details using its video ID
    # start_int = time.perf_counter()
    video_id = videoid[0]
    openaikey = videoid[1]
    try:
        video_info = utilities.get_youtube_video_info(settings.youtube_api, video_id)
    except Exception as e:
        # In case the video metadata isn't successfully extracted
        video_info = None
        errorlog[f"(get_youtube_video_info)"] = f"{type(e).__name__}: {e}"
    # finish_int = time.perf_counter()
    # print(f"Get video details finished in {round((finish_int-start_int), 2)} sec(s)")

    #------------------------------------------------------------------------------------------------------
    # converts the video duration from its iso format to seconds
    # start_int = time.perf_counter()
    if video_info:
        if video_info != None:
            overall_dictionary['ID'] = video_info['id']
            try:
                overall_dictionary['Duration'] = utilities.convert_duration_to_seconds(video_info['contentDetails']['duration'])
            except Exception as e:
                # In case the duration isn't successfully converted
                errorlog[f"(convert_duration_to_seconds)"] = f"{type(e).__name__}: {e}"
                errorlog[f"(convert_duration_to_seconds)"] = f"Duration conversion for video '{video_id}' was unsuccessful."
        else:
            # In case the video metadata isn't successfully extracted
            overall_dictionary['ID'] = video_id
            overall_dictionary['Duration'] = ''
            errorlog[f"(get_youtube_video_info)"] = f"Metadata extraction from video '{video_id}' was unsuccessful."
    else:
        # In case the video metadata isn't successfully extracted
        overall_dictionary['ID'] = video_id
        overall_dictionary['Duration'] = ''
        errorlog[f"(get_youtube_video_info)"] = f"Metadata extraction from video '{video_id}' was unsuccessful."
    # finish_int = time.perf_counter()
    # print(f"Convert duration to seconds finished in {round((finish_int-start_int), 2)} sec(s)")

    # Defines the parameters (video language in metadata) necessary for translation of subtitle if needed.
    if video_info:
        if video_info != None:
            subtitle_language = [(video_info['snippet']['defaultAudioLanguage'].split('-')[0])]
            print(subtitle_language)
            video_ids = [video_id]
        else:
            subtitle_language = ['en']
            print(subtitle_language)
            video_ids = [video_id]
    else:
        subtitle_language = ['en']
        print(subtitle_language)
        video_ids = [video_id]

    #------------------------------------------------------------------------------------------------------
    # Extracts the subtitles/transcript of the videos
    # start_int = time.perf_counter()
    try:
        video_transcript = utilities.get_video_transcript(video_ids, subtitle_language)
        # print(f"Transcript extracted successfully")
    except Exception as e: 
        # In case the transcript extraction wasn't successful
        errorlog[f"(get_video_transcript):'{subtitle_language[0]}'"] = f"{type(e).__name__}: {e}"
        video_transcript = None

    # If the video detected language was successful for transcript extraction, then the default language 'en' is checked.
    if video_transcript:
        pass
    else:
        try:
            video_transcript = utilities.get_video_transcript(video_ids, ['en'])
            subtitle_language = ['en']
        except Exception as e:
            # In case the transcript extraction wasn't successful 
            errorlog[f"(get_video_transcript):'en'"] = f"{type(e).__name__}: {e}"
            video_transcript = None    
    # finish_int = time.perf_counter()
    # print(f"Get video transcript finished in {round((finish_int-start_int), 2)} sec(s)")

    # print(video_transcript[:2])
    
    if video_transcript:
        #------------------------------------------------------------------------------------------------------
        # Using the extracted transcript, calculate the speech speed.
        # start_int = time.perf_counter()
        try:
            combined_duration, words_per_minute, audio_speed = utilities.speech_speed(video_transcript, subtitle_language[0])
            # print(f"Speech speed calculated successfully")
        except Exception as e:
            # In case the speech speed calculation was unsuccessful
            # print(f"Speech speed calculation unsuccessful")
            words_per_minute = None
            errorlog[f"(speech_speed)"] = f"{type(e).__name__}: {e}"
        # finish_int = time.perf_counter()
        # print(f"Speech speed calculation finished in {round((finish_int-start_int), 2)} sec(s)")

        # If speed speech calculation is successful, update the overall dictionary.
        if words_per_minute:
            overall_dictionary['WPM'] = f"{words_per_minute}"
            overall_dictionary['Audio Speed'] = audio_speed
            print(overall_dictionary['Duration'], combined_duration)
        else:
            # In case the speech speed calculation was unsuccessful
            overall_dictionary['WPM'] = ''
            overall_dictionary['Audio Speed'] = ''
            errorlog[f"(speech_speed)"] = f"Speech speed calculation for video '{video_id}' was unsuccessful."
        # overall_dictionary['Video Speech Percentage'] = f"{round((combined_duration/overall_dictionary['Duration'])*100)}%"
        
        #------------------------------------------------------------------------------------------------------
        # Combines the segments of the subtitle (and translates if necessary) for further processing.
        # start_int = time.perf_counter()
        try:
            combined_subt = utilities.combine_transcript_translate(video_transcript, subtitle_language[0])
        except Exception as e:
            # In case the subtitle combination was unsuccessful
            combined_subt = None
            errorlog[f"(combine_transcript_translate)"] = f"{type(e).__name__}: {e}"
        # finish_int = time.perf_counter()
        # print(f"Transcript translation calculation finished in {round((finish_int-start_int), 2)} sec(s)")
        
        #------------------------------------------------------------------------------------------------------
        # Punctuates and truncates the combined subtitle for better processign by GPT
        # start_int = time.perf_counter()
        if combined_subt:
            try:
                final_combined_punct_subt, trunc_string = utilities.subtitle_processing((combined_subt, openaikey))
                overall_dictionary['Punctuated Subtitle'] = final_combined_punct_subt  
            except Exception as e:
                # In case the subtitle punctuation was unsuccessful
                trunc_string = None
                overall_dictionary['Punctuated Subtitle'] = ''
                errorlog[f"(subtitle_processing)"] = f"{type(e).__name__}: {e}"   
        else:
            # In case the subtitle combination was unsuccessful
            trunc_string = None
            overall_dictionary['Punctuated Subtitle'] = ''
            errorlog[f"(combine_transcript_translate)"] = f"Transcript compilation and/or translation for video '{video_id}' was unsuccessful."
        # finish_int = time.perf_counter()
        # print(f"Subtitle punctuation finished in {round((finish_int-start_int), 2)} sec(s)")

        # Conduct the text analysis in a parallel manner (multithreading) using OpenAI's GPT model
        list_of_categories = ['category','summary','topic','quality','vocabulary','sentence_construct','dialogue']
        if trunc_string:
            category_and_truncstring = [(category, trunc_string, openaikey) for category in list_of_categories]
            
            #------------------------------------------------------------------------------------------------------
            # start_int = time.perf_counter()
            try:
                textanalysis_subt_dict = {}
                #Multithreading (I/O bound)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    arguments = category_and_truncstring
                    futures = [executor.submit(utilities.text_sing_analyzer, arg) for arg in arguments]

                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()
                            textanalysis_subt_dict[result[0]] = result[1]
                        except:
                            continue

                # Loads the result of the text analysis into the dictionary
                for category in list_of_categories:
                    overall_dictionary[category] = textanalysis_subt_dict[category]
            except Exception as e:
                # In case the text analysis fails.
                for category in list_of_categories:
                    overall_dictionary[category] = ''
                errorlog[f"(text_set_analyzer)"] = f"{type(e).__name__}: {e}"
                errorlog[f"(text_set_analyzer)"] = f"Text analysis for video '{video_id}' was unsuccessful."        
            # finish_int = time.perf_counter()
            # print(f"Text analysis finished in {round((finish_int-start_int), 2)} sec(s)")
            print(f"Retrieved and analysed transcript.")
        else:
            # In case the subtitle processing/punctuation fails
            for category in list_of_categories:
                overall_dictionary[category] = ''
            errorlog[f"(subtitle_processing)"] = f"Transcript processing/punctuation for video '{video_id}' was unsuccessful."
    else:
        # In case the video transcript extraction fails
        errorlog[f"(get_youtube_video_info)"] = f"Transcript extraction from video '{video_id}' was unsuccessful."
        print("Failed to retrieve transcript.")

    #------------------------------------------------------------------------------------------------------
    # start_int = time.perf_counter()
    # mp4_path, wav_path = utilities.download_audio(video_id)
    
    # audio_tempo = utilities.analyze_audio_speed(wav_path)
    # #audio_tempo = utilities.analyze_set_audio_speed(wav_path)
    # finish_int = time.perf_counter()
    # print(f"BPM analysis finished in {round((finish_int-start_int), 2)} sec(s)")

    # utilities.delete_audios([mp4_path, wav_path])

    # if audio_tempo:
    #     overall_dictionary['Audio Tempo'] = f"{round(audio_tempo)} BPM"
    #     print(f"Retrieved and analysed audio.")
    # else:
    #     print("Failed to retrieve audio.")
    
    #------------------------------------------------------------------------------------------------------
    # Convert dictionary to JSON string
    overall_response_string = json.dumps(overall_dictionary, indent=4)  # Use indent for pretty formatting
    errorlog_string = json.dumps(errorlog, indent=4)

    # Save JSON string to a file
    with open(f"./video_details/{video_id}.json", "w") as json_file:
        json_file.write(overall_response_string)
    with open(f"./video_details/error_logs/{video_id}_errorlogs.json", "w") as json_file:
        json_file.write(errorlog_string)
    print(f"{video_id} Analysis concluded!")
    return video_id


# Function to loop through the list of video metadata associated with a given channel ID (one after the other)
def channel_video_parser(channel_id):
    '''This function takes in a channel id and process all the videos (that have its dominant 
    language spoken during over 90% of the video) listed under this channel id in the channel_content 
    folder.'''

    path = f"./channel_content/{channel_id}_videos.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        channel_content = json.load(file)

    # Loops through each video ID in the .json file and parses it through the video_analyzer function.
    for key in list(channel_content.keys()):
        except_messgs = {}

        # Extracts the two languages for each video ID
        try:
            first_language = int(channel_content[key]['First Language'].split(':')[1].replace(' ','').replace('%',''))
            second_language = int(channel_content[key]['Second Language'].split(':')[1].replace(' ','').replace('%',''))
        except Exception as e:
            except_messgs[f"(language_distribution)"] = f"{type(e).__name__}: {e}"
            except_messgs[f"(language_distribution)"] = f"Language distribution for video '{key}' was either unsuccessful or is in the wrong format."
        
        # Checks if the video is majorly in one language before processing.
        if first_language:
            if (first_language >= 90) | (second_language >= 90):
                video_id = key

                try:
                    start_int2 = time.perf_counter()
                    # Conducts in-depth analysis of the video contents and saves the result (if any)
                    except_messgs = video_analyzer(video_id, except_messgs)
                    finish_int2 = time.perf_counter()
                    print(f"Finished {video_id} analysis in {round((finish_int2-start_int2)/60, 2)} minute(s)")
                except Exception as e:
                    except_messgs[f"(video_analyzer)"] = f"{type(e).__name__}: {e}"
                    except_messgs[f"(video_analyzer)"] = f"Video in-depth analysis for video '{video_id}' was unsuccessful."
                    # print(f"Error: {e}")

        # Convert error log dict to JSON strings
        except_messgs_string = json.dumps(except_messgs, indent=4)

        # Save JSON string to a file
        with open(f"./video_details/error_logs/{key}_errorlogs.json", "w") as json_file:
            json_file.write(except_messgs_string)

    print(f"Finished parsing through the videos under {channel_id}.\n")


#Function to loop through the list of videos in batches depending on the available cores (Faster!)
def channel_video_parser_modified(channel_id):
    '''This function takes in a channel id and process all the videos (that have its dominant 
    language spoken during over 90% of the video) listed under this channel id in the channel_content 
    folder.'''

    path = f"./channel_content/{channel_id}_videos.json"

    # Loads the .json file generated from extracting metadata for a given channel ID
    with open(path, 'r') as file:
        channel_content = json.load(file)

    valid_videos = []
    
    # Loops through each video ID in the .json file and parses it through the video_analyzer function.
    for key in list(channel_content.keys()):
        except_messgs = {}

        # Extracts the two languages for each video ID
        try:
            first_language = int(channel_content[key]['First Language'].split(':')[1].replace(' ','').replace('%',''))
            second_language = int(channel_content[key]['Second Language'].split(':')[1].replace(' ','').replace('%',''))
        
            if (first_language >= 90) | (second_language >= 90):
                valid_videos.append(key)
        except Exception as e:
            continue

    print(f"Length of valid videos: {len(valid_videos)}")

    # Implementing multiple keys to be used to beat the token limit per minute
    openaikey_1 = 'your_first_openai_gpt_apikey'
    openaikey_2 = 'your_second_openai_gpt_apikey'
    key_list = [openaikey_1, openaikey_2]
    count = 0
    
    num_of_cores = 6
    for i in range(0,len(valid_videos),num_of_cores):
        #This creates batches of the video IDs to be processed in parallel
        batch = valid_videos[i : i+num_of_cores]
        print(batch)

        #This piece of code loops through the list of keys and uses a new one after a number of videos
        if count >= len(key_list):
            count = 0
            openaikey = key_list[count]
        else:
            openaikey = key_list[count]
        print(openaikey, count)

        #The current API key being used is is infused into the current batch to be used for the GPT prompting.
        batch = [(videoid, openaikey) for videoid in batch]

        successfully_analysed = []
        # Multiprocessing (CPU bound)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            arguments = batch
            results = executor.map(video_analyzer, arguments)

            for result in results:
                try:
                    successfully_analysed.append(result)
                except Exception as e:
                    except_messgs[f"(video_analyzer)"] = f"{type(e).__name__}: {e}"
                    continue

        print(successfully_analysed)
        except_messgs[f"video list"] = batch
        except_messgs[f"analyzed videos"] = batch

        # Convert error log dict to JSON strings
        except_messgs_string = json.dumps(except_messgs, indent=4)

        # Save JSON string to a file
        with open(f"./video_details/error_logs/batch_{i}_errorlogs.json", "w") as json_file:
            json_file.write(except_messgs_string)

        count += 1

    print(f"Finished parsing through the videos under {channel_id}.\n")



if __name__ == "__main__":

    start = time.perf_counter()

    # Analyses the contents of the video and store it in a .json file, for a given video ID
    # video_id = 'axYAW7PuSIM'
    # video_id = 'gR0SYOCZaNY'
    # video_id = 'E4h-8rw2GlY'
    # video_id = 'bVANnFMuaW0'
    # video_id = '__Cu2nwgAjA'
    # video_id = 'BP_FvY8LT_E'
    # video_id = 'uBo0Tfk-k9w'

    # except_messgs = video_analyzer(video_id)

    # Convert error log dict to JSON strings
    # except_messgs_string = json.dumps(except_messgs, indent=4)

    # Save JSON string to a file
    # with open(f"./video_details/error_logs/{video_id}_errorlogs.json", "w") as json_file:
    #     json_file.write(except_messgs_string)
    
    # Analyses the contents of the videos listed under this channel ID and stores them in a .json file
    # channel_id = 'UCoUWq2QawqdC3-nRXKk-JUw' #EasyFrench
    # channel_id = 'UCVzyfpNuFF4ENY8zNTIW7ug' #Piece of French
    # channel_id = 'UCbj8Qov-9b5WTU1X4y7Yt-w' #French Mornings with Elisa
    channel_id = 'UCI4xp8qHD1MDErkqxb1dPbA' #innerFrench

    # channel_video_parser(channel_id)
    channel_video_parser_modified(channel_id)

    finish = time.perf_counter()
    # print(f"Finished {video_id} analysis in {round((finish-start)/60, 2)} minute(s)")
    print(f"Finished {channel_id} analysis in {round((finish-start)/60, 2)} minute(s)")