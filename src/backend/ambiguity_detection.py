import rowordnet as rwn
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from text_preprocessing import TextPreprocessor  # Import TextPreprocessor


class AmbiguityDetector:
    def __init__(self, base_url="http://127.0.0.1:5000", bert_model="dumitrescustefan/bert-base-romanian-uncased-v1"):
        self.text_preprocessor = TextPreprocessor(base_url)
        self.wn = rwn.RoWordNet()
        self.tokenizer = AutoTokenizer.from_pretrained(bert_model)
        self.model = AutoModel.from_pretrained(bert_model)

    def get_bert_embedding(self, word):

        inputs = self.tokenizer(word, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embedding.numpy()

    def find_ambiguous_words(self, text):
        tokens = self.text_preprocessor.tokenize(text)
        ambiguous_words = []

        for word in tokens:
            synset_ids = self.wn.synsets(literal=word)  # synsets for the word

            if len(synset_ids) > 1:  # word with multiple meanings in RWN
                syn_sets = [self.wn.synset(synset_id) for synset_id in synset_ids]

                # embeddings for all synsets' definitions
                sense_embeddings = [self.get_bert_embedding(synset.definition) for synset in syn_sets]

                # average embedding across all senses
                avg_sense_embedding = np.mean(sense_embeddings, axis=0)  # Average across all senses

                # embedding for the word in context
                word_embedding = self.get_bert_embedding(word)

                # Compare the word's embedding with its meanings
                similarity = cosine_similarity([word_embedding], [avg_sense_embedding])[0][0]

                if similarity < 0.8:  # If too different from all meanings
                    ambiguous_words.append(word)

        return ambiguous_words

if __name__ == '__main__':

    detector = AmbiguityDetector()
    text = "Ion și Maria merg la Călărași."
    ambiguous_words = detector.find_ambiguous_words(text)
    print(f"Ambiguous words: {ambiguous_words}")
