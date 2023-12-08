"use client"
import React, { useRef, useState } from 'react';
import captureVideoFrame from 'capture-video-frame';
import Cropper from "react-cropper";
import { Button } from '@mui/material';


const VideoScreenshot = () => {
  const videoRef = useRef(null);
  const imgRef = useRef(null);


  const [cropper, setCropper] = useState();
  const [cropData, setCropData] = useState("");
  const [screenshot, setScreenshot] = useState('');
  const getCropData = () => {
    setCropData(cropper.getCroppedCanvas().toDataURL());
  };
  const takeScreenshot = () => {
    const frame = captureVideoFrame(videoRef.current, 'png');
    setScreenshot(frame.dataUri);
  };

  return (
    <div>
      <video ref={videoRef} id="my-video" autoPlay controls>
        <source src="v4.mp4" type="video/mp4" />
      </video>

      <button onClick={takeScreenshot}>Take Screenshot</button>

      <img ref={imgRef} id="my-screenshot" src={screenshot} alt="Screenshot" />


      <Cropper
        style={{ height: 400, width: "100%" }}
        zoomTo={0.5}
        initialAspectRatio={1}
        preview=".img-preview"
        src={screenshot}
        viewMode={1}
        minCropBoxHeight={10}
        minCropBoxWidth={10}
        onInitialized={(instance) => {
          setCropper(instance);
        }}
        background={false}
        responsive={true}
        autoCropArea={1}
        checkOrientation={false} //
        guides={true}
      />

      <Button
        variant="contained"
        sx={{
          fontFamily: "Poppins, sans-serif",
          fontSize: "14px",
          fontWeight: 600,
          letterSpacing: "2px",
          textAlign: "center",
          backgroundColor: "#7e82ff",
          width: "100%",
          marginY: 3,
        }}
        onClick={() => {
          // getCropImage();
          getCropData();
        }}
      >
        Crop
      </Button>
      <img
        style={{
          width: "500px",
          height: "400px",
          marginBottom: "20px",
        }}
        src={cropData}
        alt="cropped"
      />



    </div>
  );
};

export default VideoScreenshot;
