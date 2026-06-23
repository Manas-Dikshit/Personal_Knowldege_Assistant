from typing import List, Optional
import requests


SYSTEM_PROMPT = """
You are MRD's personal AI assistant.

You represent MRD and answer as if describing his own work, experience, projects, and technical decisions.

Guidelines:

- Be confident and concise.
- Sound like an experienced developer.
- Explain things clearly without unnecessary fluff.
- Prefer natural explanations over bullet dumping.
- Summarize retrieved information instead of copying it.
- Stay grounded in the provided context.
- If information is missing or uncertain, say so explicitly.
- Never invent projects, skills, or experiences.
- Avoid phrases like "According to the context".
- Write in first person whenever appropriate.
"""


class RAG:
    def __init__(
        self,
        retriever,
        model: str = "llama3",
        ollama_url: str = "http://localhost:11434/api/generate"
    ):
        self.retriever = retriever
        self.model = model
        self.ollama_url = ollama_url

    def retrieve_context(
        self,
        question: str,
        k: int = 5
    ) -> List[str]:
        """
        Retrieve relevant chunks.
        """

        results = self.retriever.retrieve(
            question,
            k=k
        )

        return [
            chunk.text
            for chunk in results
        ]

    def build_prompt(
        self,
        question: str,
        contexts: List[str]
    ) -> str:
        """
        Build the final prompt.
        """

        context = "\n\n".join(contexts)

        return f"""
{SYSTEM_PROMPT}

========================
RETRIEVED CONTEXT
========================

{context}

========================
USER QUESTION
========================

{question}

========================
INSTRUCTIONS
========================

Answer naturally as MRD.

Do not copy chunks verbatim.

Combine information when necessary.

If the answer is not contained in the context, clearly state that you don't have enough information.

ANSWER:
""".strip()

    def generate(
        self,
        question: str,
        k: int = 5,
        temperature: float = 0.3
    ) -> str:
        """
        Retrieve context and generate response.
        """

        contexts = self.retrieve_context(
            question,
            k=k
        )

        prompt = self.build_prompt(
            question,
            contexts
        )

        try:

            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return data.get(
                "response",
                "No response generated."
            ).strip()

        except requests.RequestException as exc:

            return (
                "Unable to generate a response "
                f"({exc})."
            )

    def ask(
        self,
        question: str,
        k: int = 5
    ) -> str:
        """
        Public interface.
        """

        return self.generate(
            question,
            k=k
        )