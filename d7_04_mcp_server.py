"""MCP Server: belge arama, onaylı talep oluşturma ve durum sorgulama."""
import json
from mcp.server.fastmcp import FastMCP
from d7_store import create_ticket, get_ticket, init_db

mcp = FastMCP("KampusDestek")

@mcp.tool()
def dokuman_ara(soru: str, k: int = 3) -> str:
    """Kampüs dokümanlarında arama yapar ve kaynak bilgisi döndürür."""
    try:
        from d5_05_search import search
        docs = search(soru, k=max(1, min(k, 5)))
        return json.dumps({"ok": True, "kaynaklar": [
            {"source": d.metadata.get("source", "bilinmiyor"),
             "chunk_id": d.metadata.get("chunk_id", ""),
             "metin": d.page_content[:750]} for d in docs]}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

@mcp.tool()
def talep_olustur(request_id: str, ad_soyad: str, esya: str, konum: str, approval_token: str) -> str:
    """Yalnızca geçerli, tek kullanımlık insan onayıyla kayıp eşya talebi açar."""
    return json.dumps(create_ticket(request_id, ad_soyad, esya, konum, approval_token), ensure_ascii=False)

@mcp.tool()
def talep_durumu(request_id: str) -> str:
    """Daha önce oluşturulmuş talebin durumunu sorgular."""
    return json.dumps({"ok": True, "ticket": get_ticket(request_id)}, ensure_ascii=False)

if __name__ == "__main__":
    init_db()
    mcp.run(transport="stdio")  # stdout'a print yazma: MCP iletişimi bozulur.
