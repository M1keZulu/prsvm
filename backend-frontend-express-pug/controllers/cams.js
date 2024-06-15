const axios = require("axios");
const validator = require("validator");
const nodemailer = require("nodemailer");
const fs = require("fs");
const User = require("../models/User");

exports.getCams = (req, res) => {
    res.render("cams", {
        title: "Cams",
        cameras: req.user.cams.map((cam) => {
            return {
                name: cam.name,
                location: cam.location,
                description: cam.description,
                longitude: cam.longitude,
                latitude: cam.latitude,
            };
        }),
    });
    }

exports.addCam = async (req, res) => {
    const { name, location, description, longitude, latitude } = req.body;

    //validate input
    if (!name || !location || !description || !longitude || !latitude) {
        req.flash("errors", { msg: "Please fill in all fields." });
        res.redirect("/cams");
        return;
    }

    //camera name must be unique
    if (req.user.cams.some((cam) => cam.name === name)) {
        req.flash("errors", { msg: "Camera name already exists." });
        res.redirect("/cams");
        return;
    }

    req.user.cams.push({
        name,
        location,
        description,
        longitude,
        latitude,
    });
    await req.user.save();
    req.flash("success", { msg: "Cam was added successfully." });
    res.redirect("/cams");
}