const axios = require("axios");
const validator = require("validator");
const nodemailer = require("nodemailer");
const fs = require("fs");
const User = require("../models/User");

exports.getReid = (req, res) => {
    //append ML backend url to the videos array
    const videos = req.user.videos.map((video) => {
      return {
        name: video.name,
        url: process.env.ML_BACKEND_URL + video.url,
      };
    });
  
    res.render("reid", {
      title: "Reid",
      videos,
    });
  };

exports.queryReid = async (req, res) => {
    try {

        const unsorted = req.user.videos;
        const sorted = unsorted.sort((a, b) => {
            return new Date(a.date_time) - new Date(b.date_time);
        });
        const videos = sorted.map((video) => {
            return video.name;
        });

        
        console.log(videos);


        const response = await axios.post(
          process.env.ML_BACKEND_URL + "/query_reid",
          {
            video_name: req.body.videoName,
            date_time: req.body.date_time,
            timestamp: req.body.timestamp,
            height: req.body.height,
            width: req.body.width,
            x: req.body.x,
            y: req.body.y,
            filenames: videos,
          }
        );
        //add incident to user's incidents array
        req.user.incidents.push({
          name: req.body.name,
          description: req.body.description,
          id: response.data.job_id,
          video_name: req.body.videoName,
          timestamp: req.body.timestamp,
          height: req.body.height,
          width: req.body.width,
          x: req.body.x,
          y: req.body.y,
          url: response.data.secure_url,
          query_url: response.data.query_url,
          progress: 0,
        });
        await req.user.save();
        req.flash("success", { msg: "Query processing queued." });
        res.redirect("reid");
      }
      catch (error) {
        req.flash("errors", { msg: "Error processing query." });
        res.redirect("reid");
      }

};
    