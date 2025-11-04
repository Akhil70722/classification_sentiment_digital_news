// NewsCard.tsx - Updated to use dynamic API data
import React, { useState, useEffect } from "react";
import Card from "./card";

interface NewsItem {
  Source: string;
  Title: string;
  TitleHindi?: string;
  FullArticle: string;
  URL: string;
  Published: string;
  Category: string;
  Sentiment: [number, number, number];
  Emotion: string;
  Department: string;
  ImageURL: string;
  DescriptionHindi?: string;
}

interface Category {
  id: number;
  name: string;
  frontend_name: string;
}

export const NewsSection: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [newsByCategory, setNewsByCategory] = useState<Record<string, NewsItem[]>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Fetch categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/categories/");
        if (!response.ok) throw new Error("Failed to fetch categories");
        const data = await response.json();
        if (data.result === 'success' && data.categories) {
          setCategories(data.categories);
        }
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };

    fetchCategories();
  }, []);

  // Fetch news for each category
  useEffect(() => {
    if (categories.length === 0) return;

    const fetchNewsForAllCategories = async () => {
      setIsLoading(true);
      const newsData: Record<string, NewsItem[]> = {};

      try {
        // Fetch news for each category
        for (const category of categories) {
          try {
            const response = await fetch("http://127.0.0.1:8000/api/news/filter/", {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 
                category: category.frontend_name,
                language: 'en' 
              }),
            });

            if (response.ok) {
              const data = await response.json();
              if (data && data.news && data.news.length > 0) {
                // Take only first 6 items per category
                newsData[category.frontend_name] = data.news.slice(0, 6);
              }
            }
          } catch (error) {
            console.error(`Error fetching news for ${category.frontend_name}:`, error);
          }
        }

        setNewsByCategory(newsData);
      } catch (error) {
        console.error("Error fetching news:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNewsForAllCategories();
  }, [categories]);

  if (isLoading) {
    return (
      <div className="news-container p-8">
        <div className="text-center text-gray-500">Loading news...</div>
      </div>
    );
  }

  return (
    <div className="news-container">
      {categories.map((category) => {
        const newsItems = newsByCategory[category.frontend_name] || [];
        if (newsItems.length === 0) return null;

        return (
          <div key={category.id} className="category-section mb-12">
            <h2 className="category-title text-3xl font-bold mb-6 text-gray-900">
              {category.frontend_name}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {newsItems.map((item, index) => (
                <Card
                  key={index}
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
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};