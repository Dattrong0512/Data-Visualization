import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import dataset from '../../datasets/Dataset.csv';
import ChatbotAI from '../Overview/ChatbotAI';
import { motion } from "framer-motion"; // Import Framer Motion

const Datasets = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    Papa.parse(dataset, {
      download: true,
      header: true,
      complete: (results) => {
        console.log(results.data); // Kiểm tra dữ liệu đã phân tích cú pháp
        setData(results.data.slice(0, 10)); // Chỉ lấy 10 dòng đầu tiên
      },
    });
  }, []);

  return (
    <div className="p-4 z-30">
      {/* Phần hiển thị bảng dữ liệu */}
      <motion.div
        initial={{ x: "-100vw" }} // Start off-screen (right)
        animate={{ x: 0 }} // Animate to the center
        transition={{
          type: "spring",
          stiffness: 80,
          damping: 15,
          delay: 0.4, // Further delay for the description
        }}
      >
        <h1 className="text-4xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-br from-teal-500 via-teal-650 to-teal-800">
          Datasets
        </h1>

        <div className="overflow-auto mb-6">
          <table className="min-w-full bg-white border border-gray-300">
            <thead>
              <tr>
                {data.length > 0 &&
                  Object.keys(data[0]).map((key) => (
                    <th
                      key={key}
                      className="py-2 px-4 border-b border-gray-300 bg-gray-100 text-left text-sm font-semibold text-gray-700"
                    >
                      {key}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index} className="hover:bg-gray-100">
                  {Object.values(row).map((value, i) => (
                    <td
                      key={i}
                      className="py-2 px-4 border-b border-gray-300 text-sm text-gray-700"
                    >
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

        </div>
      </motion.div>

      {/* Phần mô tả dataset */}
      <motion.div
        initial={{ x: "100vw" }} // Start off-screen (right)
        animate={{ x: 0 }} // Animate to the center
        transition={{
          type: "spring",
          stiffness: 80,
          damping: 15,
          delay: 0.4, // Further delay for the description
        }}
      >
        <div className="bg-gray-50 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">Thông tin về Dataset</h2>
          <p className="text-gray-700 mb-4">
            <strong>Kết quả kỳ thi tốt nghiệp THPT tại Việt Nam, 2023</strong>
          </p>
          <h3 className="text-lg font-semibold mb-2">Mô tả Dataset</h3>
          <p className="text-gray-700 mb-4">
            Dataset này chứa điểm thi của 1,5 triệu học sinh trung học phổ thông tại Việt Nam tham dự kỳ thi tốt nghiệp THPT quốc gia năm 2023.
          </p>
          <p className="text-gray-700 mb-4">
            Kỳ thi kéo dài hai ngày bao gồm 6 môn thi, với các bài thi bắt buộc là Toán, Ngữ Văn và Ngoại Ngữ. Ngoài ra, học sinh chọn một trong hai tổ hợp môn:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-4">
            <li><strong>Khoa học Tự nhiên:</strong> Vật lý, Hóa học, Sinh học</li>
            <li><strong>Khoa học Xã hội:</strong> Lịch sử, Địa lý, Giáo dục Công dân</li>
          </ul>
          <p className="text-gray-700 mb-4">
            Thí sinh chọn một ngoại ngữ từ các tùy chọn sau: N1 - Tiếng Anh; N2 - Tiếng Nga; N3 - Tiếng Pháp; N4 - Tiếng Trung; N5 - Tiếng Đức; N6 - Tiếng Nhật; N7 - Tiếng Hàn.
          </p>

          <h3 className="text-lg font-semibold mb-2">Các cột dữ liệu</h3>
          <ul className="list-disc list-inside text-gray-700 mb-4">
            <li><strong>🆔 StudentID:</strong> Mã định danh duy nhất cho mỗi học sinh.</li>
            <li><strong>🧮 Mathematics:</strong> Điểm môn Toán.</li>
            <li><strong>📚 Literature:</strong> Điểm môn Ngữ Văn.</li>
            <li><strong>🌐 Foreign Language:</strong> Điểm môn Ngoại Ngữ.</li>
            <li><strong>⚙️ Physics:</strong> Điểm môn Vật lý.</li>
            <li><strong>🧪 Chemistry:</strong> Điểm môn Hóa học.</li>
            <li><strong>🌱 Biology:</strong> Điểm môn Sinh học.</li>
            <li><strong>📜 History:</strong> Điểm môn Lịch sử.</li>
            <li><strong>🌍 Geography:</strong> Điểm môn Địa lý.</li>
            <li><strong>📖 Civic Education:</strong> Điểm môn Giáo dục Công dân.</li>
            <li><strong>🗣️ Foreign Language Code:</strong> Mã đại diện cho ngoại ngữ được chọn.</li>
          </ul>

          <h3 className="text-lg font-semibold mb-2">Ứng dụng của dataset</h3>
          <ul className="list-disc list-inside text-gray-700 mb-4">
            <li>📊 <strong>Nghiên cứu giáo dục:</strong> Phân tích xu hướng kết quả học tập của học sinh qua các môn học.</li>
            <li>📈 <strong>Trực quan hóa dữ liệu:</strong> Tạo các biểu đồ và hình ảnh trực quan để truyền tải thông tin.</li>
          </ul>

        </div>
      </motion.div>
    </div>
  );
};

export default Datasets;
