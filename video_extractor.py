import librosa, librosa.display
import json, time, warnings
import numpy as np
import concurrent.futures
import utilities
from config import settings

#Run command: python video_extractor.py

# Ignore all UserWarnings
warnings.filterwarnings("ignore")
# warnings.filterwarnings("ignore", category=UserWarning)
# warnings.filterwarnings("ignore", category=RuntimeWarning)


# Function to extract videos, given a keyword.
def video_extraction_keyword(keywords, max_results):
    '''This function extracts the given number of results given a keyword,
    and saves the file in a .json file for later reference.'''

    overall_dictionary = {}
    
    # Replace 'KEYWORDS' with the keywords you want to search for
    keywords = keywords

    # Set the maximum number of results to retrieve (default is 5)
    max_results = max_results

    videos = utilities.search_videos_keyword(settings.youtube_api, keywords, max_results)

    if videos:
        for index in range(len(videos)):
            overall_dictionary[f"{videos[index]['id']['videoId']}"] = {}
            overall_dictionary[f"{videos[index]['id']['videoId']}"]['Video_URL'] = f"https://www.youtube.com/watch?v={videos[index]['id']['videoId']}"
            overall_dictionary[f"{videos[index]['id']['videoId']}"]['Details'] = videos[index]

    # Convert dictionary to JSON string
    overall_response_string = json.dumps(overall_dictionary, indent=4)  # Use indent for pretty formatting

    # Save JSON string to a file
    with open(f"{keywords}_videos.json", "w") as json_file:
        json_file.write(overall_response_string)


# Function to extract video metadata from a channel palylist, given a channel ID.
def video_extraction_channel(channel_id, max_results):
    '''This function extracts the given number of results given a channel ID, conduct
    a language distribution analysis for each video ID and saves the file in a .json file 
    for later reference.'''

    overall_dictionary = {}
    except_messgs = {}
    
    # Replace 'KEYWORDS' with the keywords you want to search for
    channel_id = channel_id

    # Set the maximum number of results to retrieve (default is 5)
    max_results = max_results

    #------------------------------------------------------------------------------------------------------
    # Extract video metadata for a limited number of videos from the channel playlist
    # start_int = time.perf_counter()
    try:
        videos = utilities.search_videos_channel(settings.youtube_api, channel_id, max_results)
    except Exception as e:
        # In case the video metadata extraction is unsuccessful.
        except_messgs[f"(search_videos_channel)"] = f"{type(e).__name__}: {e}"

    if videos == []:
        except_messgs[f"(search_videos_channel)"] = f"Video metadata extraction from channel '{channel_id}' was unsuccessful."
    # finish_int = time.perf_counter()
    # print(f"Channel video content extraction finished in {round((finish_int-start_int), 2)} sec(s)")
    
    #------------------------------------------------------------------------------------------------------
    # Loops through each video ID and checks the language distribution of the languages present in the video.
    if videos: #Checks if video variable was successfully declared
        if videos != []: #Checks if any video metadata was successfully extracted

            video_id_list = []
            for index in range(len(videos)):
                # Extracts the necessary metadata for the given video
                video_id = videos[index]['snippet']['resourceId']['videoId']
                video_id_list.append(video_id)
                overall_dictionary[video_id] = {}
                except_messgs[video_id] = {}
                overall_dictionary[video_id]['Video_URL'] = f"https://www.youtube.com/watch?v={video_id}"
                overall_dictionary[video_id]['Title'] = videos[index]['snippet']['title']
                overall_dictionary[video_id]['PublishedAt'] = videos[index]['snippet']['publishedAt']

            print(f"Number of video IDs: {len(video_id_list)}")
            num_of_cores = 6
            for i in range(0,len(video_id_list),num_of_cores):
                #The video list is broken down into batches and processed in parallel.
                batch = video_id_list[i : i+num_of_cores]
                print(batch)
            
                # Multiprocessing (CPU bound)
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    arguments = batch
                    results = executor.map(utilities.video_langdist, arguments)

                    for result in results:
                        #Results from each audio files language analysis is extracted.
                        try:
                            for key in list(result[1].keys()):
                                overall_dictionary[result[0]][key] = result[1][key]
                            for key in list(result[2].keys()):
                                except_messgs[result[0]] = result[2][key]
                        except Exception as e:
                            except_messgs[f"(video_analyzer)"] = f"{type(e).__name__}: {e}"
                            continue
    
    # Convert meta data dictionary and error log dict to JSON strings
    overall_response_string = json.dumps(overall_dictionary, indent=4)
    except_messgs_string = json.dumps(except_messgs, indent=4)

    # Save JSON string to a file
    with open(f"./channel_content/{channel_id}_videos.json", "w") as json_file:
        json_file.write(overall_response_string)
    with open(f"./channel_content/error_logs/{channel_id}_errorlogs.json", "w") as json_file:
        json_file.write(except_messgs_string)



if __name__ == "__main__":

    start = time.perf_counter()
    # key_word = 'English Tutorial'
    # channel_id = 'UCoUWq2QawqdC3-nRXKk-JUw' #EasyFrench
    channel_id = 'UCVzyfpNuFF4ENY8zNTIW7ug' #Piece of French
    # channel_id = 'UCbj8Qov-9b5WTU1X4y7Yt-w' #French Mornings with Elisa
    # channel_id = 'UCI4xp8qHD1MDErkqxb1dPbA' #innerFrench

    # Extracts the video using the specified keyword
    try:
        # video_extraction_keyword(key_word, 10)
        video_extraction_channel(channel_id, 6)

        # print(f"{key_word} YouTube videos extraction was successsful!")
        print(f"{channel_id} YouTube videos extraction was successsful!")
    except Exception as e:
        print(f"Error: {e}")

        # print(f"{key_word} YouTube videos extraction was unsuccesssful!")
        print(f"{channel_id} YouTube videos extraction was unsuccesssful!")

    finish = time.perf_counter()
    print(f"Channel video content and language analysis finished in {round((finish-start)/60, 2)} minute(s)")