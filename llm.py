from src.retrieve import Retriever
from src.rag import RAG


class MRDAI:

    def __init__(self):
        self.retriever = Retriever(dim=384)
        self.rag = RAG(self.retriever)

    def ask(self, question):
        return self.rag.generate(question)


mrd_ai = MRDAI()