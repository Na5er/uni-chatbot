from backend.database import db

query = "عن الجامعة"
results = db.search(query, k=5)
print(f"Results for '{query}':")
for r in results:
    print(f"  Score: {r['score']} - Source: {r['source']}")
    print(f"  Snippet: {r['content'][:100]}...")
