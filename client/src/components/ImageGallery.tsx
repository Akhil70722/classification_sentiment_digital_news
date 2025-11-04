import React from "react";
import { Zoom } from "react-slideshow-image";
import "react-slideshow-image/dist/styles.css";
import { ArrowLeftIcon, ArrowRightIcon } from "@heroicons/react/24/solid";

const ImageGallery = () => {
  //Array of Images
  const images = [
    "https://media.istockphoto.com/id/1329704926/photo/concept-of-indian-justice-system-showing-by-using-judge-gavel-balance-scale-on-indian-flag-as.jpg?s=612x612&w=0&k=20&c=-E8skqunh-qSszI0etp8-56tp6HfUecFndPAIb5ezoA=",
    "https://i.cdn.newsbytesapp.com/images/l95420221215105514.jpeg",
    "/categories/images/international.jpg",
    "/categories/images/business.jpg",
    "/categories/images/culture.jpg",
    "/categories/images/entertainment.jpg",
    "/categories/images/science.jpg",
  ];

  //These are custom properties for zoom effect while slide-show
   const zoomInProperties = {
    scale: 1.1,
    duration: 4000, // Change this to 4000ms for 4 seconds per slide
    transitionDuration: 300,
    infinite: true,
    prevArrow: (
      <div className="ml-8 top-1/2 transform -translate-y-1/2 z-10 bg-black/30 hover:bg-black/50 rounded-full p-2 transition-colors">
        <ArrowLeftIcon className="h-6 w-6 text-white cursor-pointer" />
      </div>
    ),
    nextArrow: (
      <div className="mr-8 top-1/2 transform -translate-y-1/2 z-10 bg-black/30 hover:bg-black/50 rounded-full p-2 transition-colors">
        <ArrowRightIcon className="h-6 w-6 text-white cursor-pointer" />
      </div>
    ),
  };
  return (
    <div className="w-full h-[90vh] relative overflow-hidden">
      <Zoom {...zoomInProperties}>
        {images.map((each, index) => (
          <div
            key={index}
            className="flex justify-center items-center w-full h-[90vh] relative"
          >
            <img 
              className="w-full h-full object-cover" 
              src={each} 
              alt={`Slide ${index}`}
            />
            {/* Optional: Overlay text */}
            {/* <div className="absolute inset-0 flex items-center justify-center bg-black/20">
              <p className="text-white text-4xl md:text-6xl font-bold uppercase text-center px-4">
                Welcome To News Analysis
              </p>
            </div> */}
          </div>
        ))}
      </Zoom>
    </div>
  );
};

export default ImageGallery;