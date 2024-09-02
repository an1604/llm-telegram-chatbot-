import os
import logging
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_text_from_file(path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(script_dir, path)
    logging.info(f"Getting text from file: {path_to_file}")
    try:
        with open(path_to_file, "r") as f:
            content = f.read()
        logging.info("File read successfully")
        return content
    except Exception as e:
        logging.error(f"Error in get_text_from_file while reading file {path_to_file}: {e}")
        return None


class Prompts(object):
    ROLE = None
    PRINCIPLES = "Principles for {target}"  # Placeholder for actual principles

    @staticmethod
    def set_role(attack_purpose):
        logging.info(f"Setting role for attack purpose: {attack_purpose}")
        try:
            if 'chat' in attack_purpose.lower():
                Prompts.ROLE = Prompts.get_role()
                logging.info("Role set to chat role")
            else:
                role_template_path = f'{attack_purpose.lower()}/{attack_purpose}Role.txt'
                logging.info(f"Loading role from template: {role_template_path}")
                Prompts.ROLE = PromptTemplate.from_template(get_text_from_file(role_template_path))
                if Prompts.ROLE is None:
                    logging.error(f"Error in set_role: Failed to set role from template: {role_template_path}")
        except Exception as e:
            logging.error(f"Error in set_role for attack_purpose {attack_purpose}: {e}")

    @staticmethod
    def get_principles(target='address'):
        logging.info(f"Getting principles for target: {target}")
        try:
            principles = Prompts.PRINCIPLES.format(target=target)
            logging.info(f"Principles: {principles}")
            return principles
        except Exception as e:
            logging.error(f"Error in get_principles while formatting principles for target {target}: {e}")
            return None

    @staticmethod
    def get_role():
        logging.info("Getting role from role.txt")
        try:
            role = get_text_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'role.txt'))
            logging.info(f"Role retrieved: {role}")
            return role
        except Exception as e:
            logging.error(f"Error in get_role while retrieving role from file: {e}")
            return None
