import os
import logging
from threading import Thread
from queue import Queue, Empty
from chat_tools.send_email import send_email

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Learner(object):
    def __init__(self):
        try:
            self.samples = Queue()
            self.samples_set = set()
            self.stop_flag = False
            self.wait_with_update = 0
            self.samples_filename = 'samples.txt'
            self.admins_mail = ['nataf12386@gmail.com', 'odedwar@gmail.com']
            self.active_learning_thread = Thread(target=self.apply_active_learning)
            self.active_learning_thread.start()
            logging.info("Learner initialized and active learning thread started.")
        except Exception as e:
            logging.error(f"Error in Learner.__init__: {e}")

    def add_sample(self, sample):
        try:
            logging.info(f"Adding sample: {sample}")
            self.samples.put(sample)
        except Exception as e:
            logging.error(f"Error in Learner.add_sample: {e}")

    def apply_active_learning(self):
        logging.info('Active learning thread running.')
        try:
            while not self.stop_flag:
                try:
                    question, answer, knowledgebase_file_path = self.samples.get(timeout=5)
                    self.samples_set.add((question, answer))
                    self.write_sample(question, answer, knowledgebase_file_path)
                    self.wait_with_update += 1
                    self.update_admin()
                except Empty:
                    continue
            logging.info('Active learning done.')
        except Exception as e:
            logging.error(f"Error in Learner.apply_active_learning: {e}")

    def stop_active_learning(self):
        try:
            self.stop_flag = True
            self.active_learning_thread.join()
            logging.info('Active learning thread stopped.')
        except Exception as e:
            logging.error(f"Error in Learner.stop_active_learning: {e}")

    def write_sample(self, question, answer, knowledgebase_file_path):
        try:
            with open(self.samples_filename, 'a') as outfile:
                outfile.write(f"'{question}'" + ';' + f"'{answer}'" + ';' + f"{knowledgebase_file_path}" + '\n')
                outfile.write('\n')
            logging.info("New line written to the samples file.")
        except IOError as e:
            logging.error(f"Error in Learner.write_sample: {e}")
        except Exception as e:
            logging.error(f"Error in Learner.write_sample: {e}")

    def update_admin(self):
        if self.wait_with_update % 3 == 0:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                update_file_path = os.path.join(script_dir, 'prompts', 'update_mail.txt')
                with open(update_file_path, 'r') as update_file:
                    update_mail = update_file.read().format(update=self.get_learning_updates_from_file())
                for mail in self.admins_mail:
                    send_email(
                        email_receiver=mail,
                        display_name="DeceptifyBot",
                        from_email="DeceptifyBot@donotreply.com",
                        email_subject="Updates from learner",
                        email_body=update_mail
                    )
                    logging.info(f"Mail sent to {mail}")
            except IOError as e:
                logging.error(f"Error in Learner.update_admin while reading update mail file: {e}")
            except Exception as e:
                logging.error(f"Error in Learner.update_admin while sending mail: {e}")

    def get_learning_updates_from_file(self):
        try:
            with open(self.samples_filename, 'r') as infile:
                updates = infile.read()
            logging.info("Learning updates retrieved from file.")
            return updates
        except IOError as e:
            logging.error(f"Error in Learner.get_learning_updates_from_file: {e}")
            return ""
        except Exception as e:
            logging.error(f"Error in Learner.get_learning_updates_from_file: {e}")
            return ""


learner = Learner()
