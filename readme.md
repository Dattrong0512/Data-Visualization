## Hướng dẫn cách khởi chạy web

### Trong folder này chứa 2 folder con:
- **data-visualize**: Front-end chứa code của web.
- **backend-data-visualize**: Back-end chứa server API và Docker để chạy container chứa vector database.

---

### Cách khởi chạy web

#### Chuẩn bị:
- Tải và cài đặt **Docker Desktop** trên máy tính.

---

#### **Bước 1**:
- Vào folder **backend-data-visualize**.
- Import các thư viện cần thiết bằng cách cài đặt các dependencies trong file `requirement.txt` bằng câu lệnh: 
    ```bash
       pip install -r requirements.txt
    ```

---

#### **Bước 2**:
- Bật **Docker Desktop** và đảm bảo các container đã chạy.
- Mở trình duyệt, truy cập địa chỉ **http://localhost:8000**.
- Đăng nhập và kiểm tra xem đã có các collection hay chưa.

---

#### **Bước 3**:
- Nếu chưa có collection:
  - Tạo collection và import data bằng cách:
    1. Chạy file `import-multimodel-rag.py` với lệnh:
       ```bash
       streamlit run import-multimodel-rag.py
       ```
    2. Chọn dataset để import (dataset nằm trong folder `frontend-data-visualize/src/datasets`).
    3. Nhấn **Import** để import data.

---

#### **Bước 4**:
- Import chứng chỉ SSL tự ký để server backend chạy trên HTTPS:
  1. Nhấn tổ hợp phím **Windows + R**, nhập `certmgr.msc` và nhấn **Enter**.
  2. Vào **Trusted Root Certification Authorities**.
  3. Trên thanh công cụ, chọn:
     - **Action → All Tasks → Import**.
  4. Nhấn **Next**, sau đó:
     - **Browse** đến file `localhost.crt` trong folder `backend-data-visualize/Certificate/`.
     - Nhấn **Next → Next** để hoàn tất.

---

#### **Bước 5**:
- Sau khi import xong data và chứng chỉ `localhost`:
  - Khởi chạy server backend:
    1. Vào file `request-api-multimodel` trong folder **backend-data-visualize**.
    2. Thực hiện khởi chạy.

---

#### **Bước 6**:
- Mở một cửa sổ **VS Code** mới.
- Khởi chạy website:
  1. Di chuyển đến folder **front-end-data-visualize**:
     ```bash
     cd front-end-data-visualize
     ```
  2. Gõ lệnh:
     ```bash
     npm run dev
     ```
  3. Truy cập địa chỉ **localhost** tương ứng để kiểm tra website.

---