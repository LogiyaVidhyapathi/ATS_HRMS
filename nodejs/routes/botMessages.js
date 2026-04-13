const express = require("express");
const router = express.Router();
 
const { joinMeeting } = require("../services/teamsJoinService");
const { handleCall } = require("../handlers/callHandler");
 
/* FastAPI backend calls this endpoint to make the bot join the meeting*/
 
router.post("/join-meeting-test", async (req, res) => {
 
    try {
        console.log("Join meeting request received");
 
        const { meetingUrl } = req.body;
 
        console.log("Meeting URL:", meetingUrl)
 
        await joinMeeting(meetingUrl)
 
        res.send("Bot joined meeting");
    } catch (error) {
        // console.error(error);
 
        // res.status(500).send("Error joining meeting");
 
        console.error("Error:", error.response?.data || error.message);
 
        res.status(500).json({
            message: "Error joining meeting",
            error: error.response?.data || error.message
        });
    }
});
 
/* Microsoft Graph sends meeting events here */
router.post("/calls-test", handleCall);
 
module.exports = router;