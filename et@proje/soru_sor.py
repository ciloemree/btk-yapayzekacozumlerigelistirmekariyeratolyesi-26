"""Kayıtlı Chroma veritabanından bağlam alıp Qwen ile cevaplar."""
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings

ROOT = Path(__file__).resolve().parent
DB_DIR = ROOT / "chroma_db"
OLLAMA_URL = "http://localhost:11434"

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
db = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

llm = ChatOllama(model="qwen2.5:3b", base_url=OLLAMA_URL)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sen bir şirket asistanısın. Sadece aşağıdaki bağlamı (context) kullanarak "
            "soruyu cevapla. Bağlamda yoksa 'Bu bilgi şirket belgelerinde bulunmuyor' de "
            "ve asla uydurma.\n\nBağlam:\n{context}",
        ),
        ("human", "{question}"),
    ]
)


def baglam_metni(belgeler):
    return "\n\n".join(belge.page_content for belge in belgeler)


zincir = (
    {"context": retriever | baglam_metni, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    print("Şirket asistanı. Çıkmak için q veya çıkış yaz.")
    while True:
        soru = input("\nSoru: ").strip()
        if soru.lower() in {"q", "çıkış", "cikis"}:
            break
        if not soru:
            continue
        print(zincir.invoke(soru))
