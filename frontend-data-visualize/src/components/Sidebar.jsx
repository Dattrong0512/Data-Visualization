
import { GrOverview } from "react-icons/gr";
import React, { useEffect, useMemo, useState } from 'react'
import { MdDataset } from "react-icons/md";
import { animate, motion } from "framer-motion";
import { Menu } from "lucide-react";
import { Link } from "react-router-dom";
import { useContext } from "react";
import { SidebarContext } from "../context/SidebarContext";
const SIDEBAR_ITEMS = [
    {
        name: 'Overview',
        icon: GrOverview,
        color: "#6366f1",
        path: '/'
    },
    {
        name: 'DataSets',
        icon: MdDataset,
        color: "#6366f1",
        path: '/datasets'
    },
]
const Sidebar = () => {
    const { isSidebarOpen, setIsSidebarOpen } = useContext(SidebarContext);
    return (
        <motion.div
            className={`min-h-screen relative z-10 transition-all duration-300 ease-in-out flex-shrink-0 ${isSidebarOpen ? 'w-64' : 'w-20'
                }`}
            animate={{ width: isSidebarOpen ? 240 : 80 }}
        >
            <div
                className="bg-white border-r border-gray-300 shadow-lg p-4 flex flex-col h-full"
            >
                {/* Sidebar content */}
                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors max-w-fit  flex items-center justify-center"
                >
                    <Menu size={24} />
                </motion.button>

                <nav className="mt-8 flex-grow">
                    {SIDEBAR_ITEMS.map((item, index) => (
                        <Link key={index} to={item.path}>
                            <motion.div
                                className="flex items-center p-4 text-sm font-medium rounded-lg hover:bg-slate-300 transition-colors mb-2"
                            >
                                <item.icon
                                    size={20}
                                    style={{
                                        color: item.color,
                                        minWidth: '20px',
                                    }}
                                />
                                {isSidebarOpen && (
                                    <motion.span
                                        className="ml-2 text-gray-700 text-lg"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ duration: 1 }}
                                    >
                                        {item.name}
                                    </motion.span>
                                )}
                            </motion.div>
                        </Link>
                    ))}
                </nav>
            </div>
        </motion.div>
    );
};

export default Sidebar;


