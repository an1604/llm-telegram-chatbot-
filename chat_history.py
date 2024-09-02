import os
import logging
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class chatHistory(object):
    def __init__(self, name='default'):
        try:
            self.chat_history = []
            self.role = None
            self.name = name
            self.directory = "chat_history"
            logging.info(f"Chat history initialized with name: {name}")
        except Exception as e:
            logging.error(f"Error in chatHistory.__init__: {e}")

    def set_profile_name_for_transcript(self, profile_name):
        try:
            self.name = profile_name
            logging.info(f"Profile name set to: {profile_name}")
        except Exception as e:
            logging.error(f"Error in chatHistory.set_profile_name_for_transcript: {e}")

    def flush(self, save_attack=True):
        try:
            if save_attack:
                self.save_chat()
            self.chat_history.clear()
            self.role = None
            logging.info("Chat history flushed.")
        except Exception as e:
            logging.error(f"Error in chatHistory.flush: {e}")

    def save_chat(self):
        try:
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
                logging.info(f"Directory created: {self.directory}")

            file_path = os.path.join(self.directory, f'chat_history-{self.name}.txt')
            with open(file_path, 'w') as f:
                for role, prompt in self.chat_history:
                    f.write(f'{role}: {prompt}\n')
            logging.info(f"Chat history saved to: {file_path}")
        except IOError as e:
            logging.error(f"Error in chatHistory.save_chat: {e}")
        except Exception as e:
            logging.error(f"Error in chatHistory.save_chat: {e}")

    def initialize_role(self, role: SystemMessage):
        try:
            self.role = role
            logging.info(f"Role initialized: {role}")
        except Exception as e:
            logging.error(f"Error in chatHistory.initialize_role: {e}")

    def add_human_message(self, msg: str):
        try:
            message = ("user", f"{msg}")
            self.chat_history.append(message)
            logging.info(f"Added human message: {msg}")
        except Exception as e:
            logging.error(f"Error in chatHistory.add_human_message: {e}")

    def add_system_message(self, msg: str):
        try:
            self.chat_history.extend([("system", f"{msg}")])
            logging.info(f"Added system message: {msg}")
        except Exception as e:
            logging.error(f"Error in chatHistory.add_system_message: {e}")

    def add_ai_response(self, res: str):
        try:
            msg = ("assistant", f"{res}")
            self.chat_history.append(msg)
            logging.info(f"Added AI response: {res}")
        except Exception as e:
            logging.error(f"Error in chatHistory.add_ai_response: {e}")

    def get_window(self):
        try:
            if self.chat_history:
                logging.info("Returning latest chat history item.")
                return self.chat_history[-1]
            logging.warning("Chat history is empty.")
            return None
        except Exception as e:
            logging.error(f"Error in chatHistory.get_window: {e}")

    def get_chat_history(self):
        try:
            logging.info("Returning entire chat history.")
            return self.chat_history
        except Exception as e:
            logging.error(f"Error in chatHistory.get_chat_history: {e}")

    def update_chat_history(self, user_message, ai_response):
        try:
            self.chat_history.extend([
                HumanMessage(content=user_message),
                AIMessage(content=ai_response)
            ])
            logging.info(f"Chat history updated with user message: {user_message} and AI response: {ai_response}")
        except Exception as e:
            logging.error(f"Error in chatHistory.update_chat_history: {e}")

    def get_prompt(self):
        try:
            logging.info("Returning current role prompt.")
            return self.role
        except Exception as e:
            logging.error(f"Error in chatHistory.get_prompt: {e}")

    def get_transcription(self):
        try:
            transcription = "\n".join(f"{role}: {msg}" for role, msg in self.chat_history) + "\n"
            logging.info("Transcription generated.")
            return transcription
        except Exception as e:
            logging.error(f"Error in chatHistory.get_transcription: {e}")
