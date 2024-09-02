import os
import logging
import re
from time import time
from langchain_community.llms import Ollama
from chat_history import chatHistory
from embeddings import embeddings
from prompts.prompts import Prompts
from learner import learner

# Configure logging with function name
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY


def add_sample_for_learning(prompt, answer, knowledgebase_file_path):
    try:
        logging.info(f"add_sample_for_learning called with prompt: {prompt}")
        learner.add_sample((prompt, answer, knowledgebase_file_path))
    except Exception as e:
        logging.error(f"Error in add_sample_for_learning: {e}")


class Llm(object):
    def __init__(self):
        try:
            logging.info("Initializing LLM...")
            self.llm = Ollama(model=model_name)
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
            logging.info("LLM initialized")
        except Exception as e:
            logging.error(f"Error in Llm.__init__: {e}")

    def get_transcript(self):
        try:
            return self.chat_history.get_transcription()
        except Exception as e:
            logging.error(f"Error in Llm.get_transcript: {e}")

    def flush(self):
        try:
            logging.info("Flushing chat history and embedding model")
            self.chat_history.flush()
            self.embedding_model.flush()
        except Exception as e:
            logging.error(f"Error in Llm.flush: {e}")

    def initialize_new_attack(self, attack_purpose, profile_name):
        try:
            logging.info(f"Initializing new attack: {attack_purpose} with profile: {profile_name}")
            self.end_conv = False
            self.mimic_name = profile_name
            Prompts.set_role(attack_purpose=attack_purpose)
            self.purpose = attack_purpose

            if 'chat' not in attack_purpose.lower():
                self.embedding_model.initialize_again(attack_purpose)

            self.chat_history.set_profile_name_for_transcript(profile_name)
            self.chat_history.initialize_role(Prompts.ROLE)
            self.user_prompt = self.chat_history.get_prompt()

            self.embedd_custom_knowledgebase = False
            self.init_msg = f"Hello {self.mimic_name}, it's Jason from {attack_purpose}."
            self.chat_history.add_ai_response(self.init_msg)
        except Exception as e:
            logging.error(f"Error in Llm.initialize_new_attack: {e}")

    def get_init_msg(self):
        try:
            return self.init_msg
        except Exception as e:
            logging.error(f"Error in Llm.get_init_msg: {e}")

    def get_chat_history(self):
        try:
            return [msg for msg in self.chat_history.get_chat_history() if msg not in ['user', 'assistant']]
        except Exception as e:
            logging.error(f"Error in Llm.get_chat_history: {e}")

    def get_answer(self, prompt):
        try:
            if not self.end_conv:
                logging.info(f"Getting answer for prompt: {prompt}")
                self.chat_history.add_human_message(prompt)

                if 'chat' in self.purpose.lower():
                    return self.get_general_answer(prompt)

                if not self.embedd_custom_knowledgebase:
                    self.embedding_model.generate_faq_embedding()
                    self.embedd_custom_knowledgebase = True

                answer, apply_active_learning = self.embedding_model.get_answer_from_embedding(prompt)
                if answer is None:
                    chain = self.user_prompt | self.llm
                    time1 = time()
                    validate = self.validate_number(prompt)
                    if validate:
                        answer = validate
                    else:
                        answer = chain.invoke({
                            "history": self.chat_history.get_chat_history(),
                            'name': self.mimic_name,
                            "context": prompt
                        })
                    logging.info(f"Response time: {time() - time1} seconds")
                    self.chat_history.add_ai_response(answer)
                    self.actions_for_next_state(apply_active_learning, prompt, answer)

                return answer
            else:
                return 'The conversation is done. Have a great day!'
        except Exception as e:
            logging.error(f"Error in Llm.get_answer: {e}")

    def is_conversation_done(self):
        try:
            return self.end_conv
        except Exception as e:
            logging.error(f"Error in Llm.is_conversation_done: {e}")

    def validate_number(self, prompt):
        try:
            number = re.findall(r'\d+', prompt.replace(" ", ""))
            if number:
                if self.purpose == "Bank":
                    if int(number[0]) == 0:
                        return "This is not a real number"
                    elif len(number[0]) == 6:
                        return "Thank you, we have solved the issue. Goodbye"
                    else:
                        return "I need a 6 digit account number"
                elif self.purpose == "Hospital":
                    if int(number[0]) == 0:
                        return "This is not a real number"
                    elif len(number[0]) == 9:
                        return "Thank you, we have opened your account. Goodbye"
                    else:
                        return "I need a 9 digit ID"
            return None
        except Exception as e:
            logging.error(f"Error in Llm.validate_number: {e}")

    def actions_for_next_state(self, apply_active_learning, prompt, answer):
        try:
            if apply_active_learning:
                logging.info(f"Applying active learning for prompt: {prompt}")
                add_sample_for_learning(prompt, answer, self.embedding_model.knowledgebase_file_path)

            if 'bye' in answer.lower() or 'bye' in prompt.lower():
                logging.info("Ending conversation")
                self.end_conv = True
        except Exception as e:
            logging.error(f"Error in Llm.actions_for_next_state: {e}")

    def get_general_answer(self, msg):
        try:
            logging.info(f"Getting general answer for message: {msg}")
            answer = self.llm.invoke(self.general_role.format(context=msg))
            self.chat_history.add_ai_response(answer)
            return answer
        except Exception as e:
            logging.error(f"Error in Llm.get_general_answer: {e}")


class llm_factory(object):
    @staticmethod
    def generate_new_attack(attack_type, profile_name):
        try:
            logging.info(f"Generating new attack: {attack_type} with profile: {profile_name}")
            llm = Llm()
            llm.initialize_new_attack(attack_type, profile_name)
            return llm
        except Exception as e:
            logging.error(f"Error in llm_factory.generate_new_attack: {e}")


llm = Llm()
