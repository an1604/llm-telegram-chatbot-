import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate


def get_text_from_file(path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(script_dir, path)
    print(path_to_file)
    with open(path_to_file, "r") as f:
        return f.read()


class Prompts(object):
    ROLE = None

    # PRINCIPLES = get_text_from_file('Server/LLM/prompts/remember.txt')
    # KNOWLEDGEBASE_ROLE = SystemMessage(content=get_text_from_file('knowledge.txt'))

    @staticmethod
    def set_role(attack_purpose):
        Prompts.ROLE = PromptTemplate.from_template(
            get_text_from_file(f'{attack_purpose.lower()}/{attack_purpose}Role.txt'))

    @staticmethod
    def get_principles(target='address'):
        return Prompts.PRINCIPLES.format(target=target)

    @staticmethod
    def get_role():
        try:
            return get_text_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'role.txt'))
        except Exception as e:
            print(e)
            return None
