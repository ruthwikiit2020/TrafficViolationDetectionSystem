import React from "react";
import RealTimeStatistics from "../Status/RealTimeStatistics";
import './edSec.css';

const EducationSection = () => {
  const safetyTips = [
    {
      title: "Wear Helmets",
      description:
        "Always wear a helmet while riding a bike. It can save lives and reduce the severity of injuries.",
      icon: "🛵",
    },
    {
      title: "Avoid Over-Speeding",
      description:
        "Speed limits are set to ensure safety for everyone. Always drive within the prescribed limits.",
      icon: "⚡",
    },
    {
      title: "Follow Traffic Signals",
      description:
        "Traffic signals are there for a reason. Following them prevents accidents and ensures smooth traffic flow.",
      icon: "🚦",
    },
    {
      title: "Stay Alert",
      description:
        "Avoid distractions such as mobile phones while driving. Stay focused to prevent mishaps.",
      icon: "👀",
    },
  ];

  return (
    <div className="education-section bg-gray-800 py-10 px-6">
      <h2 className="text-4xl font-bold text-center mb-8">Road Safety Tips</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {safetyTips.map((tip, index) => (
          <div
            key={index}
            className="tip-card bg-gray-800 p-6 rounded-lg shadow-lg flex flex-col items-center text-center"
          >
            <div className="icon text-5xl mb-4">{tip.icon}</div>
            <h3 className="text-xl font-bold mb-2">{tip.title}</h3>
            <p>{tip.description}</p>
          </div>
        ))}
      </div>
      <div className="mt-10">
        <RealTimeStatistics />
      </div>
    </div>
  );
};

export default EducationSection;
