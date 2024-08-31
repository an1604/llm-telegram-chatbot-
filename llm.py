from langchain_community.llms import Ollama
from time import time
from chat_history import chatHistory
from embeddings import embeddings
from prompts.prompts import Prompts
from learner import learner
import re

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY


def add_sample_for_learning(prompt, answer, knowledgebase_file_path):
    print("add_sample_for_learning called with prompt: {}".format(prompt))
    learner.add_sample((prompt, answer, knowledgebase_file_path))


class Llm(object):
    def __init__(self):
        self.llm = Ollama(model=model_name)  # Switched the Ollama to ChatOllama
        self.embedding_model = embeddings()
        self.chat_history = chatHistory()
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()
        self.embedd_custom_knowledgebase = False
        self.mimic_name = 'Donald'  # Default value
        self.init_msg = None
        self.end_conv = False
        self.purpose = None

        self.general_role = Prompts.get_role()

    def get_transcript(self):
        return self.chat_history.get_transcription()

    def flush(self):
        self.chat_history.flush()
        self.embedding_model.flush()

    def initialize_new_attack(self, attack_purpose, profile_name):
        self.end_conv = False
        self.mimic_name = profile_name
        Prompts.set_role(attack_purpose=attack_purpose)  # Defining the new role according to the purpose.
        self.purpose = attack_purpose
        self.embedding_model.initialize_again(attack_purpose)  # Initialize the embedding with a purpose.

        self.chat_history.set_profile_name_for_transcript(profile_name)
        self.chat_history.initialize_role(Prompts.ROLE)
        self.user_prompt = self.chat_history.get_prompt()

        self.embedd_custom_knowledgebase = False
        self.init_msg = f"Hello {self.mimic_name}, its Jason from {attack_purpose}."
        self.chat_history.add_ai_response(self.init_msg)

    def get_init_msg(self):
        return self.init_msg

    def generate_knowledgebase(self, gen_info):
        return self.llm.invoke(Prompts.KNOWLEDGEBASE_ROLE.format(gen_info=gen_info))

    def get_chat_history(self):
        return [msg for msg in self.chat_history.get_chat_history() if msg not in ['user', 'assistant']]

    def get_answer(self, prompt):
        if not self.end_conv:  # Checks the conversation state
            self.chat_history.add_human_message(prompt)
            if not self.embedd_custom_knowledgebase:
                self.embedding_model.generate_faq_embedding()
                self.embedd_custom_knowledgebase = True

            answer, apply_active_learning = self.embedding_model.get_answer_from_embedding(prompt)
            if answer is None:
                chain = self.user_prompt | self.llm
                time1 = time()
                answer = None
                validate = self.validate_number(prompt)
                if validate:
                    answer = validate
                else:
                    answer = chain.invoke({
                        "history": self.chat_history.get_chat_history(),
                        'name': self.mimic_name,  # Default value
                        # 'place': 'park',  # Default value
                        # 'target': 'address',  # Default value
                        # 'connection': 'co-worker',  # Default value,
                        # 'principles': prompts.get_principles(),
                        "context": prompt
                    })
                print(time() - time1)

            self.chat_history.add_ai_response(answer)
            self.actions_for_next_state(apply_active_learning, prompt,
                                        answer)  # Function that getting the llm for the next state

            return answer

        else:
            return 'The conversation is done. Have a great day!'

    def is_conversation_done(self):
        return self.end_conv

    def validate_number(self, prompt):
        # Regular expression to find the number
        number = re.findall(r'\d+', prompt.replace(" ", ""))
        # Convert the first match to an integer (or float if needed)
        if number:
            if self.purpose == "Bank":  # account number
                if int(number[0]) == 0:
                    return "This is not a real number"
                elif len(number[0]) == 6:
                    return "Thank you, we have solved the issue. Goodbye"

                else:
                    return "I need a 6 digit account number"
            elif self.purpose == "Hospital":
                if int(number[0]) == 0:
                    return "This is not a real number"
                elif len(number[0]) == 9:  # check for 0 at the start of the number
                    return "Thank you, we have opened your account. Goodbye"
                else:
                    return "I need a 9 digit ID"
        return None

    def actions_for_next_state(self, apply_active_learning, prompt, answer):
        if apply_active_learning:
            add_sample_for_learning(prompt, answer, self.embedding_model.knowledgebase_file_path)

        if 'bye' in answer.lower() or 'bye' in prompt.lower():
            self.end_conv = True
            # self.flush() IN THE CHATBOT CASE, WE DONT NEED TO USE flush() AT ALL!

    def get_general_answer(self, msg):
        return self.llm.invoke(self.general_role.format(context=msg))


class llm_factory(object):
    @staticmethod
    def generate_new_attack(attack_type, profile_name):
        llm = Llm()
        llm.initialize_new_attack(attack_type, profile_name)
        return llm


llm = Llm()
