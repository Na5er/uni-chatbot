from backend.database import db

query = "هذه رسالة ليس لها أي علاقة بمحتوى الجامعة العشوائية"
results = db.search(query, k=5)
print(f"Results for '{query}':")
for r in results:
    print(f"  Score: {r['score']} - Source: {r['source']}")

query = "بطيخ بطاطس طماطم خيار تفاح برتقال موز عنب"
results = db.search(query, k=5)
print(f"\nResults for '{query}':")
for r in results:
    print(f"  Score: {r['score']} - Source: {r['source']}")
