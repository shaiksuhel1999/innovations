from rag_system import TraumaKnotRAG
import os

rag = TraumaKnotRAG()
unsafe = 'conversations/2026-06-21T13:57:27.205140.json'
print('Attempting to save to unsafe path:', unsafe)
path = rag.save_conversation(unsafe)
print('Saved to:', path)
print('Exists:', os.path.exists(path))
print('Contents size (bytes):', os.path.getsize(path))
with open(path, 'r', encoding='utf-8') as f:
    data = f.read()
print('First 200 chars:', data[:200])

