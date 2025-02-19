from dotenv import find_dotenv, load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from openai import OpenAI
import requests, os

load_dotenv(find_dotenv())

def generate_script(topic):
    template = """
    You are a captivating storyteller tasked with creating an engaging video script for a YouTube channel documentary in the style of YouTuber 'Lindsay Ellis'. Your goal is to produce a detailed narrative with a minimum length of 8,000 characters and 15 paragraphs. Your script should be rich in detail and insights, avoiding overly concise or point-by-point explanations. Dive deep into the topic and craft a compelling storyline that will captivate and educate the audience. You possess comprehensive knowledge on the subject and should provide detailed insights without resorting to hypothetical scenarios. Avoid headings or titles, instead, focus on weaving a seamless narrative that flows smoothly from one point to the next. Generate the text for the video topic below, ensuring it meets the required length and maintains the audience's attention throughout. The final output should be broken into at least 15 different paragraphs of text with multiple sentences in each paragraph. Each paragraph should have at least 6 sentence and each sentence should be no longer than 18 words. Once this is generated, confirm it is greater than 8,000 characters and 15 paragraphs, if not, add more to the script until it is that length. The most important part of your response is that it is around 8,000 characters long.
    Topic: "{topic}"
    """

    prompt = PromptTemplate(template=template, input_variables=["topic"])

    story_llm = LLMChain(llm=ChatOpenAI(
        model_name="gpt-3.5-turbo-16k",temperature=.6), prompt=prompt, verbose=False)
    
    script = story_llm.predict(topic=topic)

    return script


def generate_thumbnail(topic):
    client = OpenAI()

    response = client.images.generate(
        model="dall-e-3",
        prompt=topic,
        size="1792x1024",
        quality="standard",
        n=1,
    )

    download_image(response.data[0].url, "img_thumbnail", "thumbnail.jpg")
    return response.data[0].url


def generate_image_topics_sentence(topic, paragraph):
    template = """
    Your goal is to generate a noun, phrase, event, person, or thing based on a specific sentence. This should ideally be a single word or two max. This could include details about its history, key figures, events, or iconic elements. For instance, consider the current sentence we're exploring: "{paragraph}". Generate a single concrete and visually specific noun, phrase, event, person, or thing that aligns with the previous sentence as well as the overall topic of "{topic}".
    Preferably, the result is directly related or pulled from the last sentence in the sentence if possible.
    It is extremely important that you think about how the generated result, when passed into an image generation tool, would consistently return images directly related to both sentence and the topic! In otherwords the result cannot be vague because it will not return a valid image but it is important that it is not too unique that an image wouldn't exist. If the generated result is too vague or unique and does NOT meet that criteria, then find a new result that by itself relates. It MUST relate not only the sentence(s) but the overall topic "{topic}"!
    Return ONLY the single word or two result and nothing else.
    """
    prompt = PromptTemplate(template=template, input_variables=["topic","paragraph"])

    story_llm = LLMChain(llm=ChatOpenAI(
        model_name="gpt-3.5-turbo",temperature=.45), prompt=prompt, verbose=False)
    
    image_topic_sentence = story_llm.predict(topic=topic, paragraph=paragraph)

    return image_topic_sentence


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