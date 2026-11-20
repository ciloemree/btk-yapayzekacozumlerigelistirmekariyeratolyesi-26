"""Ollama ile salt-okunur tool calling; modelin araç seçmesi garanti değildir."""
import os
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from d5_05_search import search

@tool
def kampus_belgesi_ara(soru: str) -> str:
    """Kampüs kuralları, kayıp eşya ve kütüphane belgelerinde arama yapar."""
    docs = search(soru, k=3)
    return "\n".join(f"[{d.metadata.get('source', 'bilinmiyor')}] {d.page_content[:350]}" for d in docs)

if __name__ == "__main__":
    llm = ChatOllama(model=os.getenv("AGENT_MODEL", "qwen2.5:3b"),
                     base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), temperature=0)
    model = llm.bind_tools([kampus_belgesi_ara])
    cevap = model.invoke([HumanMessage(content="Kayıp eşya başvuru noktasını kampüs belgelerinde araştır.")])
    print("Modelin araç çağrısı:", cevap.tool_calls)
    for c in cevap.tool_calls:
        if c["name"] == "kampus_belgesi_ara":
            print("Araç sonucu:", kampus_belgesi_ara.invoke(c["args"]))
    if not cevap.tool_calls:
        print("Model araç seçmedi. Daha güçlü bir tool-calling modeli deneyin.")
