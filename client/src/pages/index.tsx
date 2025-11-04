import Image from "next/image";
import { Inter } from "next/font/google";
import { useState } from "react";
import Header from "../components/header";
import CategoryNav from "../components/CategoryNav";
import LatestPosts from "@/components/latestPosts";
import ImageGallery from "@/components/ImageGallery";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'hi'>('en');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
      />
      <CategoryNav 
        activeCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />
      <div className="mb-4">
        <ImageGallery />
      </div>
      <LatestPosts 
        selectedCategory={selectedCategory}
        selectedLanguage={selectedLanguage}
      />
    </div>
  );
}
