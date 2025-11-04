import React, { useState, useEffect } from "react";
import Card from "../components/card";

interface LatestPostsProps {
  selectedCategory: string | null;
  selectedLanguage: 'en' | 'hi';
}

const LatestPosts: React.FC<LatestPostsProps> = ({ selectedCategory, selectedLanguage }) => {
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
            body: JSON.stringify({ 
              category: selectedCategory,
              language: selectedLanguage 
            }),
          });
        } else {
          // Make GET request for all news with language parameter
          response = await fetch(`http://127.0.0.1:8000/?language=${selectedLanguage}`);
        }
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        if (data && data.news !== undefined) {
          setNewsData(data.news);
          console.log(`Loaded ${data.news.length} news items for language: ${selectedLanguage}`);
          
          // Debug: Check if Hindi translations exist
          if (selectedLanguage === 'hi' && data.news.length > 0) {
            const firstItem = data.news[0];
            console.log('First news item Hindi fields:', {
              hasTitleHindi: !!firstItem['TitleHindi'],
              hasDescriptionHindi: !!firstItem['DescriptionHindi'],
              titleHindi: firstItem['TitleHindi']?.substring(0, 50),
              title: firstItem['Title']?.substring(0, 50)
            });
          }
          
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
  }, [selectedCategory, selectedLanguage]);

  if (isLoading) {
    return <div className="flex justify-center items-center text-2xl">{selectedLanguage === 'hi' ? 'लोड हो रहा है...' : 'Loading...'}</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center text-2xl">{selectedLanguage === 'hi' ? 'त्रुटि: ' : 'Error: '}{error}</div>;
  }

  const translations = {
    en: {
      title: "LATEST ARTICLES",
      subtitle: "Crawled more than",
      live: "LIVE",
      news: "news!"
    },
    hi: {
      title: "नवीनतम लेख",
      subtitle: "कुल",
      live: "लाइव",
      news: "समाचार क्रॉल किए गए!"
    }
  };

  const t = translations[selectedLanguage];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-center items-center mb-4">
          <h2 className="text-4xl font-bold text-gray-900">{t.title} {selectedLanguage === 'en' ? 'IN ' + selectedLanguage.toUpperCase() : ''}</h2>
          {selectedLanguage === 'hi' && (
            <span className="ml-2 text-2xl text-gray-600">(हिन्दी में)</span>
          )}
        </div>
        <div className="flex justify-center items-center mb-6">
          <p className="text-gray-600 text-lg">
            {t.subtitle} <span className="font-bold text-blue-600">{newsData.length}+</span>{" "}
            <span className="font-bold">{t.live}</span> {t.news}
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
            TitleHindi={news["TitleHindi"]}
            descriptionHindi={news["DescriptionHindi"]}
            positive={Math.round(news["Sentiment"][0] * 100)}
            neutral={Math.round(news["Sentiment"][2] * 100)}
            negative={Math.round(news["Sentiment"][1] * 100)}
            time={news["Published"]}
            url={news["URL"]}
            updatedOn={news["Published"]}
            category={news["Category"]}
            language={selectedLanguage}
          />
        ))}
      </div>
    </div>
  );
};

export default LatestPosts;
