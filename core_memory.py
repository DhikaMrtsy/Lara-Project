import chromadb
from sentence_transformers import SentenceTransformer
import uuid

class MemoriLara:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./db_lara") # Folder penyimpanan DB // DB's folder
        self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2') # SentenceTransformer's simple model (IND/ENG)
        self.collection = self.client.get_or_create_collection(name="ingatan_utama")

    def simpan_ingatan(self, teks, kategori="umum"):
        """ Saving chat to DB """
        try: 
            vector = self.model.encode(teks).tolist()
            self.collection.add(
                documents=[teks],
                embeddings=[vector],
                metadatas=[{"kategori": kategori}],
                ids=[str(uuid.uuid4())] # Pake UUID biar ID-nya gak bakal bentrok
        )
        except Exception as e:
            print(f"❌ Lara gagal menyimpan ingatan: {e}")

    def cari_ingatan(self, query, limit=3):
        """ Finding memories in DB """
        query_vector = self.model.encode(query).tolist()
        hasil = self.collection.query(
            query_embeddings=[query_vector],
            n_results=limit
        )
        if hasil['documents'] and hasil['documents'][0]: # Gabungkan hasil jadi satu paragraf untuk 'intruksi' ke Lara
            return "\n".join(hasil['documents'][0])
        return ""