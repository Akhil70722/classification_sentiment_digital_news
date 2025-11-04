import React, { useState } from "react";

interface CategoryNavProps {
  onCategoryChange: (category: string | null) => void;
  activeCategory: string | null;
}

const CategoryNav: React.FC<CategoryNavProps> = ({ onCategoryChange, activeCategory }) => {
  const categories = [
    "External Affairs",
    "Law and Justice",
    "Youth Affairs and Sports",
    "Finance",
    "Internal Security",
    "Culture",
    "Information and Broadcasting",
    "Home Affairs",
    "Science and Technology",
    "Electronics and Information Technology"
  ];

  const handleCategoryClick = (category: string) => {
    if (activeCategory === category) {
      onCategoryChange(null); // Deselect if already active
    } else {
      onCategoryChange(category);
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 sticky top-[73px] z-40">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-6 py-3 overflow-x-auto scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => handleCategoryClick(category)}
              className={`whitespace-nowrap px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                activeCategory === category
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-700 hover:text-blue-500 border-b-2 border-transparent"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategoryNav;
