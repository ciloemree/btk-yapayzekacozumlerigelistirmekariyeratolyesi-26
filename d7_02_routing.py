"""Conditional routing: bilgi sorusu ile işlem talebini ayır."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    soru: str
    istek_tipi: str
    sonuc: str
    plan: list[str]

def planla(state: State):
    metin = state["soru"].lower()
    islem = any(k in metin for k in ("oluştur", "kaydet", "talep aç", "başvuru yap"))
    tip = "islem" if islem else "bilgi"
    plan = ["dokuman_ara", "insan_onayi", "talep_kaydet"] if islem else ["dokuman_ara", "yanitla"]
    return {"istek_tipi": tip, "plan": plan}

def yonlendir(state: State):
    return state["istek_tipi"]

def bilgi(state: State):
    return {"sonuc": "Bilgi araması yapılacak."}

def islem(state: State):
    return {"sonuc": "Bilgi aranacak, ardından onay istenecek."}

builder = StateGraph(State)
for ad, fn in (("planla", planla), ("bilgi", bilgi), ("islem", islem)):
    builder.add_node(ad, fn)
builder.add_edge(START, "planla")
builder.add_conditional_edges("planla", yonlendir, {"bilgi": "bilgi", "islem": "islem"})
builder.add_edge("bilgi", END)
builder.add_edge("islem", END)
app = builder.compile()

if __name__ == "__main__":
    for soru in ("Kayıp eşya nereye teslim edilir?", "Kulaklığım için başvuru oluştur"):
        print(app.invoke({"soru": soru, "istek_tipi": "", "sonuc": "", "plan": []}))
