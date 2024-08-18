from threading import Thread
from queue import Queue, Empty


class Learner(object):
    def __init__(self):
        self.samples = Queue()
        self.stop = False
        self.active_learning_thread = Thread(target=self.apply_active_learning)
        self.active_learning_thread.start()

    def add_sample(self, sample):
        self.samples.put(sample)

    def apply_active_learning(self):
        while not self.stop:
            try:
                question, answer, knowledgebase_file_path = self.samples.get(timeout=1)
                print(f'Question: {question} --> Answer: {answer}')
                feedback = input("Was the response helpful? (yes/no): ").strip().lower()
                if feedback == 'yes':
                    with open(knowledgebase_file_path, 'a') as outfile:
                        outfile.write(f"'{question}'" + ';' + f"'{answer}'" + '\n')
                        outfile.write('\n')
            except Empty:
                continue

    def stop_active_learning(self):
        self.stop = True
        self.active_learning_thread.join()


learner = Learner()
