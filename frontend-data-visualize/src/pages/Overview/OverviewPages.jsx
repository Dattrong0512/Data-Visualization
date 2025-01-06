import { motion } from "framer-motion";
import Headers from "../../common/Headers";
import ChatbotAI from "./ChatbotAI";
import Dashboard from "./Dashboard";

const OverviewPages = () => {
  return (
    <div className="flex flex-col h-full z-10 relative">
      {/* Header */}
      <motion.div
        initial={{ y: "-100%" }}
        animate={{ y: 0 }}
        transition={{
          duration: 2,
          ease: "easeOut",
        }}
        className="h-[10%] z-10"
      >
        <Headers title="Overview" />
      </motion.div>

      {/* Dashboard */}
      <div className="flex-grow flex overflow-hidden h-[90%] z-10">
        <Dashboard />
      </div>
        
      {/* Chatbot */}
      <ChatbotAI />
    </div>
  );
};

export default OverviewPages;