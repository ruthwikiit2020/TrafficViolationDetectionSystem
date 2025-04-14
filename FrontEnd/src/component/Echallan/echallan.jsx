import React, { useState, useCallback } from "react";
import axios from "axios";
import "./echallan.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Echallan = () => {
  const [numberPlate, setNumberPlate] = useState("");
  const [violations, setViolations] = useState([]);
  const [selectedViolation, setSelectedViolation] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // Loading state

  // Debounced search
  const handleSearch = useCallback(async () => {
    if (!numberPlate) {
      setError("Please enter a number plate.");
      setViolations([]);
      return;
    }

    setError("");
    setLoading(true); // Start loading
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/getViolations/${numberPlate}`
      );

      if (response.status === 200 && Array.isArray(response.data.data)) {
        setViolations(response.data.data);
      } else {
        setViolations([]);
        setError(response.data.message || "No data found.");
      }
      setNumberPlate(""); // Clear input after search
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("No such Number Plate found in DB, check the Number Plate.");
      setViolations([]);
    } finally {
      setLoading(false); // End loading
    }
  }, [numberPlate]);

  const calculateAmount = (className) => {
    return className === "Over-Speeding" ? 1000 : 500;
  };

  const totalFine =
    violations?.reduce(
      (sum, violation) => sum + calculateAmount(violation.class_name),
      0
    ) || 0;

  return (
    <div className="main flex flex-col items-center pt-8 px-4">
      {/* Search Input */}
      <div className="search flex justify-center items-center mb-6 w-full max-w-lg">
        <input
          type="text"
          className="input form-control form-control-sm rounded-md border-2 border-gray-300 p-3 w-full"
          placeholder="Enter your number plate"
          value={numberPlate}
          onChange={(e) => setNumberPlate(e.target.value)}
        />
        <button
          className="btn btn-primary mx-2 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-300"
          onClick={handleSearch}
        >
          Search
        </button>
      </div>

      {/* Error Message */}
      {error && <div className="alert alert-danger text-red-600">{error}</div>}

      {/* Loading Spinner */}
      {loading && (
        <div className="loading-container flex justify-center items-center my-4">
          <span className="loading loading-spinner loading-md"></span>
        </div>
      )}

      {/* Table to display violations */}
      <div className="table w-full overflow-x-auto">
        <table className="MainTable table-auto w-full text-left">
          <thead className="text-black bg-transparent">
            <tr>
              <th className="px-4 py-2">S.No</th>
              <th className="px-4 py-2">Type of Violation</th>
              <th className="px-4 py-2">Amount</th>
            </tr>
          </thead>
          <tbody className="text-white">
            {violations.length > 0 ? (
              violations.map((violation, index) => (
                <tr
                  key={index}
                  className="hover:bg-gray-700 hover:text-black transition duration-200 cursor-pointer"
                  onClick={() => setSelectedViolation(violation)}
                >
                  <td className="px-4 py-2">{index + 1}</td>
                  <td className="px-4 py-2">{violation.class_name}</td>
                  <td className="px-4 py-2">
                    ₹ {calculateAmount(violation.class_name)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3" className="text-center px-4 py-2">
                  No data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Total Fine */}
      <div className="total-fine flex justify-end items-center w-full mt-4">
        <div className="bg-transparent text-white px-4 py-2 rounded-md text-lg font-bold">
          Total Fine: ₹{totalFine}
        </div>
      </div>

      {/* Detailed Modal Card */}
      {selectedViolation && (
        <div className="modal-overlay" onClick={() => setSelectedViolation(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold mb-4">Violation Details</h2>
            <p>
              <strong>Number Plate:</strong> {selectedViolation.numberplate}
            </p>
            <p>
              <strong>Type of Violation:</strong> {selectedViolation.class_name}
            </p>
            {selectedViolation.class_name === "Over-Speeding" && (
              <p>
                <strong>Speed:</strong> {selectedViolation.speed} Km/hr
              </p>
            )}
            <p>
              <strong>Date:</strong> {selectedViolation.date}
            </p>
            <p>
              <strong>Time:</strong> {selectedViolation.time}
            </p>
            <p>
              <strong>Amount:</strong> ₹
              {calculateAmount(selectedViolation.class_name)}
            </p>
            <button
              className="close-btn"
              onClick={() => setSelectedViolation(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Echallan;
