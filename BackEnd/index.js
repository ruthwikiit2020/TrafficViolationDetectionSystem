const express = require("express");
const mongoose = require("mongoose");
const route = require("./route/route");
const cors = require("cors");
require('dotenv').config();


const app = express();
app.use(express.json());
app.use(cors({
  // origin: "https://trafficviolation-frontend.vercel.app", 
  origin: "http://localhost:5173", 
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));

app.use((req, res, next) => {
  // res.header("Access-Control-Allow-Origin", "https://trafficviolation-frontend.vercel.app");
  res.header("Access-Control-Allow-Origin", "http://localhost:5173");
  res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  next();
});




mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

app.get("/", (req, res) => {
  res.send("Hello, World!");
});

app.use("/api", route);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
