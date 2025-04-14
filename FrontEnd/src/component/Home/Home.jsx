import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

const Home = React.memo(() => {
  return (
    <div className="hero min-h-screen relative">
      {/* Video Background with lazy loading */}
      <video
        className="absolute top-0 left-0 w-full h-full object-cover"
        src="images/vid1.mp4"
        autoPlay
        loop
        muted
        preload="auto" // Preloading video for quicker playback
        loading="lazy" // Lazy load video
      ></video>

      {/* Overlay for readability */}
      <div className="hero-overlay bg-black bg-opacity-50"></div>

      {/* Content with optimized text and button */}
      <div className="hero-content text-neutral-content text-center flex justify-center items-center relative z-10">
        <div className="max-w-lg text-white px-4 sm:px-8 md:px-16">
          <h1 className="mb-5 text-4xl sm:text-5xl font-bold leading-tight">
            Road Safety Matters
          </h1>
          <p className="mb-5 text-lg sm:text-xl">
            Every action on the road counts. Adhering to traffic rules can save lives.
          </p>
          <Link to="/echallan">
            <button className="btn btn-primary text-lg sm:text-xl">
              Pay Challan
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
});

export default Home;



