from dataclasses import dataclass

from llm import llm_factory


@dataclass
class Attack:
    def __init__(self, attack_type, profile_name):
        self.attack_type = attack_type
        self.profile_name = profile_name
        self.llm = llm_factory.generate_new_attack(attack_type, profile_name)


@dataclass
class User:
    def __init__(self, user_id, user_name):
        self.current_answer = None
        self.llm = None
        self.attack = None
        self.attack_type = None
        self.user_id = user_id
        self.user_name = user_name
        self.is_in_attack = False
        self.transcript = None

        self.tries_counter = 0  # This counter is for handling attack initialization problems in the chat itself.
        # It keeps track the tries of the user to generate new attack without any success
        # if some error occurs on the server side and session restart needed.

    def is_restart_session(self):
        self.tries_counter += 1

        if self.tries_counter >= 3:
            self.tries_counter = 0
            self.end_attack()
            return True

        return False

    def start_new_attack(self, attack_type):
        self.is_in_attack = True
        self.transcript = None
        self.attack_type = attack_type
        self.attack = Attack(attack_type=attack_type, profile_name=self.user_name)
        self.llm = llm_factory.generate_new_attack(attack_type, self.user_name)
        self.current_answer = self.llm.get_init_msg()

    def end_attack(self):
        self.transcript = self.llm.get_transcript()
        self.is_in_attack = False
        self.attack = None
        self.llm = None
        self.attack_type = None

    def get_answer_from_llm(self, prompt):
        answer = self.llm.get_answer(prompt)
        self.current_answer = answer
        return answer
