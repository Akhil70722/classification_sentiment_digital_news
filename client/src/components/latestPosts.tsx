import React, { useState, useEffect } from "react";
import Card from "../components/card";

interface LatestPostsProps {
  selectedCategory: string | null;
}

const LatestPosts: React.FC<LatestPostsProps> = ({ selectedCategory }) => {
  const [newsData, setNewsData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch data from the backend
    const fetchData = async () => {
      setIsLoading(true);
      try {
        let response;
        
        if (selectedCategory) {
          // Make POST request with category filter
          response = await fetch("http://127.0.0.1:8000/", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ category: selectedCategory }),
          });
        } else {
          // Make GET request for all news
          response = await fetch("http://127.0.0.1:8000/");
        }
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        if (data && data.news !== undefined) {
          setNewsData(data.news);
          console.log(`Loaded ${data.news.length} news items`);
          if (data.news.length === 0 && selectedCategory) {
            console.warn(`No news found for category: ${selectedCategory}`);
          }
        } else {
          throw new Error(data?.message || "Invalid data format");
        }
      } catch (err: any) {
        console.error('Error fetching news:', err);
        setError(err?.message || 'Failed to fetch news');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [selectedCategory]);

  if (isLoading) {
    return <div className="flex justify-center items-center text-2xl">Loading...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center text-2xl">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-center items-center mb-4">
          <h2 className="text-4xl font-bold text-gray-900">LATEST ARTICLES</h2>
        </div>
        <div className="flex justify-center items-center mb-6">
          <p className="text-gray-600 text-lg">
            Crawled more than <span className="font-bold text-blue-600">{newsData.length}+</span>{" "}
            <span className="font-bold">LIVE</span> news!
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-7xl mx-auto">
        {newsData.map((news, index) => (
          <Card
            key={index}
            imgUrl={news["ImageURL"] || news["Category"]}
            Title={news["Title"]}
            description={news["Description"] || (typeof news["FullArticle"] === 'string' ? news["FullArticle"].substring(0, 200) : "No description available")}
            positive={Math.round(news["Sentiment"][0] * 100)}
            neutral={Math.round(news["Sentiment"][2] * 100)}
            negative={Math.round(news["Sentiment"][1] * 100)}
            time={news["Published"]}
            url={news["URL"]}
            updatedOn={news["Published"]}
            category={news["Category"]}
          />
        ))}
      </div>
    </div>
  );
};

export default LatestPosts;
