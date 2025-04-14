import React, { useEffect, useState } from 'react';
import RealTimePieChart from './RealTimePieChart'; // Your pie chart component
import axios from 'axios'; // Axios for API requests

const RealTimeStatistics = () => {
  const [totalFines, setTotalFines] = useState(0);
  const [helmetViolations, setHelmetViolations] = useState(0);
  const [speedingViolations, setSpeedingViolations] = useState(0);
  const [loadingStats, setLoadingStats] = useState(true); // Loading state for statistics
  const [loadingChart, setLoadingChart] = useState(true); // Loading state for chart
  const [error, setError] = useState(null); // Error state


  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    // Fetch data from the backend for statistics
    const fetchStatistics = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/getDailyStats`); // Replace with your API endpoint
        const data = response.data.data;

        // Update state with the fetched data
        setTotalFines(data.totalFines);
        setHelmetViolations(data.helmetViolations);
        setSpeedingViolations(data.speedingViolations);
        setLoadingStats(false);
      } catch (err) {
        console.error('Error fetching statistics:', err);
        setError('Failed to fetch data. Please try again later.');
        setLoadingStats(false);
      }
    };

    fetchStatistics();

    const interval = setInterval(fetchStatistics, 30000);

  // Clear the interval on component unmount
  return () => clearInterval(interval);
  }, []);

  // Once data is loaded, prepare violations data for the chart
  const violationsData = [
    { id: 0, label: 'No-Helmet Violations', value: helmetViolations },
    { id: 1, label: 'Over-Speeding Violations', value: speedingViolations },
  ];

  useEffect(() => {
    // Once violationsData is available, stop the chart loading spinner
    if (helmetViolations || speedingViolations) {
      setLoadingChart(false);
    }
  }, [helmetViolations, speedingViolations]);

  if (loadingStats) {
    return (
      <div className="flex justify-center items-center">
        <span className="loading loading-spinner loading-md"></span>
      </div>
    );
  }

  // If there's an error, show the error alert
  if (error) {
    return (
      <div role="alert" className="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-4xl font-bold text-center mb-8">Real-Time Statistics</h2>
      
      {/* Loading state for individual card data */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex flex-col items-center text-center">
          <h3 className="text-xl font-bold mb-2">Total Fines Collected Today</h3>
          <p>₹ {totalFines}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex flex-col items-center text-center">
          <h3 className="text-xl font-bold mb-2">Number of Violations Reported</h3>
          <p>{helmetViolations + speedingViolations}</p>
        </div>
      </div>

      {/* Loading spinner for the chart */}
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg flex flex-col items-center text-center mt-6">
        <h2 className="text-xl font-bold mb-2">Violations Breakdown</h2>
        {loadingChart ? (
          <div className="flex justify-center items-center">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : (
          <RealTimePieChart violationsData={violationsData} />
        )}
      </div>
    </div>
  );
};

export default RealTimeStatistics;
