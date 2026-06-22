import requests


class RAG:
    def __init__(self, retriever):
        self.retriever = retriever

    def build_prompt(self, question, contexts):
        context_text = "\n\n".join(contexts)

        prompt = f"""
You are MRD's personal AI assistant.

You must answer EXACTLY like MRD would:
- confident
- slightly technical
- clean and structured
- no unnecessary fluff
- practical and developer-focused
- if unsure, say it clearly

Use the context below to answer.

---

CONTEXT:
{context_text}

---

QUESTION:
{question}

---

RESPONSE STYLE (IMPORTANT):
- Think like MRD explaining his own work
- Keep answers direct and intelligent
- Avoid listing raw text
- Summarize and interpret information
- Sound like a real developer speaking about his experience

ANSWER:
"""
        return prompt

    def generate(self, question):
        contexts = self.retriever.search(question)

        prompt = self.build_prompt(question, contexts)

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]