'use client';
import React, { useState } from 'react';
import ReactPlayer from 'react-player';
import {Delete,CloudUpload,NavigateNext} from '@mui/icons-material';
import { Box,Grid, IconButton, Typography, Button } from '@mui/material';
const FileUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileChange = (event) => {
    const files = event.target.files;
    setSelectedFiles([...selectedFiles, ...files]);
  };

  const deleteFile = (index) => {
    const updatedFiles = [...selectedFiles];
    updatedFiles.splice(index, 1);
    setSelectedFiles(updatedFiles);
  };

  const handledel =()=>{
    setSelectedFiles([])
  }

  const renderVideoPlayers = () => {
    return selectedFiles.map((file, index) => (
        <Grid mt={10} container display={'flex'} sx={{justifyContent: 'space-evenly',alignItems: 'center'}} className="video-item">
        <Grid item >
            <ReactPlayer
              url={URL.createObjectURL(file)}
              controls
              width="320px"
            height="180px"
            />
        </Grid>
        <Grid item >
             <Typography variant='h6'>{file.name}</Typography>
             </Grid>
        <Grid item >
             <Typography variant='h6'>{(file.size / (1024 * 1024)).toFixed(2)} MB</Typography>
             </Grid>
             <Grid item >
            <button onClick={() => deleteFile(index)}>
              <Delete sx={{ color: 'red' }} />
            </button>
          
        </Grid>
      </Grid>
    ));
  };

  return (
    <>
    <Box textAlign={'center'}>
      <Button  sx={{ margin:"10px"}}  variant="contained" startIcon={<CloudUpload/>} component="label">
        <span>Upload videos</span>
      <input  hidden style={{border:"2px dotted black", padding:"5%"}} type="file" accept="video/*" onChange={handleFileChange} multiple/>
      </Button>
      <Button onClick={handledel}   sx={{ background: "red  !important", margin:"10px"}} variant='contained' startIcon={<Delete/>}>Delete All</Button>
      <Button  sx={{ background: "green  !important", margin:"10px"}} variant='contained' startIcon={<NavigateNext/>}>Proceed</Button>
     </Box>
      <Box>
        {renderVideoPlayers()}
      </Box>
    </>
  );
};

export default FileUpload;
