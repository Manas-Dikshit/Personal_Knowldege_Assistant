from typing import List

import requests

from src.config import LLM_MODEL, OLLAMA_URL


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
        model: str = LLM_MODEL,
        ollama_url: str = OLLAMA_URL
    ):
        if retriever is None:
            raise ValueError("RAG requires a retriever.")

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

        context = (
            "\n\n".join(contexts)
            if contexts
            else "(No relevant information was retrieved.)"
        )

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

        if not question or not question.strip():
            return "Please provide a question."

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

        except requests.ConnectionError:
            return (
                "Unable to reach Ollama. Is it running? "
                "Start it with 'ollama serve' and pull the model with "
                f"'ollama pull {self.model}'."
            )

        except requests.RequestException as exc:
            return f"Unable to generate a response ({exc})."

        except ValueError:
            # response.json() failed to decode
            return "Ollama returned an invalid response."

        answer = data.get("response", "").strip()

        if not answer:
            return "No response generated."

        return answer

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

    def ask_detailed(
        self,
        question: str,
        k: int = 5,
        temperature: float = 0.3
    ) -> dict:
        """
        Answer plus retrieval provenance for UI source attribution.
        """

        chunks = self.retriever.retrieve(
            question,
            k=k
        )

        sources = []
        seen = set()

        for chunk in chunks:
            md = chunk.metadata

            key = (
                md.get("source"),
                md.get("repo") or md.get("file") or "",
                md.get("section") or ""
            )

            if key in seen:
                continue
            seen.add(key)

            label = key[1] or md.get("path", "")
            if key[2]:
                label += f" — {key[2]}"

            sources.append(
                {
                    "source": md.get("source", ""),
                    "label": label,
                    "score": round(chunk.score, 3)
                }
            )

        answer = self.generate(
            question,
            k=k,
            temperature=temperature
        )

        return {"answer": answer, "sources": sources}
