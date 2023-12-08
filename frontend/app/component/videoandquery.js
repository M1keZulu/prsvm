"use client"

import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';
import React, { useRef, useState, useEffect } from 'react';
import captureVideoFrame from 'capture-video-frame';
import { Button, Typography,Box } from '@mui/material';
import { Margin } from '@mui/icons-material';

const VideoScreenshot = () => {
  const videoRef = useRef(null);
  const [cropper, setCropper] = useState();
  const [cropData, setCropData] = useState("");
  const [screenshot, setScreenshot] = useState('');
  const [croppedImage, setCroppedImage] = useState('');

  const takeScreenshot = () => {
    const frame = captureVideoFrame(videoRef.current, 'jpeg');
    setScreenshot(frame.dataUri);
  };

  const getCropData = () => {
    if (cropper !== undefined) {
      const croppedCanvas = cropper.getCroppedCanvas();
      if (croppedCanvas !== null) {
        setCropData(croppedCanvas.toDataURL());
      }
    }
  };

  const displaySelectedPortion = () => {
    getCropData();
    //setCroppedImage(cropData); // Remove this line from here
  };

  useEffect(() => {
    // Update croppedImage when cropData changes
    if (cropData !== "") {
      setCroppedImage(cropData);
    }
  }, [cropData]);

  return (
    <div>
     
      <video style={{height:"100%", width:"100%"}} ref={videoRef} id="my-video" autoPlay controls>
        <source src="v4.mp4" type="video/mp4" />
      </video>
     
      <Button sx={{marginY:3}} fullWidth variant="contained" component="label" onClick={takeScreenshot}>Capture frame</Button>
     
      <Cropper
        style={{  height: "100%", width: "100%", backgroundColor:"white" }}
        zoomTo={0.5}
        initialAspectRatio={1}
        preview=".img-preview"
        src={screenshot}
        viewMode={1}
        minCropBoxHeight={10}
        minCropBoxWidth={10}
        background={false}
        responsive={true}
        autoCropArea={1}
        checkOrientation={false}
        onInitialized={(instance) => {
          setCropper(instance);
        }}
        guides={true}
      />
    <Button  sx={{marginY:3}} fullWidth  variant="contained" component="label"  onClick={displaySelectedPortion}>Crop</Button>
      {croppedImage && (
        <Box boxShadow={8}  textAlign={'center'}>
          <Typography variant='h5' sx={{margin:"2rem"}}>Cropped Image</Typography>
          <img style={{margin:"auto"}} src={croppedImage} alt="Cropped" />
          <Button  sx={{marginY:3}}   variant="contained" component="label">Start Re identification</Button>
        </Box>
      )}

   

    </div>
  );
};

export default VideoScreenshot;
