const express = require("express")
require("dotenv").config();

const botRoutes = require("./routes/botMessages");

const app = express();

app.use(express.json());

app.use("/bot-test", botRoutes);

const PORT = 4001;

app.listen(PORT, () => {
    console.log(`Teams Bot running on port ${PORT}`);
});