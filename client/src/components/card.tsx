import React, { useState } from "react";
import style from "../styles/card.module.css";
import Image from "next/image";

interface CardProps {
  imgUrl: string;
  Title: string;
  description: string;
  positive: number;
  neutral: number;
  negative: number;
  url: string;
  updatedOn: string;
  time: string;
  category?: string;
}

const Card: React.FC<CardProps> = (props) => {
  const [bookMark, setBookMark] = useState(false);
  const [priority, setPriority] = useState<string[]>([]);

  const handlePriorityChange = (value: string) => {
    const updatedPriority = [...priority];

    if (updatedPriority.includes(value)) {
      // If the checkbox is already selected, deselect it
      const index = updatedPriority.indexOf(value);
      updatedPriority.splice(index, 1);
    } else {
      // If the checkbox is not selected, select it
      updatedPriority.push(value);
    }

    setPriority(updatedPriority);
  };


  function extractDateFromTimestamp(timestamp: string) {
    // Check if the timestamp follows the "UPDATED: Mon DD, YYYY HH:mm IST" format
    const matchFormat1 = timestamp.match(/UPDATED: (\w{3} \d{2}, \d{4} \d{2}:\d{2} (?:AM|PM) IST)/i);
    if (matchFormat1) {
      const parsedDate = new Date(matchFormat1[1]);
      const formattedDate = `${parsedDate.getDate()}/${parsedDate.getMonth() + 1}/${parsedDate.getFullYear()}`;
      return formattedDate;
    } else {
      // Check if the timestamp follows the "Updated: Day, DD Month YYYY HH:mm PM (IST)" format
      const matchFormat2 = timestamp.match(/Updated: (\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2} (?:AM|PM) \(IST\))/i);
      if (matchFormat2) {
        const parsedDate = new Date(matchFormat2[1]);
        const formattedDate = `${parsedDate.getDate()}/${parsedDate.getMonth() + 1}/${parsedDate.getFullYear()}`;
        return formattedDate;
      } else {
        // If neither format matches, return null or handle accordingly
        return null;
      }
    }
  }
  return (
    <div className="w-full">
      <div className={style.card}>
        <div className={style.card_header}>
          {props.imgUrl && (props.imgUrl.startsWith('http://') || props.imgUrl.startsWith('https://')) ? (
            <img
              src={props.imgUrl}
              width={400}
              height={200}
              alt={props.Title}
              style={{ width: '100%', height: '180px', objectFit: 'cover' }}
              onError={(e) => {
                // Fallback to category image if article image fails to load
                const fallbackCategory = props.category || props.imgUrl || 'default';
                e.currentTarget.src = `/categories/images/${fallbackCategory}.jpg`;
                // If Next.js Image component is needed for fallback, use regular img
                e.currentTarget.onerror = null; // Prevent infinite loop
              }}
            />
          ) : (
            <Image
              src={`/categories/images/${props.imgUrl || props.category || 'default'}.jpg`}
              width={400}
              height={200}
              alt={props.Title}
            />
          )}
        </div>
        <div className={style.card_content}>
          <h3 className="flex justify-center text-center text-base font-semibold leading-tight mb-2" id="news-title">
            {props.Title}
          </h3>
          <p className="mt-2 text-sm text-gray-600 line-clamp-3" id="news-desc">
            {props.description}
          </p>
        </div>
        <div className="flex justify-center items-center space-x-3 py-3">
          <div className="flex flex-col justify-center items-center px-3 py-1.5 bg-green-50 rounded-lg">
            <span className="text-xs text-gray-600 font-medium">Positive</span>
            <div className="text-base font-bold text-green-600">{props.positive}%</div>
          </div>
          <div className="flex flex-col justify-center items-center px-3 py-1.5 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-600 font-medium">Neutral</span>
            <div className="text-base font-bold text-gray-600">{props.neutral}%</div>
          </div>
          <div className="flex flex-col justify-center items-center px-3 py-1.5 bg-red-50 rounded-lg">
            <span className="text-xs text-gray-600 font-medium">Negative</span>
            <div className="text-base font-bold text-red-600">{props.negative}%</div>
          </div>
          {!bookMark ? (
            <img
              className="hover:cursor-pointer"
              onClick={() => setBookMark(!bookMark)}
              src="Bookmark.png"
              width={40}
              height={40}
              alt=""
            />
          ) : (
            <img
              className="hover:cursor-pointer"
              onClick={() => setBookMark(!bookMark)}
              src="bookmarkActive.png"
              width={40}
              height={40}
              alt=""
            />
          )}
        </div>
        {/* Priority Checkboxes */}
        <div className={`${style.priorityCheckboxes} flex flex-row justify-center mt-2`}>
          <label className="checkbox-label mr-4">
            <input
              type="checkbox"
              value="Critical"
              checked={priority.includes("Critical")}
              onChange={() => handlePriorityChange("Critical")}
            />
            Critical
          </label>
          <label className="checkbox-label mr-4">
            <input
              type="checkbox"
              value="High"
              checked={priority.includes("High")}
              onChange={() => handlePriorityChange("High")}
            />
            High
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              value="Low"
              checked={priority.includes("Low")}
              onChange={() => handlePriorityChange("Low")}
            />
            Low
          </label>
        </div>
        <div className="flex justify-center items-center mt-3 mb-2">
          <span className="text-xs text-gray-500">{props.time}</span>
        </div>
        <div className="flex justify-between items-center pt-2 px-4 pb-3 border-t border-gray-100">
          <a
            className="text-blue-600 hover:text-blue-800 font-medium text-sm hover:underline transition-colors"
            target="_blank"
            rel="noopener noreferrer"
            href={props.url}
          >
            Read More →
          </a>
          <span className="text-xs text-gray-500">
            Updated: {extractDateFromTimestamp(props.updatedOn) || 'N/A'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Card;