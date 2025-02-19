from moviepy.editor import *
from moviepy.video.fx.resize import resize
from moviepy.video.fx.all import *
from gtts import gTTS
import requests
import shutil
import os
import math
import re
from PIL import Image
import numpy
import random
from TTS import text_to_speech
from script_generator import generate_image_topics_sentence
from image_reflection import resize_and_mirror


def create_video(script, keyWords, image_folder, output_path, thumbnail, topic, paidTTS):
    padding = .45
    video_clips = []
    # List of effect functions
    effect_functions = [zoom_out_effect,zoom_in_effect]

    paragraphs = re.split(r'[.!?]\s|\n', script) # Assuming paragraphs end with a period and a space

    # Thumbnail and BG Audio
    if thumbnail != "":
        download_image(thumbnail, "img_thumbnail", "thumbnail.jpg")
    shutil.copyfile("img_thumbnail/thumbnail.jpg", "imgs/default_image.jpg")
    thumbnail_clip = ImageClip("img_thumbnail/thumbnail.jpg", duration=5)
    thumbnail_clip = resize(thumbnail_clip, width=1920, height=1080) 
    video_clips.append(thumbnail_clip)
    bg_audio_clip = AudioFileClip("audio_bg/bg_audio.mp3")

    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            #TTS
            if paidTTS:
                #GOOD VOICE
                audio_filename = os.path.join("audio", f"speech_audio_{i}.mp3")
                text_to_speech(paragraph,audio_filename)
            else:
                #BAD/TEST VOICE
                tts = gTTS(paragraph, lang='en')
                audio_filename = os.path.join("audio", f"speech_audio_{i}.mp3")
                tts.save(audio_filename) 

            # Add image to video
            image_path = os.path.join(image_folder, get_google_image(keyWords, image_folder, paragraph, False, topic))

            # Get the duration of the audio clip
            audio_clip = AudioFileClip(audio_filename)
            audio_duration = audio_clip.duration + (padding)
            audio_clip.audio_fadein(0.02).audio_fadeout(0.02)

            # Create the image clip
            image_clip = ImageClip(image_path, duration=audio_duration)

            original_width, original_height = image_clip.size
            image_clip = resize(image_clip, width=original_width, height=original_height)
            #image_clip = resize(image_clip, width=1920, height=1080) 

            # Zoom effect
            random_effect_function = random.choice(effect_functions)
            image_clip = random_effect_function(image_clip, 0.04)

            # Set audio for the image clip
            video_clip_with_audio = image_clip.set_audio(audio_clip)

            # Add text to the bottom of the image clip
            #text_clip = TextClip(paragraph, fontsize=24, color='white', bg_color='black', size=(image_clip.size[0], 100))
            text_clip = TextClip(paragraph, font="Keep-Calm-Medium", kerning=-1, interline=-1, color='white', bg_color='black', size=(image_clip.size[0]-20, 100), method='caption')
            text_clip = text_clip.set_position((((image_clip.size[0] - text_clip.size[0]) / 20)-5, 'bottom')).set_duration(audio_duration)
            
            final_clip = CompositeVideoClip([video_clip_with_audio, text_clip])
            final_clip.audio = final_clip.audio.set_start(0.3)
            final_clip = final_clip.set_end(final_clip.duration -0.3)

            # Append the video clip with audio to the list
            video_clips.append(final_clip)


    # Fade Transition between clips
    video_fx_list = [video_clips[0]]
    # set padding to initial video
    idx = video_clips[0].duration - (padding)
    for video in video_clips[1:]:
        video_fx_list.append(video.set_start(idx).crossfadein((padding)))
        idx += video.duration - (padding)
        

    # Combine all the video clips at the end
    #final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip = CompositeVideoClip(video_fx_list)

    # Create a CompositeAudioClip with the background audio at a lower volume
    bg_audio_clip = bg_audio_clip.volumex(0.075)
    final_duration = final_clip.duration
    num_loops = int(final_duration / bg_audio_clip.duration) + 1
    looped_bg_audio = bg_audio_clip.audio_loop(num_loops)
    final_audio_clip = CompositeAudioClip([final_clip.audio, looped_bg_audio])  # Adjust volume as needed

    # Set the final audio clip for the combined video
    final_clip = final_clip.set_audio(final_audio_clip)

    # Write the final video to the output path
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)


    # Clear Audio Folder
    for filename in os.listdir("audio"):
            file_path = os.path.join("audio", filename)

            # Check if it's a file (not a subdirectory)
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)

    # Clear Imgs Folder
    for filename in os.listdir("imgs"):
            file_path = os.path.join("imgs", filename)

            # Check if it's a file (not a subdirectory)
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)


def get_google_image(query, output_folder, paragraph, default, topic):
    passed_in_query = query

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ID")
    user_agent = os.getenv("GOOGLE_USER_AGENT")

    if default:
        query = query[0]
    else:    
        query = query[0] + " " + generate_image_topics_sentence(topic, paragraph)
        print()
        print("(Google):")
        print("Query: " + query)
        print("Script: " + paragraph)
        print()

    # Set the query parameters
    params = {
        'q': query,
        'num': 10,
        'start': 1,
        'searchType': 'image',
        'key': api_key,
        'cx': search_engine_id,
        'imgType': 'photo',
        'fileType': 'jpg',
        'safe': 'active',
        #'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
    }

    headers = {'User-Agent': user_agent}

    try:
        # Make the GET request
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        result = response.json()
        items = result.get('items', [])
        random.shuffle(items)
       
        # Iterate through shuffled items
        for item in items:
            image_url = item.get('link')
            
            try:
                # Download the image
                response_image = requests.get(image_url, headers=headers, stream=True)
                response_image.raise_for_status()

                # Create the output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)

                # Save the image to the output folder
                image_filename = os.path.join(output_folder, 'downloaded_image.jpg')
                with open(image_filename, 'wb') as f:
                    shutil.copyfileobj(response_image.raw, f)

                try:
                    resize_and_mirror(image_filename, 1920, 1080)
                    return 'downloaded_image.jpg'
                except:
                    continue

            except requests.exceptions.RequestException as e:
                continue  # Move to the next item if download fails

    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        if hasattr(e, 'response') and e.response is not None:
            # Print only the status code number
            #print(f'ERROR (Google): {e.response.status_code}')
            print(f'ERROR (Google): {e}')

    except ValueError as e:
        # Handle JSON decoding errors
        print(f'JSON decoding error: {e}')

    # Return a default image or handle the case where no image is found
    return get_unsplash_image(passed_in_query, output_folder, paragraph, True, topic)


def get_unsplash_image(query, output_folder, paragraph, default, topic):
    # Set up Unsplash API credentials
    access_key = os.getenv("UNSPLASH_API_KEY")  # Replace with your Unsplash access key
    passed_in_query = query
    base_url = "https://api.unsplash.com"
    endpoint = "/search/photos"

    # Set your Unsplash access key
    headers = {
        "Authorization": f"Client-ID {access_key}",
    }

    if default:
        query = query[0]
    else:
        query =  query[0] + " " + generate_image_topics_sentence(topic, paragraph)
        print()
        print("(Unsplash):")
        print("Query: " + query)
        print("Script: " + paragraph)
        print()


    # Set the query parameters
    params = {
        "query": query,
        "per_page": 1,  # Adjust per_page as needed
        "width": 1920,
        "height": 1080,
        "orientation": "landscape",
    }

    try:
        params["page"] = random.randint(1, 6)

        # Make the GET request
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        result = response.json()

        # Get the URL of the first image in the search results
        if result.get('total', 0) > 0 and result.get('results'):
            image_url = result['results'][0]['urls']['regular']

            # Download the image
            response_image = requests.get(image_url, stream=True)
            response_image.raise_for_status()

            # Create the output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Save the image to the output folder
            image_filename = os.path.join(output_folder, 'downloaded_image.jpg')
            with open(image_filename, 'wb') as f:
                shutil.copyfileobj(response_image.raw, f)

            resize_and_mirror(image_filename, 1920, 1080)
            return "downloaded_image.jpg"
        else:
            print(f"No matching photo found for query: {query}")

    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        print(f"HTTP request error: {e}")

    except ValueError as e:
        # Handle JSON decoding errors
        print(f"JSON decoding error: {e}")

    # Return a default image or handle the case where no image is found
    return get_unsplash_image(passed_in_query,output_folder,paragraph,True,topic)


def zoom_out_effect(clip, zoom_ratio=0.55):
    total_duration = clip.duration

    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        initial_zoom = 1.5 + zoom_ratio  # Initial zoom level
        current_zoom = initial_zoom - zoom_ratio * t

        if current_zoom < 1.0:
            current_zoom = 1.0  # Ensure we don't zoom in beyond the original size

        new_size = [
            math.ceil(img.size[0] * current_zoom),
            math.ceil(img.size[1] * current_zoom)
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)

def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)

def download_image(url, folder_path, file_name):
    response = requests.get(url)
    
    if response.status_code == 200:
        # Check if the folder exists, create it if not
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Combine folder path and file name to get the full path
        full_path = os.path.join(folder_path, file_name)

        # Save the image to the specified path
        with open(full_path, 'wb') as file:
            file.write(response.content)
        
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
