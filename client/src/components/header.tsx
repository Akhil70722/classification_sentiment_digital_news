
import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect } from "react";
import Link from "next/link";

const Header = () => {
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const currTime = new Date();
    const target = new Date(currTime.getTime() + 60 * 60000);

    const interval = setInterval(() => {
      const now = new Date();
      const difference = target.getTime() - now.getTime();
      const m = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      setMinutes(m);

      const s = Math.floor((difference % (1000 * 60)) / 1000);
      setSeconds(s);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-12 items-center py-4 gap-4">
            {/* Left Side - Emblem and Time */}
            <div className="col-span-2 flex items-center gap-3">
              <img 
                src="/Emblem_of_India.svg" 
                width={35} 
                height={35} 
                alt="India Emblem" 
                className="object-contain"
              />
              <div className="text-base font-semibold text-gray-700">
                {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
              </div>
            </div>

            {/* Center - Search Bar */}
            <div className="col-span-4 flex justify-center">
              <div className="relative w-full max-w-md">
                <input
                  type="text"
                  className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  placeholder="Search Your Interest..."
                />
                <FontAwesomeIcon
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
                  icon={faMagnifyingGlass}
                />
              </div>
            </div>

            {/* Center Title */}
            <div className="col-span-2 flex justify-center">
              <h1 className="text-2xl font-bold text-black tracking-wide whitespace-nowrap">
                NEWS ANALYSIS
              </h1>
            </div>

            {/* Right Side - About, Refresh, Logo */}
            <div className="col-span-4 flex items-center justify-end gap-6">
              <div className="flex items-center gap-6">
                <a 
                  href="#about" 
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium text-sm"
                >
                  About
                </a>
                <a 
                  href="/" 
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium text-sm"
                >
                  Refresh
                </a>
              </div>
              <img 
                src="/news_logo4.png" 
                width={50} 
                height={50} 
                alt="News Logo" 
                className="object-contain"
              />
            </div>
          </div>
        </div>
        {/* Divider */}
        <hr className="border-gray-200" />
      </header>
    </>
  );
};

export default Header;