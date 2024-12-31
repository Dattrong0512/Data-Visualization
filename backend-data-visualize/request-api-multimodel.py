import os
from flask import Flask, request, jsonify
from pymilvus import connections, Collection
from google.genai import types
from google import genai
from dataclasses import dataclass
from dotenv import load_dotenv
import os
from flask_talisman import Talisman
from flask_cors import CORS

CERTIFICATE_DIR = os.path.join(os.path.dirname(__file__), "Certificate")
CERT_KEY = os.path.join(CERTIFICATE_DIR, "localhost.key")
CERT_CRT = os.path.join(CERTIFICATE_DIR, "localhost.crt")


@dataclass
class Config:
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    COLLECTION_NAME: str = "data_visualize"
    EMBEDDING_DIM: int = 768
    MODEL_NAME: str = "gemini-2.0-flash-exp"
    TEXT_EMBEDDING_MODEL_ID: str = "text-embedding-004"

class MilvusQueryHandler:
    def __init__(self, api_key: str):
        self.gemini_client = genai.Client(api_key=api_key)
        self.collection_name = Config.COLLECTION_NAME
        self.collection = None
        self.connect_to_milvus()

    def connect_to_milvus(self):
        try:
            connections.connect(host=Config.MILVUS_HOST, port=Config.MILVUS_PORT)
            self.collection = Collection(name=self.collection_name)
            self.collection.load()
            print("Milvus collection loaded.")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Milvus: {e}")

    def query_milvus(self, query_text: str):
        try:
            query_embedding = self.gemini_client.models.embed_content(
                model=Config.TEXT_EMBEDDING_MODEL_ID,
                contents=query_text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            ).embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Error generating query embedding: {e}")

        try:
            results = self.collection.search(
                data=[query_embedding],
                anns_field="vector",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=10,  # Giới hạn số kết quả trả về để cải thiện hiệu suất
                output_fields=["text"]
            )
        except Exception as e:
            raise RuntimeError(f"Error querying Milvus: {e}")

        if not results or len(results[0]) == 0:
            return ["No relevant documents found in the database."]

        context = []
        for idx,hit in enumerate(results[0]):
            score = hit.distance
            description = hit.entity.text
            print(f"Result {idx+1}: Score: {score}, Description: {description}")
            context_fragment = f"Document {idx + 1}:\nScore: {score:.4f}\nContent: {description[:1200]}..."
            context.append(context_fragment)

        return context

    def ask_google_gemini(self, query_text: str, context: list):
        prompt = f"Context:\n{''.join(context)}\n\nQuery: {query_text}\nAnswer:"
        try:
            response = self.gemini_client.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            return response.text if response.text else "No response from Gemini."
        except Exception as e:
            raise RuntimeError(f"Error querying Google Gemini: {e}")

# Flask App
app = Flask(__name__)
CORS(app)
# Kích hoạt Flask-Talisman
Talisman(app)
load_dotenv()

# Load API key từ .env
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("API Key not found in environment variables. Please set 'GENAI_API_KEY' in .env file.")

query_handler = MilvusQueryHandler(api_key)

@app.route('/query', methods=['GET', 'POST'])
def query():
    try:
        # Lấy query text từ request JSON
        if request.method == 'POST':
            data = request.json
        else:  # Nếu là GET
            data = request.args

        query_text = data.get("query", "").strip()

        if not query_text:
            return jsonify({"error": "Query text is required"}), 400

        # Gửi truy vấn tới Milvus
        milvus_results = query_handler.query_milvus(query_text)

        # Gửi truy vấn tới Google Gemini
        gemini_response = query_handler.ask_google_gemini(query_text, milvus_results)

        return jsonify({
            "gemini_response": gemini_response
        })

    except Exception as e:
        # Trả về lỗi chi tiết hơn để debug
        print(f"Error in /query: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context=(CERT_CRT, CERT_KEY))


