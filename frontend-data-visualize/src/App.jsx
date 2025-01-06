import { Routes, Route } from "react-router-dom";
import OverviewPages from "./pages/Overview/OverviewPages";
import Sidebar from "./components/Sidebar";
import Datasets from "./pages/Dataset/Datasets";
import DatasetPages from "./pages/Dataset/DatasetPages";

function App() {
  return (
    <div className="bg-gray-700 text-gray-900 min-h-screen flex relative">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-400 to-gray-700 z-0"></div>

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-grow flex flex-col z-10">
        <Routes>
          <Route path="/" element={<OverviewPages />} />
          <Route path="/datasets" element={<DatasetPages />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;