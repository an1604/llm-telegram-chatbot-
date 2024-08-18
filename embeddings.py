import json
import os
from functools import lru_cache
from threading import Thread

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


class embeddings(object):
    def __init__(self, knowledgebase=None):
        self.learner = []  # list of tuples for active learning

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)

        self.knowledgebase = knowledgebase if knowledgebase is not None else 'clone'  # Clone for no-purpose attack

        self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
        self.sentences_map = {}

        # Fetch the correct csv file according the knowledgebase param.
        self.knowledgebase_file_path = None
        self.faq = None

        self.active_learner_threshold = 1.19999  # Decide which threshold is valid to apply active learning.

    # @lru_cache(maxsize=128)
    def get_nearest_neighbors(self, vector, k=3):
        index = faiss.read_index(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), f'indexes/{self.knowledgebase}-faiss.index'))
        query_vector = vector.astype("float32").reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return indices, distances

    def flush(self):
        if len(self.learner) > 0:
            active_learning_thread = Thread(target=self.apply_active_learning,
                                            args=(self.knowledgebase_file_path, self.learner,))
            active_learning_thread.start()

        self.save_sentences_map()  # Saving the sentence map for feature extraction (reduce computation).
        self.sentences_map = {}

        self.knowledgebase_file_path = None
        self.json_filename_for_sentences_map = None
        self.faq = None
        self.knowledgebase = None
        self.index = faiss.IndexFlatL2(384)

        if len(self.learner) > 0:
            active_learning_thread.join()

    @staticmethod
    def apply_active_learning(knowledgebase_file_path, learner):
        new_products = []
        # Getting the Admins feedback
        for question, answer in learner:
            print(f'Question: {question} --> Answer: {answer}')
            feedback = input("Was the response helpful? (yes/no): ").strip().lower()
            if feedback == 'yes':
                new_products.append((question, answer))

        # Extending all the attractive outputs from the model to the knowledgebase.
        with open(knowledgebase_file_path, 'a') as outfile:
            for question, answer in new_products:
                outfile.write(f"'{question}'" + ';' + f"'{answer}'" + '\n')
            outfile.write('\n')

    def initialize_again(self, knowledgebase):
        self.knowledgebase = knowledgebase
        self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
        self.init_knowledgebase_path(knowledgebase)
        self.faq = self.get_faq()

    def init_knowledgebase_path(self, knowledgebase):
        dire = os.path.dirname(os.path.abspath(__file__)) + f'\\prompts\\{knowledgebase.lower()}\\'
        if knowledgebase is None:
            knowledgebase = 'knowledgebase_custom.csv'
            self.knowledgebase_file_path = os.path.join(dire, knowledgebase)
        else:
            self.knowledgebase_file_path = os.path.join(dire, f'{knowledgebase}-knowledge.csv')

    def save_sentences_map(self):
        sentences_map_json = json.dumps(self.sentences_map)
        with open(self.json_filename_for_sentences_map, 'w') as f:
            f.write(sentences_map_json)

    def generate_faq_embedding(self):
        for qa in self.faq:  # Create the embedding representation for each row in the knowledgebase.
            embedding = self.get_embedding(qa)
            self.index.add(embedding)

        indexes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indexes')
        os.makedirs(indexes_dir, exist_ok=True)
        index_path = os.path.join(indexes_dir, f'{self.knowledgebase.lower()}-faiss.index')
        faiss.write_index(self.index, index_path)

    def get_faq(self):
        df = pd.read_csv(self.knowledgebase_file_path, sep=";").dropna()
        faq = []
        for x, y in df.values:
            faq.append(x)
            self.sentences_map[x] = y
        return faq

    def get_embedding(self, _input):
        embedding = self.embedding_model.encode(_input)
        return np.array([embedding])  # Ensure it returns a 2D array

    def get_answer_from_embedding(self, _input, threshold=0.7):
        print(_input)
        prompt_embedding = self.get_embedding(_input.lower())  # Get the embedding representation for the prompt
        indices, distances = self.get_nearest_neighbors(prompt_embedding)

        closest_distance = distances[0][0]
        print(closest_distance)
        faq_index = indices[0][0]  # Taking the closest FAQ index

        if closest_distance < threshold:
            try:
                answer = self.sentences_map[self.faq[faq_index]]
            except IndexError as e:
                print(f"IndexError: {e}")
                print(f"Cannot find the value for the given key: {self.faq[faq_index]}")
                answer = "Can you repeat it?"
        else:
            answer = None

        return answer, closest_distance > self.active_learner_threshold

    def learn(self, param):
        self.learner.append(param)  # Add the new tuple to the list for future inspection.
