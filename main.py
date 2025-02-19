# main.py
from script_generator import generate_script
from script_generator import generate_thumbnail
from video_editor import create_video


#************************ INPUTS START ************************#
topic = "Public speaking. Top 10 tips you have to know!"
image_keyWords = ["public speaking"]
thumbnail_prompt="public speaking"
image_folder = "imgs"
output_path = "output/output.mp4"
#************************ INPUTS END #************************#
# :::ideas:::
#Exploring Ancient Mysteries: Unraveling the Secrets of Lost Civilizations
#The Evolution of Technology: From Stone Tools to AI
#Unsolved Mysteries: Bizarre Cases That Baffle Experts

#---------- THUMBNAIL ----------#
user_response = input('Generate New Thumbnail? (y/n): ')
thumbnail = ""
if user_response.lower() == 'y':
    thumbnail = generate_thumbnail(thumbnail_prompt)

#---------- VIDEO SCRIPT ----------#
user_response = input('Generate New Script? (y/n): ')   
if user_response.lower() == 'y':
    script = generate_script(topic)

    # CLEAN OUT CHAPTER HEADERS
    lines = script.split('\n')
    filtered_lines = [line for line in lines if not line.startswith('Chapter')]
    filtered_text = '\n'.join(filtered_lines)

    with open('script.txt', 'w') as file:
        file.write(script)
    print("\n...Script created and saved. Length: ")
    print(len(script))

#---------- CREATE VIDEO ----------#
user_response = input('Create video based on "script.txt" file? (y/n): ')   
if user_response.lower() == 'y':
    with open('script.txt', 'r') as file:
        script = file.read()
    user_response = input('Paid TTS? (y/n): ')   
    if user_response.lower() == 'y':
        paidTTS = True
    else:
        paidTTS = False
    print("Video creation starting...\n\n")
    create_video(script, image_keyWords, image_folder, output_path, thumbnail, topic, paidTTS)