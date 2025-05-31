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
    scale: 1.3,
    duration: 4000, // Change this to 4000ms for 4 seconds per slide
    transitionDuration: 300,
    infinite: true,
    prevArrow: (
      <div className="ml-10 top-40 md:top-72">
        <ArrowLeftIcon className="h-8 w-8 text-white cursor-pointer" />
      </div>
    ),
    nextArrow: (
      <div className="mr-10 top-40 md:top-72">
        <ArrowRightIcon className="h-8 w-8 text-white cursor-pointer" />
      </div>
    ),
  };
  return (
    <div className="w-full h-[90vh]">
      <Zoom {...zoomInProperties}>
        {images.map((each, index) => (
          <div
            key={index}
            className="flex justify-center md:items-center items-start w-screen h-[70vh] relative bg-black"
          >
            <img className="w-full h-full object-contain mx-auto my-auto" src={each} alt={'Slide ${index}'}/>
            {/* <p className="absolute md:top-80 top-40 inset-x-1/4 text-center z-10 md:text-2xl text-3xl bold text-white font-bold uppercase">
                Welcome To News Analysis
            </p> */}
          </div>
        ))}
      </Zoom>
    </div>
  );
};

export default ImageGallery;