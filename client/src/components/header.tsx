
import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass, faChevronDown } from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect } from "react";
import Link from "next/link";

interface HeaderProps {
  selectedLanguage: 'en' | 'hi';
  onLanguageChange: (lang: 'en' | 'hi') => void;
}

const Header: React.FC<HeaderProps> = ({ selectedLanguage, onLanguageChange }) => {
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);

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

  const languages = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' }
  ];

  const currentLanguage = languages.find(lang => lang.code === selectedLanguage) || languages[0];

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
                  placeholder={selectedLanguage === 'hi' ? "अपनी रुचि खोजें..." : "Search Your Interest..."}
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

            {/* Right Side - Language Selector, About, Refresh, Logo */}
            <div className="col-span-4 flex items-center justify-end gap-4">
              {/* Language Selector */}
              <div className="relative">
                <button
                  onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors duration-200 border border-gray-300 rounded-lg bg-white hover:bg-gray-50"
                >
                  <span>{currentLanguage.nativeName}</span>
                  <FontAwesomeIcon 
                    icon={faChevronDown} 
                    className={`text-xs transition-transform duration-200 ${showLanguageDropdown ? 'transform rotate-180' : ''}`}
                  />
                </button>
                
                {showLanguageDropdown && (
                  <>
                    <div 
                      className="fixed inset-0 z-10" 
                      onClick={() => setShowLanguageDropdown(false)}
                    ></div>
                    <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                      {languages.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => {
                            onLanguageChange(lang.code as 'en' | 'hi');
                            setShowLanguageDropdown(false);
                          }}
                          className={`w-full text-left px-4 py-2 text-sm hover:bg-blue-50 transition-colors ${
                            selectedLanguage === lang.code 
                              ? 'bg-blue-50 text-blue-600 font-medium' 
                              : 'text-gray-700'
                          }`}
                        >
                          {lang.nativeName}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>

              <div className="flex items-center gap-6">
                <a 
                  href="#about" 
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium text-sm"
                >
                  {selectedLanguage === 'hi' ? 'के बारे में' : 'About'}
                </a>
                <a 
                  href="/" 
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium text-sm"
                >
                  {selectedLanguage === 'hi' ? 'ताज़ा करें' : 'Refresh'}
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