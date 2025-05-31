
import React, { useState } from "react";
import { categoryNews } from "./categoryNews";

type NewsItem = {
  title: string;
  link: string;
  description?: string;
  source?: string;
};

const Categories = () => {
  type CategoryKey = keyof typeof categoryNews;
  const [selectedCategory, setSelectedCategory] = useState<CategoryKey | null>(null);
  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category === selectedCategory ? null : category as CategoryKey);
  };

  return (
    <>
      {/* Category Tabs */}
      <div className="flex flex-wrap justify-center items-center gap-6 py-4 px-5 bg-gray-50 font-semibold text-lg">
        {Object.keys(categoryNews).map((category) => (
          <button
            key={category}
            onClick={() => handleCategoryClick(category)}
            className={`transition-all duration-300 border-b-2 ${
              selectedCategory === category
                ? "text-blue-600 border-blue-600"
                : "border-transparent text-gray-800 hover:text-blue-500"
            }`}
          >
            {category}
          </button>
        ))}
      </div>
      {/* News Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-5">
        {selectedCategory &&
          (categoryNews[selectedCategory] as NewsItem[]).map((item, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-shadow border border-gray-200 p-5 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-xl font-semibold text-blue-700 mb-2">{item.title}</h3>
                {item.description && (
                  <p className="text-gray-700 mb-4 text-sm">{item.description}</p>
                )}
              </div>
              <div className="mt-auto pt-2 flex justify-between items-end">
                <a
                  href={item.link}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors text-sm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Read more →
                </a>
                {item.source && (
                  <span className="text-gray-400 text-xs italic">
                    {item.source}
                  </span>
                )}
              </div>
            </div>
          ))}
      </div>
    </>
  );
};

export default Categories;