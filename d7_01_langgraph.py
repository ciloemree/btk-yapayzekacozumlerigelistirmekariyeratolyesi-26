"""İlk LangGraph: bir talebin adım adım işlenmesi."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    soru: str
    kategori: str
    cevap: str

def siniflandir(state: State):
    soru = state["soru"].lower()
    return {"kategori": "kayip_esya" if "kayb" in soru or "kulaklık" in soru else "genel"}

def yanitla(state: State):
    return {"cevap": f"İşlenecek kategori: {state['kategori']}"}

builder = StateGraph(State)
builder.add_node("siniflandir", siniflandir)
builder.add_node("yanitla", yanitla)
builder.add_edge(START, "siniflandir")
builder.add_edge("siniflandir", "yanitla")
builder.add_edge("yanitla", END)
app = builder.compile()

if __name__ == "__main__":
    print(app.invoke({"soru": "Kulaklığımı kaybettim", "kategori": "", "cevap": ""}))
