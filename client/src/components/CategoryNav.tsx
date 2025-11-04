import React, { useState, useEffect } from "react";

interface CategoryNavProps {
  onCategoryChange: (category: string | null) => void;
  activeCategory: string | null;
}

interface Category {
  id: number;
  name: string;
  frontend_name: string;
}

const CategoryNav: React.FC<CategoryNavProps> = ({ onCategoryChange, activeCategory }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch categories from API
    const fetchCategories = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/categories/");
        if (!response.ok) {
          throw new Error("Failed to fetch categories");
        }
        const data = await response.json();
        if (data.result === 'success' && data.categories) {
          setCategories(data.categories);
        }
      } catch (error) {
        console.error("Error fetching categories:", error);
        // Fallback to empty array on error
        setCategories([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  const handleCategoryClick = (category: string) => {
    if (activeCategory === category) {
      onCategoryChange(null); // Deselect if already active
    } else {
      onCategoryChange(category);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white border-b border-gray-200 sticky top-[73px] z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center gap-6 py-3">
            <div className="text-gray-500 text-sm">Loading categories...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-b border-gray-200 sticky top-[73px] z-40">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-6 py-3 overflow-x-auto scrollbar-hide">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategoryClick(category.frontend_name)}
              className={`whitespace-nowrap px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                activeCategory === category.frontend_name
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-700 hover:text-blue-500 border-b-2 border-transparent"
              }`}
            >
              {category.frontend_name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategoryNav;
