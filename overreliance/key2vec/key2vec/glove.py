import numpy as np
from typing import Dict

class Glove(object):
    """GloVe vectors.

    Parameters
    ----------
    path : str, required
        Path to the GloVe embeddings

    Attributes
    ----------
    embeddings : Dict[str, np.float64]
        Dictionary of GloVe embeddings
    dim : int
        Dimension of GloVe embeddings
    """

    def __init__(self,text=None, spacy_nlp = None, path = None) -> None:
        self.spacy_nlp = spacy_nlp
        self.embeddings = None
        self.dim = None
        
        if spacy_nlp and text: 
            self.embeddings = self.__make_glove(text)
            self.spacy_nlp = spacy_nlp
            self.dim = self.__get_dim()
            
        if path:
            self.embeddings = self.__read_glove(path)
            self.dim = self.__get_dim()

        
        
    def __read_glove(self,path) -> Dict[str, np.float64]:
        """Reads GloVe vectors into a dictionary, where
           the words are the keys, and the vectors are the values.
           
           self.path should be set to the location of glove.6B.xd.txt, if you have it.
           Otherwise, use __set_embeddings using the nlp object from spacy.load

        Returns
        -------
        word_vectors : Dict[str, np.float64]
        """
        with open(path, 'r') as f:
            data = f.readlines()
        word_vectors = {}
        for row in data:
            stripped_row = row.strip('\n')
            split_row = stripped_row.split(' ')
            word = split_row[0]
            vector = []
            for el in split_row[1:]:
                vector.append(float(el))
            word_vectors[word] = np.array(vector)
        return word_vectors
    
    def __make_glove(self,text) -> Dict[str,np.float64]:
        """Reads spacy generated nlp object, then creates a word dictionary.
        

        Returns:
            word_vectors : Dict[str,np.float64]
        """
        doc = self.spacy_nlp(text)
        word_dict = dict()
        for token in doc:
            word_dict[token.text] = token.vector
        return word_dict

    def __get_dim(self) -> int:
        return len(self.embeddings[list(self.embeddings.keys())[0]])