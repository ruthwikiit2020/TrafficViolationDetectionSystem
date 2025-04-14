const express = require("express");
const mongoose = require("mongoose");
const router = express.Router();
require('dotenv').config();

// MongoDB connection
const MONGO_URI = process.env.MONGODB_URI;

mongoose
  .connect(MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .catch((err) => console.error("Error connecting to MongoDB:", err));

// Mongoose schema and model
const ViolationSchema = new mongoose.Schema(
  {
    date: { type: String, required: true }, // Date of violation (YYYY-MM-DD)
    time: { type: String, required: true }, // Time of violation (HH:MM:SS)
    class_name: { type: String, required: true }, // Type of violation (e.g., "Overspeeding", "No Helmet")
    numberplate: { type: String, required: true }, // Common field
    speed: { type: Number }, // Optional: Only for speed violations
  },
  { collection: "violations" } // Specify collection name
);

const Violation = mongoose.model("Violation", ViolationSchema,"violations");

// Endpoint to get violations by number plate
router.get("/getViolations/:numPlate", async (req, res) => {
  try {
    const { numPlate } = req.params;

    // Validate number plate input
    if (!numPlate || typeof numPlate !== "string" || numPlate.trim() === "") {
      return res
        .status(400)
        .json({ message: "Invalid or missing number plate." });
    }

    // Find violations in the database
    const data = await Violation.find({ numberplate: numPlate.trim() });

    // Check if any violations exist
    if (data.length === 0) {
      return res
        .status(200)
        .json({ message: "No violations found for the provided number plate." });
    }

    // Send the violations data
    res.status(200).json({ status: "success", data });
    console.log(res)
  } catch (error) {
    console.error("Error in fetching violations from DB:", error);
    res.status(500).json({
      message: "An error occurred while fetching violations.",
      error: error.message,
    });
  }
});

//Endpoint to get dailyStats
router.get("/getDailyStats", async (req, res) => {
  try {
    const today = new Date().toISOString().split("T")[0]; // Get current date in YYYY-MM-DD format

    // Fetch the data for today's violations
    const violations = await Violation.find({ date: `${today}` });

    console.log("piechartr : ",violations)

    // Calculate total fines and counts
    let totalFines = 0;
    let helmetViolations = 0;
    let speedingViolations = 0;

    violations.forEach((violation) => {
      if (violation.class_name === "No-Helmet") {
        helmetViolations++;
        totalFines += 500; // Assuming a fine of 500 for no helmet violations
      } else if (violation.class_name === "OverSpeeding") {
        speedingViolations++;
        totalFines += 1000; // Assuming a fine of 1000 for speeding violations
      }
    });

    // Respond with the computed statistics
    res.status(200).json({
      status: "success",
      data: {
        totalFines,
        helmetViolations,
        speedingViolations,
      },
    });
  } catch (error) {
    console.error("Error fetching daily statistics:", error);
    res.status(500).json({
      message: "An error occurred while fetching daily statistics.",
      error: error.message,
    });
  }
});

// Export the router
module.exports = router;
