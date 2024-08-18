from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate, PromptTemplate
import os


class chatHistory(object):
    def __init__(self, name='default'):
        self.chat_history = []
        self.role = None
        self.name = name
        self.directory = "chat_history"

    def set_profile_name_for_transcript(self, profile_name):
        self.name = profile_name

    def flush(self, save_attack=True):
        if save_attack:
            self.save_chat()
        self.chat_history.clear()
        self.role = None

    def save_chat(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        file_path = os.path.join(self.directory, f'chat_history-{self.name}.txt')
        with open(file_path, 'w') as f:
            for role, prompt in self.chat_history:
                f.write(f'{role}: {prompt}\n')

    def initialize_role(self, role: SystemMessage):
        self.role = role

    def add_human_message(self, msg: str):
        message = ("user", f"{msg}")
        self.chat_history.append(message)

    def add_system_message(self, msg: str):
        self.chat_history.extend(SystemMessage(content=msg))

    def add_ai_response(self, res: str):
        msg = ("assistant", f"{res}")
        self.chat_history.append(msg)

    def get_window(self):
        return self.chat_history[-1]

    def get_chat_history(self):
        return self.chat_history

    def update_chat_history(self, user_message, ai_response):
        self.chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=ai_response)
        ])

    def get_prompt(self):
        return self.role

    def get_transcription(self):
        return "\n".join(f"{role}: {msg}" for role, msg in self.chat_history) + "\n"
