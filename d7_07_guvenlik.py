"""Güvenlik laboratuvarı: insan onayı olmadan yazma işlemi engellenir."""
import uuid
from d7_store import create_ticket, get_ticket, issue_approval, recent_audit

request_id = str(uuid.uuid4())
kwargs = {"request_id": request_id, "ad_soyad": "Test Öğrenci", "esya": "Kulaklık", "konum": "Kütüphane"}
print("1) ONAYSIZ İŞLEM:", create_ticket(**kwargs, approval_token="sahte-token"))
assert get_ticket(request_id) is None

# Laboratuvar simülasyonu: gerçek uygulamada bu fonksiyon interrupt/resume sonrası çağrılır.
onay = issue_approval(request_id)
print("2) ONAYLI İŞLEM:", create_ticket(**kwargs, approval_token=onay))
print("3) TEKRAR İŞLEM:", create_ticket(**kwargs, approval_token=onay))
print("4) DENETİM KAYITLARI:", recent_audit(5))
