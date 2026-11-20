
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "sirket_belgesi.pdf"
DB_DIR = ROOT / "chroma_db"

MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434"


def pdf_yukle(yol: Path):
    if not yol.is_file():
        raise SystemExit(
            f"PDF yok: {yol}\n"
            "sirket_belgesi.pdf dosyasını bu klasöre koy, sonra scripti tekrar çalıştır."
        )
    return PyPDFLoader(str(yol)).load()


def parcala(sayfalar):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    return splitter.split_documents(sayfalar)


def veritabani_yaz(parcalar):
    embeddings = OllamaEmbeddings(model=MODEL, base_url=OLLAMA_URL)
    return Chroma.from_documents(
        documents=parcalar,
        embedding=embeddings,
        persist_directory=str(DB_DIR),
    )


if __name__ == "__main__":
    sayfalar = pdf_yukle(PDF_PATH)
    print(f"Sayfa sayısı: {len(sayfalar)}")

    parcalar = parcala(sayfalar)
    print(f"Parça sayısı: {len(parcalar)}")

    # EKRANDA GÖSTERME DÖNGÜSÜ:
    print("\n--- KESİLEN PARÇALARIN İÇERİĞİ ---")
    for i, parca in enumerate(parcalar):
        print(f"\n[PARÇA {i+1}] (Karakter: {len(parca.page_content)}):")
        print(parca.page_content)
        print("-" * 40)

    db = veritabani_yaz(parcalar)
    print("\nKayıt:", db._collection.count())
    print("Veritabanı:", DB_DIR)
