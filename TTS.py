import requests
import os
import time

key = os.getenv("TTS_API_KEY")
voice = os.getenv("TTS_VOICE_ID")

def text_to_speech(text, output):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": key
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    max_retries = 2  # Set the maximum number of retries
    retry_delay = 30  # Set the delay between retries (in seconds)

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(output, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

            # If execution reaches here, the request was successful
            return

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed. Error: {e}")

            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")
                break
