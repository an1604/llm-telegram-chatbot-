import logging
import os

import speech_recognition as sr
import json
import uuid
from pydub import AudioSegment
from aiogram import types

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_descriptions = [
    "Our project focuses on harnessing the power of AI to simulate social engineering attacks, using advanced technologies like generative AI and deepfakes. The goal is to help organizations improve their awareness and preparedness against the ever-changing landscape of digital threats.",

    "Our project leverages cutting-edge AI technologies, including generative AI and deepfakes, to create realistic simulations of social engineering attacks. By providing organizations with hands-on experience, we aim to enhance their ability to recognize and respond to sophisticated digital threats.",

    "Through the use of advanced AI and deepfake technology, our project aims to replicate social engineering attack scenarios with high fidelity. This initiative is designed to boost organizational readiness and resilience by exposing them to evolving digital threats in a controlled environment."
]


async def download_file(file: types.File, destination_path, bot):
    try:
        logging.info("download_file() called.")
        destination_file = await bot.download_file(file, destination_path)
        logging.info("file saved in: {}".format(destination_file))
        return destination_file
    except Exception as e:
        logging.error(f'Error from download_file() --> {e}')
        return None


def get_filename_path():
    try:
        file_name = os.path.join(os.getcwd(), 'audios', f"audio_{str(uuid.uuid4())}.wav")
        logging.info(f"filename is: {file_name}")
        return file_name
    except Exception as e:
        logging.error(f'Error from get_filename_path() --> {e}')
        return None


async def handle_audio_message(message, bot):
    transcription = None
    try:
        if message.content_type == 'audio':
            logging.info("Found an audio message sent to the bot.")
            audio = message.audio

            if audio:
                try:
                    file_name = get_filename_path()

                    audio.save(file_name)
                    logging.info(f"Audio file saved: {file_name}")
                    transcription = transcribe_audio(file_name)
                    logging.info(f"FROM AUDIO: Transcription generated: {transcription}")
                except Exception as e:
                    logging.error(f"Error in handle_audio_message while processing audio: {e}")
            else:
                logging.warning("Audio message received but no audio file found.")
        else:
            document = message.document
            if document:
                try:
                    logging.info("Found a document message sent to the bot.")
                    file_name = get_filename_path()

                    if await download_file(document, file_name, bot) is None:
                        logging.error("Document message received but no audio file found.")
                        return None

                    logging.info(f"Document file saved: {file_name}")
                    transcription = transcribe_audio(file_name)
                    logging.info(f"FROM DOCUMENT: Transcription generated: {transcription}")
                except Exception as e:
                    logging.error(f"Error in handle_audio_message while processing document: {e}")
            else:
                logging.warning("Message received but neither audio nor document was found.")
    except Exception as e:
        logging.error(f"Unexpected error in handle_audio_message: {e}")

    return transcription


def mp3_to_wav(file_path):
    wav_file_path = file_path.replace('.mp3', '.wav')
    try:
        audio = AudioSegment.from_mp3(file_path)
        audio.export(wav_file_path, format='wav')
        os.remove(file_path)
        file_path = wav_file_path
        return file_path
    except Exception as e:
        logging.error(f"Error in mp3_to_wav: {e}")
        return


def transcribe_audio(file_path, json_file_path=None, return_as_string=False):
    if file_path.endswith('.mp3'):
        file_path = mp3_to_wav(file_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as audio_file:
            recognizer.adjust_for_ambient_noise(audio_file)
            audio_data = recognizer.record(audio_file)
            transcription = recognizer.recognize_google(audio_data)
            logging.info(f"Transcription: {transcription}")
            if not return_as_string and json_file_path:
                with open(json_file_path, 'w') as json_file:
                    json.dump({"transcription": transcription}, json_file)
                logging.info(f"Transcription saved to {json_file_path}")
            else:
                return transcription
    except sr.UnknownValueError:
        logging.error("Error in transcribe_audio: Google Web Speech API could not understand the audio")
    except sr.RequestError as e:
        logging.error(f"Error in transcribe_audio: Could not request results from Google Web Speech API; {e}")
    except Exception as e:
        logging.error(f"Error in transcribe_audio: {e}")
