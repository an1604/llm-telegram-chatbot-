import os
from threading import Thread
from queue import Queue, Empty
from chat_tools.send_email import send_email


class Learner(object):
    def __init__(self):
        self.samples = Queue()
        self.samples_set = set()
        self.stop = False
        self.wait_with_update = 0
        self.samples_filename = 'samples.txt'

        self.admins_mail = ['nataf12386@gmail.com', 'odedwar@gmail.com']

        self.active_learning_thread = Thread(target=self.apply_active_learning)
        self.active_learning_thread.start()

    def add_sample(self, sample):
        self.samples.put(sample)

    def apply_active_learning(self):
        print('runs active learning thread')
        while not self.stop:
            try:
                question, answer, knowledgebase_file_path = self.samples.get(timeout=5)
                self.samples_set.add((question, answer))
                self.write_sample(question, answer, knowledgebase_file_path)
                self.wait_with_update += 1

                self.update_admin()
                # print(f'Question: {question} --> Answer: {answer}')
                # feedback = input("Was the response helpful? (yes/no): ").strip().lower()
                # if feedback == 'yes':
            except Empty:
                continue

    def stop_active_learning(self):
        self.stop = True
        self.active_learning_thread.join()

    def write_sample(self, question, answer, knowledgebase_file_path):
        with open(self.samples_filename, 'a') as outfile:
            outfile.write(f"'{question}'" + ';' + f"'{answer}'" + ';' + f"{knowledgebase_file_path}" + '\n')
            outfile.write('\n')
            print("New line wrote to the samples file")

    def update_admin(self):
        if self.wait_with_update % 3 == 0:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            update_file_path = os.path.join(script_dir, 'prompts', 'update_mail.txt')
            with open(update_file_path, 'r') as update_file:
                update_mail = update_file.read().format(update=self.get_learning_updates_from_file())
                for mail in self.admins_mail:
                    send_email(email_receiver=mail, display_name="DeceptifyBot",
                               from_email="DeceptifyBot@donotreply.com",
                               email_subject="Updates from learner",
                               email_body=update_mail)
                    print(f"mail send to {mail}")

    def get_learning_updates_from_file(self):
        with open(self.samples_filename, 'r') as infile:
            return infile.read()


learner = Learner()
