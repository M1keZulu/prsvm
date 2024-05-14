const axios = require("axios");
const validator = require("validator");
const nodemailer = require("nodemailer");
const fs = require("fs");
const User = require("../models/User");

//create server side event stream that streams after connection to socketio
exports.streamProgress = async (req, res) => {
}

exports.processVideo = async (req, res) => {
  const videoName = req.params.name;
  const video = req.user.videos.find((video) => {
    return video.name === videoName;
  });

  if (!video) {
    req.flash("errors", { msg: "Video was not found." });
    res.redirect("/videos");
  }

  try {
    const response = await axios.post(
      process.env.ML_BACKEND_URL + "/process_video",
      {
        video_name: videoName,
        date_time: video.date_time,
      }
    );

    //push job_id to video object
    video.job_id = response.data.job_id;
    await req.user.save();
    req.flash("success", { msg: "Video processing queued." });
    res.redirect("/videos");
  } catch (error) {
    req.flash("errors", { msg: "Error processing video." });
    res.redirect("/videos");
  }
};

exports.deleteVideo = async (req, res) => {
  const videoName = req.params.name;
  req.user.videos = req.user.videos.filter((video) => {
    return video.name !== videoName;
  });

  try {
    await axios.delete(process.env.ML_BACKEND_URL + "/delete_video", {
      data: {
        video_name: videoName,
      },
    });
    await req.user.save();
    req.flash("success", { msg: "Video was deleted successfully." });
    res.redirect("/videos");
  } catch (error) {
    if (error.response.status === 404) {
      await req.user.save();
      req.flash("errors", { msg: "Video was not found." });
    } else {
      req.flash("errors", { msg: "Error deleting video." });
    }
    res.redirect("/videos");
  }
};

//get all videos
exports.getVideos = async (req, res) => {

  //get position of all videos using get request to job_position
  positions = {}
  job_stat = {}
  for (let i = 0; i < req.user.videos.length; i++) {
    const video = req.user.videos[i];
    try {
      const response = await axios.get(
        process.env.ML_BACKEND_URL + "/job_position/" + video.job_id)
      positions[video.name] = response.data.position;
      job_stat[video.name] = response.data.status;
    } catch (error) {
      positions[video.name] = null;
      job_stat[video.name] = "Video not processed";
    }
  }

  //append ML backend url to the videos array
  const videos = req.user.videos.map((video) => {
    return {
      name: video.name,
      url: process.env.ML_BACKEND_URL + video.url,
      position: positions[video.name]+1,
      job_status: job_stat[video.name],
      progress: Math.floor(video.progress),
    };
  });

  console.log(videos);

  const cameras = req.user.cams.map((cam) => {
    return {
      name: cam.name,
      location: cam.location,
      description: cam.description,
      longitude: cam.longitude,
      latitude: cam.latitude,
    };
  });

  res.render("videos", {
    title: "Videos",
    videos,
    cameras,
  });
};

exports.postVideos = async (req, res) => {
  const formData = new FormData();

  const file = await fs.promises.readFile(req.file.path);
  const fileName = req.file.filename;
  const blob = new Blob([file], { type: req.file.mimetype });

  formData.append("file", blob, fileName);

  try {
    const response = await axios({
      method: "POST",
      url: process.env.ML_BACKEND_URL + "/upload_video",
      data: formData,
      headers: {
        "content-type": `multipart/form-data`,
      },
    });
    //update user's videos array

    //get camera name from form
    const cameraName = req.body.camera
    const camera = req.user.cams.find((cam) => {
      return cam.name === cameraName;
    });

    console.log(req.body)

    req.user.videos.push({
      name: fileName,
      url: response.data.secure_url,
      camera: camera,
      date_time: req.body.date_time,
      job_id: null,
      processed: false,
      progress: 0,
    });

    await req.user.save();

    req.flash("success", { msg: "Video was uploaded successfully." });
    res.redirect("videos");
  } catch (error) {
    req.flash("errors", { msg: "Error uploading video." });
    res.redirect("videos");
  }

  //delete file from local storage
  await fs.promises.unlink(req.file.path);
};
