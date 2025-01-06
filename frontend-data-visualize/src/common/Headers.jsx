import React from 'react';
import { useContext } from "react";
import { motion } from "framer-motion";
import { SidebarContext } from "../context/SidebarContext";
import ChatbotAI from '../pages/Overview/ChatbotAI';

const Headers = ({ title }) => {
    console.log('Title:', title); // Thêm dòng này để kiểm tra giá trị của title
    const { isSidebarOpen } = useContext(SidebarContext);
    return (
        <header className='bg-gray-400 bg-opacity-50 backdrop-blur-md shadow-lg border-b border-gray-700'>
            <div className='w-full mx-auto py-4 px-4 sm:px-6 lg:px-8'>
                <motion.h1
                    className='text-4xl font-semibold text-transparent bg-clip-text bg-gradient-to-br from-gray-100 to-gray-200 drop-shadow-sm'
                    animate={{ paddingLeft: isSidebarOpen ? '9rem' : '6rem' }}
                    transition={{ duration: 1 }}
                >
                    {title}
                </motion.h1>
            </div>
        </header>
    );
};

export default Headers;
