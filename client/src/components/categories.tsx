import React, { useState, useEffect } from "react";
import Card from "./card";

interface Category {
  id: number;
  name: string;
  frontend_name: string;
}

interface NewsItem {
  Source: string;
  Title: string;
  TitleHindi?: string;
  FullArticle: string;
  URL: string;
  Published: string;
  Category: string;
  Sentiment: [number, number, number]; // [positive, negative, neutral]
  Emotion: string;
  Department: string;
  ImageURL: string;
  DescriptionHindi?: string;
}

const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);

  // Fetch categories from API
  useEffect(() => {
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
      } finally {
        setIsLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  // Fetch news when category is selected
  useEffect(() => {
    if (selectedCategory) {
      setIsLoading(true);
      const fetchNews = async () => {
        try {
          const response = await fetch("http://127.0.0.1:8000/api/news/filter/", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              category: selectedCategory,
              language: 'en' 
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          if (data && data.news !== undefined) {
            setNewsData(data.news);
          }
        } catch (error) {
          console.error('Error fetching news:', error);
          setNewsData([]);
        } finally {
          setIsLoading(false);
        }
      };

      fetchNews();
    } else {
      setNewsData([]);
    }
  }, [selectedCategory]);

  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category === selectedCategory ? null : category);
  };

  return (
    <>
      {/* Category Tabs */}
      <div className="flex flex-wrap justify-center items-center gap-6 py-4 px-5 bg-gray-50 font-semibold text-lg">
        {isLoadingCategories ? (
          <div className="text-gray-500">Loading categories...</div>
        ) : (
          categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategoryClick(category.frontend_name)}
              className={`transition-all duration-300 border-b-2 ${
                selectedCategory === category.frontend_name
                  ? "text-blue-600 border-blue-600"
                  : "border-transparent text-gray-800 hover:text-blue-500"
              }`}
            >
              {category.frontend_name}
            </button>
          ))
        )}
      </div>
      {/* News Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-5">
        {isLoading ? (
          <div className="col-span-3 text-center text-gray-500">Loading news...</div>
        ) : selectedCategory && newsData.length > 0 ? (
          newsData.map((item, idx) => (
            <Card
              key={idx}
              imgUrl={item.ImageURL || item.Category}
              Title={item.Title}
              description={item.FullArticle?.substring(0, 200) || "No description available"}
              TitleHindi={item.TitleHindi}
              descriptionHindi={item.DescriptionHindi}
              positive={Math.round(item.Sentiment[0] * 100)}
              neutral={Math.round(item.Sentiment[2] * 100)}
              negative={Math.round(item.Sentiment[1] * 100)}
              time={item.Published}
              url={item.URL}
              updatedOn={item.Published}
              category={item.Category}
              language="en"
            />
          ))
        ) : selectedCategory ? (
          <div className="col-span-3 text-center text-gray-500">
            No news found for this category.
          </div>
        ) : null}
      </div>
    </>
  );
};

export default Categories;