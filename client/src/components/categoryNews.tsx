/**
 * categoryNews.tsx
 * 
 * This file previously contained hardcoded news data.
 * All data is now fetched dynamically from the API.
 * 
 * This file is kept for backward compatibility but is no longer used.
 * All components now use the API endpoints:
 * - GET /api/categories/ - for category list
 * - GET /api/news/ - for all news
 * - POST /api/news/filter/ - for filtered news by category
 */

// Export empty object for backward compatibility
// Components should use API endpoints instead
export const categoryNews = {};