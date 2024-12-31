import streamlit as st
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
from google import genai
from google.genai import types
from PIL import Image
import fitz
import io
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import os
from ratelimit import limits, sleep_and_retry
import time
from typing import List
import time  # Thêm thư viện time
from pymilvus import utility


@dataclass
class Config:
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    COLLECTION_NAME: str = ""
    EMBEDDING_DIM: int = 768
    MODEL_NAME: str = "gemini-2.0-flash-exp"
    TEXT_EMBEDDING_MODEL_ID: str = "text-embedding-004"
    DPI: int = 300
    FILE_TYPE: str = ""


class PDFProcessor:
    @staticmethod
    def pdf_to_images(pdf_path: str, dpi: int = Config.DPI) -> List[Image.Image]:
        images = []
        pdf_document = fitz.open(pdf_path)
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        pdf_document.close()
        return images


class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key is required")
        self.client = genai.Client(api_key=api_key)

    @sleep_and_retry
    @limits(calls=6, period=60)  # Giới hạn 5 lần gọi mỗi 60 giây
    def analyze_page(self, image: Image.Image) -> str:
        time.sleep(1)  # Tạm dừng 5 giây trước mỗi yêu cầu
        prompt = """You are an assistant tasked with summarizing images for retrieval.
        These summaries will be embedded and used to retrieve the raw image.
        Extract all text content from the page accurately."""
        try:
            time.sleep(1)  # Tạm dừng 1 giây để tránh vượt quá giới hạn
            response = self.client.models.generate_content(
                model=Config.MODEL_NAME,
                contents=[prompt, image]
            )
            return response.text if response.text else ""
        except Exception as e:
            print(f"Error analyzing page: {e}")
            return ""

    # @sleep_and_retry
    # @limits(calls=6, period=60)  # Giới hạn 5 lần gọi mỗi 60 giây
    def create_embeddings(self, text: str):
        time.sleep(1)  # Tạm dừng 1 giây trước mỗi yêu cầu
        response = self.client.models.embed_content(
            model=Config.TEXT_EMBEDDING_MODEL_ID,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        if Config.FILE_TYPE == "csv":
            return response.embeddings[0].values
        else:
            return response


class MilvusHandler:
    def __init__(self, collection_name: str = Config.COLLECTION_NAME, embedding_dim: int = Config.EMBEDDING_DIM):
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.collection = None

    def connect(self):
        connections.connect(
        host=Config.MILVUS_HOST,
        port=Config.MILVUS_PORT,
        timeout=120  # Tăng giá trị timeout
        )
        print("Connected to Milvus")

    def create_collection_csv(self):
        self.connect()

        # Kiểm tra nếu collection đã tồn tại
        existing_collections = utility.list_collections()
        print(existing_collections)
        if self.collection_name in existing_collections:
            print(f"Collection '{self.collection_name}' already exists. Using the existing collection.")
            self.collection = Collection(name=self.collection_name)
            return
        print(f"Collection '{self.collection_name}' does not exist. Creating a new one...")
        # Các trường mặc định
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=20000),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        ]
        # # Thêm các trường từ csv_columns làm VARCHAR
        # for column in csv_columns:
        #     fields.append(FieldSchema(name=column, dtype=DataType.VARCHAR, max_length=200))

        # Tạo schema
        schema = CollectionSchema(fields=fields, description="Dynamic schema from CSV columns")
        try:
            self.collection = Collection(name=self.collection_name, schema=schema)
            print(f"Collection '{self.collection_name}' created successfully.")
        except Exception as e:
            print(f"Error creating collection: {e}")
            self.collection = None


    def create_collection_pdf(self):
        self.connect()

        # Kiểm tra nếu collection đã tồn tại
                # Kiểm tra nếu collection đã tồn tại
        existing_collections = utility.list_collections()

        print(existing_collections)
        # Kiểm tra nếu collection đã tồn tại
        if self.collection_name in existing_collections:
            print(f"Collection '{self.collection_name}' already exists. Using the existing collection.")
            self.collection = Collection(name=self.collection_name)
            return

        # Nếu chưa tồn tại, tạo mới
        print(f"Collection '{self.collection_name}' does not exist. Creating a new one...")
        id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000)
        vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)

        schema = CollectionSchema(fields=[id_field, text_field, vector_field], description="Document Embeddings")
        self.collection = Collection(name=self.collection_name, schema=schema)
        print(f"Collection '{self.collection_name}' created successfully.")
        
    def insert_data(self, batch_texts: List[str], vectors: List[List[float]]):
        if not self.collection:
            print("Collection not initialized.")
            return

        # Chèn vào Milvus
        self.collection.insert([batch_texts, vectors])
        self.collection.create_index(
            field_name="vector",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
        )
        self.collection.load()
        print(f"Inserted {len(batch_texts)} records into '{self.collection_name}'.")

class ImportHandler:
    def __init__(self, api_key: str, collection_name: str = Config.COLLECTION_NAME):
        self.gemini_client = GeminiClient(api_key)
        self.milvus_handler = MilvusHandler(collection_name=collection_name)
        self.data_df = None

    def process_pdf(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.milvus_handler.create_collection_pdf()
        st.write("Converting PDF to images...")
        images = PDFProcessor.pdf_to_images(pdf_path)

        page_contents = []
        page_analyses = []

        st.write("Analyzing PDF pages...")
        for i, image in enumerate(tqdm(images)):
            content = self.gemini_client.analyze_page(image)
            if content:
                page_contents.append({'page_number': i + 1, 'content': content})
                page_analyses.append(content)

        if not page_analyses:
            raise ValueError("No content found in PDF pages")

        self.data_df = pd.DataFrame({
            'Original Content': page_contents,
            'Analysis': page_analyses
        })

        st.write("Generating embeddings...")
        embeddings = []
        for text in tqdm(self.data_df['Analysis']):
            embedding = self.gemini_client.create_embeddings(text)
            embeddings.append(embedding.embeddings[0].values)

        if len(embeddings) != len(self.data_df):
            raise ValueError(f"Embeddings length ({len(embeddings)}) does not match DataFrame length ({len(self.data_df)})")

        self.data_df['Embeddings'] = embeddings

        st.write("Saving to Milvus...")
        texts = [content['content'] for content in page_contents]
        self.milvus_handler.insert_data(texts, embeddings)
        st.success(f"Processed {len(texts)} pages and saved embeddings to Milvus.")


    def process_csv(self, csv_path: str, batch_size: int = 200):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        st.write("Reading CSV file...")
        self.data_df = pd.read_csv(csv_path)

        # Sửa tên cột trong DataFrame thành định dạng hợp lệ
        self.data_df.columns = [col.replace(" ", "_").replace("-", "_").replace(".", "_") for col in self.data_df.columns]

        # Lấy danh sách cột sau khi sửa
        csv_columns = self.data_df.columns.tolist()
        print(f"CSV Columns: {csv_columns}")

        # Tạo collection trong Milvus với danh sách cột đã sửa
        self.milvus_handler.create_collection_csv()

        st.write(f"Generating embeddings in batches of {batch_size} rows...")
        batch_texts = []
        embeddings = []
        print(f"Expected columns for other_fields_data: {csv_columns[0:]}")

        total_rows = len(self.data_df)
        # Tạo văn bản từ dữ liệu các cột
        # Tạo văn bản từ dữ liệu các cột
        for start in tqdm(range(0, total_rows, batch_size)):
            end = min(start + batch_size, total_rows)
            batch = self.data_df.iloc[start:end]

            # Gom nhóm 10 dòng/lần
            for i in range(0, len(batch), 10):
                sub_batch = batch.iloc[i:i+10]

                # Tạo văn bản gộp (xử lý giá trị null)
                batch_text = " | ".join(
                    f"{col}: {','.join(sub_batch[col].fillna('None').astype(str).tolist())}"
                    for col in csv_columns
                )

                # **In chuỗi gộp ra màn hình**
                print(f"Generated text for group {i // 10 + 1}:")
                print(batch_text)
                print("-" * 80)

                try:
                    # Tạo embedding cho nhóm
                    batch_embedding = self.gemini_client.create_embeddings(batch_text)
                    embeddings.append(batch_embedding)
                    batch_texts.append(batch_text)
                except Exception as e:
                    print(f"Error creating embedding for group {i}-{i+10}: {e}")
                    continue

        if not batch_texts:
            raise ValueError("No valid data to insert into Milvus.")

        # Chuẩn bị dữ liệu chèn vào Milvus
        st.write(f"Inserting {len(batch_texts)} records into Milvus...")
        try:
            self.milvus_handler.insert_data(batch_texts, embeddings)
            st.success(f"Processed {len(batch_texts)} records and saved embeddings to Milvus.")
        except Exception as e:
            st.error(f"Error inserting data into Milvus: {e}")




def main():
    load_dotenv()  # Load .env file
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        st.error("API Key not found in environment variables. Please set 'GENAI_API_KEY' in .env file.")
        return

    st.set_page_config(page_title="CSV Processor with Milvus", layout="wide")
    st.title("CSV Embedding Processor")

    collection_name = st.text_input("Enter the name for the collection", value="data_visualize")

    
    uploaded_file = st.file_uploader("Upload a CSV or PDF file", type=["csv", "pdf"])
    batch_size = None

    if uploaded_file and str(uploaded_file.name).endswith('.csv'):
        batch_size = st.number_input(
            "Enter the batch size for processing (number of rows per embedding)",
            min_value=1,
            value=10,
        )

    if st.button("Import and Process"):
        if uploaded_file:
            st.write(collection_name)
            Config.COLLECTION_NAME = collection_name
            st.write(Config.COLLECTION_NAME)
            handler = ImportHandler(api_key, collection_name=Config.COLLECTION_NAME)
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            start_time = time.time()

            try:
                if str(uploaded_file.name).endswith('.csv'):
                    st.write("Processing CSV file...")
                    Config.FILE_TYPE = "csv"
                    handler.process_csv(temp_path, batch_size=batch_size)
                else:
                    st.write("Processing PDF file...")
                    Config.FILE_TYPE = "pdf"
                    handler.process_pdf(temp_path)
                            
                  # Ghi lại thời gian kết thúc
                end_time = time.time()
                elapsed_time = end_time - start_time

                st.success(f"File processed successfully in {elapsed_time:.2f} seconds!")
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
        else:
            st.error("Please upload a file before processing.")

if __name__ == "__main__":
    main()

