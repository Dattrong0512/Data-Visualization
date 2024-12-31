import streamlit as st
from pymilvus import connections, Collection
from google.genai import types
from google import genai
from dataclasses import dataclass
from dotenv import load_dotenv
import os


@dataclass
class Config:
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    COLLECTION_NAME: str = "chantroisangtao"
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
        connections.connect(host=Config.MILVUS_HOST, port=Config.MILVUS_PORT)
        self.collection = Collection(name=self.collection_name)
        self.collection.load()
        print("Milvus collection loaded.")

    def query_milvus(self, query_text: str):
        # Tạo vector embedding từ truy vấn
        try:
            query_embedding = self.gemini_client.models.embed_content(
                model=Config.TEXT_EMBEDDING_MODEL_ID,
                contents=query_text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            ).embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Error generating query embedding: {e}")

        # Tìm kiếm trong Milvus
        try:
            results = self.collection.search(
                data=[query_embedding],
                anns_field="vector",
                param={"metric_type": "L2","offset": 0,"ignore_growing":
                             False, "params": {"nprobe": 10}},
                limit=100,  # Số lượng kết quả trả về
                output_fields=["text"]
            )
        except Exception as e:
            raise RuntimeError(f"Error querying Milvus: {e}")

        # Lấy các tài liệu liên quan
        if not results or len(results[0]) == 0:
            return "No relevant documents found in the database."

        context = []
            # Process results
        for idx,hit in enumerate(results[0]):
            score = hit.distance
            description = hit.entity.text
            print(f"Result {idx+1}: Score: {score}, Description: {description}")
            context_fragment = f"Document {idx + 1}:\nScore: {score:.4f}\nContent: {description[:1200]}..."
            context.append(context_fragment)

        return context

    def ask_google_gemini(self, query_text: str, context: list):
        # Xây dựng prompt cho Google Gemini
        prompt = f"Context:\n{''.join(context)}\n\nQuery: {query_text}\nAnswer:"

        try:
            response = self.gemini_client.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            return response.text if response.text else "No response from Gemini."
        except Exception as e:
            raise RuntimeError(f"Error querying Google Gemini: {e}")


def main():
    load_dotenv()  # Load API key từ file .env
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        st.error("API Key not found in environment variables. Please set 'GENAI_API_KEY' in .env file.")
        return

    st.set_page_config(page_title="Query Milvus and Google Gemini", layout="wide")
    st.title("Milvus and Google Gemini Query Interface")

    query_handler = MilvusQueryHandler(api_key)

    st.header("Query the Database and Ask Google Gemini")
    query_text = st.text_input("Enter your query", placeholder="Type something to search...")

    if st.button("Search"):
        if query_text.strip():
            st.write("Querying database and Google Gemini...")
            try:
                # Query Milvus
                milvus_results = query_handler.query_milvus(query_text)
                st.write("### Milvus Results:")
                for result in milvus_results:
                    st.text(result)

                # Ask Google Gemini
                gemini_response = query_handler.ask_google_gemini(query_text, milvus_results)
                st.write("### Google Gemini Response:")
                st.text(gemini_response)

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid query before searching.")


if __name__ == "__main__":
    main()
