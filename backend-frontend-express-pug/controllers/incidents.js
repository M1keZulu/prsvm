const axios = require("axios");
const validator = require("validator");
const nodemailer = require("nodemailer");
const fs = require("fs");
const User = require("../models/User");

//get all incidents
exports.getIncidents = async (req, res) => {
    const videos = req.user.videos.map((video) => {
        return {
          name: video.name,
          url: process.env.ML_BACKEND_URL + video.url,
          camera: video.camera,
        };
      });

      positions = {}
      job_stat = {}
      for (let i = 0; i < req.user.incidents.length; i++) {
        const incident = req.user.incidents[i];
        try {
          const response = await axios.get(
            process.env.ML_BACKEND_URL + "/job_position/" + incident.id)
          positions[incident.id] = response.data.position;
          job_stat[incident.id] = response.data.status;
        } catch (error) {
          positions[incident.id] = null;
          job_stat[incident.id] = "Incident not processed";
        }
      }

    res.render("incidents", {
        title: "Incidents",
        incidents: req.user.incidents.map((incident) => {
            return {
                id: incident.id,
                name: incident.name,
                description: incident.description,
                video_name: incident.video_name,
                images_list: incident.images_list,
                timestamp: incident.timestamp,
                height: incident.height,
                width: incident.width,
                x: incident.x,
                y: incident.y,
                backend_url: process.env.ML_BACKEND_URL,
                url: process.env.ML_BACKEND_URL + incident.url,
                query_url: process.env.ML_BACKEND_URL + incident.query_url,
                videos_detected: incident.videos_detected,
                job_status: job_stat[incident.id],
                position: positions[incident.id]+1,
                progress: Math.floor(incident.progress),
        };
        }
        ),
        videos,
    });
    }

exports.deleteIncident = async (req, res) => {
    const incidentId = req.body.incidentId;
    //delete from backend
    try {
        await axios.post(process.env.ML_BACKEND_URL + "/delete_incident", {
            id: incidentId,
        });
    } catch (error) {
        req.flash("errors", { msg: "Error deleting incident." });
        res.redirect("/incidents");
        return;
    }

    req.user.incidents = req.user.incidents.filter((incident) => {
        return incident.id !== incidentId;
    });
    await req.user.save();
    req.flash("success", { msg: "Incident was deleted successfully." });
    res.redirect("/incidents");
    }

exports.getPDF = async (req, res) => {

}