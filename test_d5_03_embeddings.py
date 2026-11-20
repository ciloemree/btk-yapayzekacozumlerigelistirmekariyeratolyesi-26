from langchain_ollama import OllamaEmbeddings

MODEL = "embeddinggemma"
BASE_URL = "http://localhost:11434"

if __name__ == "__main__":
    mesaj = input("Embedding alınacak metin: ").strip()
    if not mesaj:
        raise SystemExit("Boş metin gönderilemez.")

    emb = OllamaEmbeddings(model=MODEL, base_url=BASE_URL)
    vector = emb.embed_query(mesaj)

    print("Model:", MODEL)
    print("Base URL:", BASE_URL)
    print("Boyut:", len(vector))
    print("Vektör:")
    print(vector)
