// NewsCard.tsx
import { categoryNews } from './categoryNews';

export const NewsSection = () => {
  return (
    <div className="news-container">
      {Object.entries(categoryNews).map(([category, items]) => (
        <div key={category} className="category-section">
          <h2 className="category-title">{category}</h2>
          <div className="news-cards">
            {(items as any[]).map((item, index) => (
              <div key={index} className="news-card">
                <img src={item.image} alt={item.title} className="card-image" />
                <div className="card-content">
                  <h3>{item.title}</h3>
                  <p className="card-description">{item.description}</p>
                  <div className="card-meta">
                    <span>{item.date}</span>
                    <span>{item.source}</span>
                  </div>
                  <a href={item.link} className="read-more">Read More</a>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};