# BTK Akademi — 7. ve 8. Gün Uygulama Paketi

**Senaryo:** Akıllı Kampüs Destek Masası. 5–6. gün RAG altyapısı üzerine LangGraph + MCP + FastAPI + n8n.

## Ön koşullar

- Python 3.11/3.12, VS Code, Ollama, `ollama pull qwen2.5:3b`, `ollama pull embeddinggemma`.
- Önceki günlerin **aynı proje kökünde** `config.py`, `d5_03_embeddings.py`, `d5_05_search.py` ve dolu `chroma_kampus/` klasörü olmalı.
- `kodlar/` içindeki `d7_*.py` ve `d8_*.py` dosyalarını bu proje köküne kopyalayın. Var olan `d5_...` ve `d6_...` dosyalarını değiştirmeyin.
- Bu paket, önceki günün Chroma koleksiyonunu yeniden oluşturmaz.

## Kurulum

```bash
python -m pip install -r requirements_gun7_8.txt
ollama list
```

## Gün 7 — çalıştırma sırası

```bash
python d7_01_langgraph.py
python d7_02_routing.py
python d7_03_tool_calling.py
python d7_05_mcp_client.py
python d7_06_agent.py
python d7_07_guvenlik.py
```

`d7_04_mcp_server.py` doğrudan terminalde başlatılıp okunacak bir uygulama değildir; MCP istemcisi tarafından stdio üzerinden açılır. Sunucu kodunda stdout'a `print` eklemeyin.

`d7_03_tool_calling.py` Ollama modelinin araç çağırmasını gösterir; küçük modeller her zaman doğru araç seçmeyebilir. `AGENT_MODEL=qwen2.5:3b` veya daha güçlü tool-calling destekli model kullanın.

## Gün 8 — FastAPI

```bash
python -m uvicorn d8_01_api:app --host 0.0.0.0 --port 8000
```

Başka terminalde:

```bash
python d8_02_istemci.py
```

Swagger: `http://127.0.0.1:8000/docs`.

## Gün 8 — n8n

Docker Desktop (Windows/macOS) ile:

```bash
docker volume create n8n_data
docker run -d --name n8n -p 5678:5678 -e TZ=Europe/Istanbul -e GENERIC_TIMEZONE=Europe/Istanbul -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

`http://localhost:5678` adresinde n8n'i açın. `n8n/` içindeki iki JSON workflow dosyasını içe aktarın. n8n Docker konteynerinden bilgisayardaki FastAPI'ye `http://host.docker.internal:8000` adresiyle erişin. Bu adres Docker Desktop için geçerlidir; Linux'ta ek host-gateway ayarı gerekebilir.

- `campus_ask`: `POST /webhook/campus-ask`, JSON gövdesi: `{"question":"Kulaklığımı kaybettim, başvuru oluştur.","ad_soyad":"Örnek Öğrenci","esya":"Kulaklık","konum":"Kütüphane"}`.
- Yanıt `approval_required` ve `thread_id` içerirse **insan onayı gerekir**. Otomatik onay vermeyin.
- `campus_approve`: `POST /webhook/campus-approve`, JSON gövdesi: `{"thread_id":"...","approved":true}`. Bu yalnızca eğitmen laboratuvarı içindir; gerçek sistemde kimlik doğrulama/rol kontrolü gerekir.
- Webhook test modunda `/webhook-test/...`, workflow aktifken `/webhook/...` yolunu kullanın.

## Hata simülasyonu

`DEMO_FAIL_ONCE=1` ile başlatılan Agent, ilk **okuma** denemesinde kasıtlı hata üretir, sonra tekrar dener. Bu seçenek yazma işlemlerine uygulanmaz. `LAB_MODE=1` ile API başlatıldığında `GET /demo/error` 503 üretir. `/audit` ile logları inceleyin.

## Güvenlik ve sınırlamalar

- `issue_approval()` yalnızca LangGraph `interrupt()` sonrası güvenilir kod tarafından çağrılır. MCP sunucusu onay token'ını doğrular. Model token'ı görmez.
- Talep kayıtlarında `request_id` benzersizdir; aynı talebin iki kez kaydedilmesi engellenir.
- Bu **yerel laboratuvar** örneğinde API/webhook kimlik doğrulaması, kullanıcı bazlı yetkilendirme ve HTTPS yoktur. İnternete açmayın, gerçek öğrenci kişisel verisi kullanmayın.
- Ollama/MCP/LangGraph entegrasyonunu bu oluşturma ortamında canlı çalıştırmak mümkün olmadığından, **çalıştırmadan önce öğrenci bilgisayarında uçtan uca test edin**. Python sözdizimi ve SQLite onay/idempotency testleri ayrı doğrulanmıştır.
