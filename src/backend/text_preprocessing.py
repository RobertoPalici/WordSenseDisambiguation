import requests


class TextPreprocessor:

    def __init__(self, base_url: str='http://127.0.0.1:5000'):

        """
        :param base_url: the base url of the Teprolin server
        """

        self.base_url = base_url

    def tokenize(self, text: str):

        endpoint = "/process"  # endpoint for NLP tasks
        data = {
            "text": text,  #  input text to be tokenized
            "exec": "tokenization"  # NLP task
        }

        response = requests.post(f"{self.base_url}{endpoint}", data=data)

        # print(f"Response Status Code: {response.status_code}")
        # print(f"Response Content: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Response: {data}")
                tokens = []

                # tokens are dictionaries
                tokenized_data = data.get("teprolin-result", {}).get("tokenized", [])
                for sentence in tokenized_data:
                    for token_info in sentence:
                        word = token_info.get("_wordform", "")
                        if word:
                            tokens.append(word)

                return tokens
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def pos_tagging(self, tokens: list):
        """
        :param tokens: List of tokens (pre-tokenized words)
        :return: List of tuples (word, pos_tag)
        """

        text = " ".join(tokens)  # the input for Teprolin is a string

        endpoint = "/process"
        data = {
            "text": text,
            "exec": "pos-tagging"
        }

        response = requests.post(f"{self.base_url}{endpoint}", data=data)

        # print(f"Response Status Code: {response.status_code}")
        # print(f"Response Content: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                pos_tags = data.get("teprolin-result", {}).get("tokenized", [])
                if pos_tags:
                    # Flattening and extracting word and POS
                    pos_tags = [(word["_wordform"], word["_ctg"]) for sentence in pos_tags for word in sentence]
                return pos_tags
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def ner(self, tokens: list):
        """
        Perform Named Entity Recognition (NER) on a list of tokens using the Teprolin web service
        :param tokens: List of tokens (pre-tokenized and POS-tagged words)
        :return: List of tuples (word, named_entity)
        """
        text = " ".join(tokens)

        endpoint = "/process"
        data = {
            "text": text,
            "exec": "named-entity-recognition"
        }

        response = requests.post(f"{self.base_url}{endpoint}", data=data)

        # print(f"Response Status Code: {response.status_code}")
        # print(f"Response Content: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                ner_result = data.get("teprolin-result", {}).get("tokenized", [])
                if ner_result:
                    ner_result = [(word["_wordform"], word["_ner"]) for sentence in ner_result for word in sentence]
                return ner_result
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def dependency_parsing(self, text: str):
        endpoint = "/process"
        data = {
            "text": text,  # input text
            "exec": "dependency-parsing",  # NLP task
            "model": "udpipe-ufal"
        }

        response = requests.post(f"{self.base_url}{endpoint}", data=data)

        if response.status_code == 200:
            try:
                data = response.json()
                # print(f"JSON Response: {data}")

                dependencies = []

                # extract dependency information from tokenized data
                tokenized_data = data.get("teprolin-result", {}).get("tokenized", [])
                for sentence in tokenized_data:
                    for token_info in sentence:
                        word = token_info.get("_wordform", "")
                        dependency_relation = token_info.get("_deprel", "")
                        head = token_info.get("_head", "")

                        if word:
                            dependencies.append((word, dependency_relation, head))

                return dependencies

            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return []
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []



if __name__ == '__main__':

    preprocessor = TextPreprocessor()
    input_text = "Ion și Maria merg la Calarasi."

    """
    received_tokens = preprocessor.tokenize(input_text)
    
    print(f"Received_tokens:\n{received_tokens}")
    pos_tags = preprocessor.pos_tagging(received_tokens)
    print(f"POS Tags:\n{pos_tags}")

    ner_results = preprocessor.ner(received_tokens)
    print(f"Ner Results:\n{ner_results}")
    """
    print(preprocessor.dependency_parsing(input_text))
