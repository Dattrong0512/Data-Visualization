import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { BiMessageRoundedDots } from "react-icons/bi";
import { motion } from "framer-motion"; // Import Framer Motion

const ChatbotAI = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Xin chào! Hãy đặt câu hỏi của bạn." },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatRef = useRef(null);
  const [tempMessage, setTempMessage] = useState("");

  const scrollToBottom = () => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, tempMessage, isLoading]);

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", text: input },
    ]);
    setInput("");

    setIsLoading(true);

    try {
      const response = await axios.get(`https://127.0.0.1:5000/query`, {
        params: { query: input },
      });

      if (response.status === 200 && response.data) {
        const geminiResponse = response.data.gemini_response;
        displayResponseWordByWord(geminiResponse);
      } else {
        throw new Error("Phản hồi từ server không hợp lệ.");
      }
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "bot",
          text: "Có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const displayResponseWordByWord = (response) => {
    const words = response.split(" ");
    let index = 0;
    setTempMessage("");

    const interval = setInterval(() => {
      if (index < words.length) {
        setTempMessage((prev) => prev + words[index] + " ");
        index++;
      } else {
        clearInterval(interval);
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: response },
        ]);
        setTempMessage("");
      }
    }, 20);
  };

  return (
    <>
      {/* Icon Chat */}
      <motion.div
        className="fixed bottom-4 right-4 z-50 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
        initial={{ y: -200, scale: 0.5 }} // Bắt đầu ở trên và nhỏ hơn
        animate={{ y: 0, scale: 1 }} // Di chuyển xuống vị trí chuẩn với kích thước ban đầu
        transition={{
          type: "spring",
          stiffness: 120, // Độ căng của lò xo
          damping: 20, // Độ mềm mại của chuyển động
          times: { duration: 1.5 },
        }}
      >
        <div className="p-3 bg-gradient-to-br from-blue-500 to-teal-500 rounded-full shadow-lg hover:scale-110 transition-transform duration-300">
          <BiMessageRoundedDots size={34} className="text-white" />
        </div>
      </motion.div>

      {/* Chatbox */}
      {isOpen && (
        <motion.div
          className="fixed bottom-20 right-6 w-90 sm:w-96 h-2/3 bg-white border border-gray-300 shadow-2xl rounded-xl z-50 flex flex-col overflow-hidden"
          initial={{ y: -300, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: "spring", stiffness: 150, damping: 12 }}
        >
          {/* Header */}
          <div className="flex justify-between items-center p-4 bg-gradient-to-r from-teal-500 to-blue-500 text-white rounded-t-xl">
            <h3 className="text-lg font-semibold">Chat Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white font-bold text-2xl hover:text-gray-200 transition duration-300"
            >
              &times;
            </button>
          </div>

          {/* Chat Content */}
          <div
            ref={chatRef}
            className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50 chat-container"
          >
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"
                  } chat-message`}
              >
                <span
                  className={`px-4 py-2 rounded-2xl text-sm ${msg.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-800"
                    }`}
                >
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </span>
              </div>
            ))}

            {/* Temporary Response */}
            {tempMessage && (
              <div className="flex justify-start chat-message">
                <span className="px-4 py-2 rounded-2xl text-sm bg-gray-200 text-gray-800">
                  {tempMessage}
                </span>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="flex justify-start chat-message">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-300 flex items-center bg-gray-100">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Nhập câu hỏi của bạn..."
              className="flex-grow p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <button
              onClick={handleSendMessage}
              className="ml-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition duration-300"
            >
              Gửi
            </button>
          </div>
        </motion.div>
      )}
    </>
  );
};

export default ChatbotAI;
