import faiss

import numpy as np

class RetrievalEngine:

    def __init__(self,dimension):

        self.index=faiss.IndexFlatIP(dimension)

    def build(self,vectors):

        self.index.add(

            np.asarray(vectors,dtype=np.float32)

        )

    def search(self,query_vector,k=1000):

        scores,idx=self.index.search(

            np.asarray([query_vector],dtype=np.float32),

            k

        )

        return scores[0],idx[0]