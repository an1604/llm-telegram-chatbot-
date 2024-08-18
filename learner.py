from threading import Thread
from queue import Queue, Empty


class Learner(object):
    def __init__(self):
        self.samples = Queue()
        self.samples_set = set()
        self.stop = False
        self.samples_filename = 'samples.txt'

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


learner = Learner()
