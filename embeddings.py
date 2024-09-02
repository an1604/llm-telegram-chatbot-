import json
import os
import logging
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class embeddings(object):
    def __init__(self, knowledgebase=None):
        try:
            logging.info("Initializing embeddings...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = faiss.IndexFlatL2(384)

            self.knowledgebase = knowledgebase if knowledgebase is not None else 'clone'
            self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
            self.sentences_map = {}

            self.knowledgebase_file_path = None
            self.faq = None

            self.stop = False
            self.active_learner_threshold = 1.39999

            logging.info("Embeddings initialized")
        except Exception as e:
            logging.error(f"Error in embeddings.__init__: {e}")

    def get_nearest_neighbors(self, vector, k=3):
        try:
            index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      f'indexes/{self.knowledgebase}-faiss.index')
            logging.info(f"Loading FAISS index from: {index_path}")
            index = faiss.read_index(index_path)
            if isinstance(vector, tuple):
                vector = np.array(vector)
            query_vector = vector.astype("float32").reshape(1, -1)
            distances, indices = index.search(query_vector, k)
            logging.info(f"Nearest neighbors found: indices={indices}, distances={distances}")
            return indices, distances
        except Exception as e:
            logging.error(f"Error in embeddings.get_nearest_neighbors: {e}")

    def flush(self):
        try:
            logging.info("Flushing embeddings...")
            self.sentences_map = {}
            self.knowledgebase_file_path = None
            self.json_filename_for_sentences_map = None
            self.faq = None
            self.knowledgebase = None
            self.index = faiss.IndexFlatL2(384)
        except Exception as e:
            logging.error(f"Error in embeddings.flush: {e}")

    def initialize_again(self, knowledgebase):
        try:
            logging.info(f"Re-initializing with knowledgebase: {knowledgebase}")
            self.knowledgebase = knowledgebase
            self.json_filename_for_sentences_map = f'{self.knowledgebase}.json'
            self.init_knowledgebase_path(knowledgebase)
            self.faq = self.get_faq()
        except Exception as e:
            logging.error(f"Error in embeddings.initialize_again: {e}")

    def init_knowledgebase_path(self, knowledgebase):
        try:
            dire = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts', knowledgebase.lower())
            if knowledgebase is None:
                knowledgebase = 'knowledgebase_custom.csv'
            self.knowledgebase_file_path = os.path.join(dire, f'{knowledgebase}-knowledge.csv')

            if not os.path.exists(dire):
                os.makedirs(dire)
                logging.info(f"Created directory: {dire}")

            if not os.path.exists(self.knowledgebase_file_path):
                logging.error(f"The knowledge base file {self.knowledgebase_file_path} does not exist.")
                raise FileNotFoundError(f"The knowledge base file {self.knowledgebase_file_path} does not exist.")
        except Exception as e:
            logging.error(f"Error in embeddings.init_knowledgebase_path: {e}")

    def save_sentences_map(self):
        try:
            logging.info(f"Saving sentences map to {self.json_filename_for_sentences_map}")
            sentences_map_json = json.dumps(self.sentences_map)
            with open(self.json_filename_for_sentences_map, 'w') as f:
                f.write(sentences_map_json)
        except Exception as e:
            logging.error(f"Error in embeddings.save_sentences_map: {e}")

    def generate_faq_embedding(self):
        try:
            logging.info("Generating FAQ embeddings...")
            for qa in self.faq:
                embedding = self.get_embedding(qa)
                self.index.add(embedding)

            indexes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indexes')
            os.makedirs(indexes_dir, exist_ok=True)
            index_path = os.path.join(indexes_dir, f'{self.knowledgebase.lower()}-faiss.index')
            faiss.write_index(self.index, index_path)
            logging.info(f"FAISS index saved to: {index_path}")
        except Exception as e:
            logging.error(f"Error in embeddings.generate_faq_embedding: {e}")

    def get_faq(self):
        try:
            logging.info(f"Loading FAQ from: {self.knowledgebase_file_path}")
            df = pd.read_csv(self.knowledgebase_file_path, sep=";").dropna()
            faq = []
            for x, y in df.values:
                faq.append(x)
                self.sentences_map[x] = y
            logging.info("FAQ loaded and sentences map created")
            return faq
        except Exception as e:
            logging.error(f"Error in embeddings.get_faq: {e}")

    def get_embedding(self, _input):
        try:
            embedding = self.embedding_model.encode(_input)
            return tuple(embedding)
        except Exception as e:
            logging.error(f"Error in embeddings.get_embedding: {e}")

    def get_answer_from_embedding(self, _input, threshold=0.7):
        try:
            logging.info(f"Getting answer for input: {_input}")
            prompt_embedding = self.get_embedding(_input.lower())
            if isinstance(prompt_embedding, tuple):
                prompt_embedding = np.array(prompt_embedding).reshape(1, -1).astype("float32")

            indices, distances = self.get_nearest_neighbors(prompt_embedding)

            closest_distance = distances[0][0]
            faq_index = indices[0][0]

            if closest_distance < threshold:
                try:
                    answer = self.sentences_map[self.faq[faq_index]]
                except IndexError as e:
                    logging.error(f"IndexError in embeddings.get_answer_from_embedding: {e}")
                    logging.error(f"Cannot find the value for the given key: {self.faq[faq_index]}")
                    answer = "Can you repeat it?"
            else:
                answer = None

            logging.info(f"Answer: {answer}, Distance: {closest_distance}")
            return answer, closest_distance > self.active_learner_threshold
        except Exception as e:
            logging.error(f"Error in embeddings.get_answer_from_embedding: {e}")
