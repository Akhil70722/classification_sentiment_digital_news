import React, { useState, useEffect } from "react";
import Card from "../components/card";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { Dropdown } from "flowbite-react";

const LatestPosts = () => {
  const [newsData, setNewsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data from the backend
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/");
        const data = await response.json();

        if (data && data.news) {
          setNewsData(data.news);
        } else {
          throw new Error("Invalid data format");
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return <div className="flex justify-center items-center text-2xl">Loading...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center text-2xl">Error: {error}</div>;
  }

  return (
    <>
      <div className="mb-10">
        <div className="flex justify-center items-center text-5xl m-6 mt-12">
          LATEST ARTICLES
        </div>
        <div className="flex justify-center items-center mb-4">
          Crawled more than {newsData.length}+{" "}
          <span className="font-bold ml-1 mr-1 text-lg"> LIVE </span> news!
        </div>
        <div className="flex justify-center items-center">
          <div className="flex justify-center items-center">
            <input
              style={{ width: 400, height: 50 }}
              type="text"
              className="input-text ml-4"
              placeholder="Search Keywords..."
            />
            <FontAwesomeIcon
              className="-ml-7 mt-1 hover:cursor-pointer"
              icon={faMagnifyingGlass}
            />
            <div className="ml-3">
              <Dropdown label="Top Keywords" className="text-black">
                <div className="flex flex-col space-y-2">
                  {/* Add dropdown items dynamically if needed */}
                </div>
              </Dropdown>
            </div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {newsData.map((news, index) => (
          <Card
            key={index}
            imgUrl={news["Category"]}
            Title={news["Title"]}
            description={news["Description"] || "No description available"}
            positive={Math.round(news["Sentiment"][0] * 100)}
            neutral={Math.round(news["Sentiment"][2] * 100)}
            negative={Math.round(news["Sentiment"][1] * 100)}
            time={news["Published"]}
            url={news["URL"]}
            updatedOn={news["Published"]}
          />
        ))}
      </div>
    </>
  );
};

export default LatestPosts;
