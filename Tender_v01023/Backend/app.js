const express = require("express");
const bodyParser = require("body-parser");
const surveyRoutes = require("./routes/surveys");

const app = express();
app.use(bodyParser.json());

// Setup CORS
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, Cache-Control");
  next();
});

app.use('/surveys', surveyRoutes);

const port = process.env.PORT || 8000;
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
