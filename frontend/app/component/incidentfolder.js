import React from 'react';
import { IconButton, Typography } from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';

function IncidentFolder(props) {
  return (
    <IconButton disableRipple sx={{m:3, display: 'flex', flexDirection: 'column', alignItems: 'center', width: "100px", height: "auto" }}>
      <FolderIcon sx={{ fontSize: '70px', color: "#ADD8E6" }} />
      <Typography variant='button' sx={{wordWrap:"break-word", width:"100px"}}>
        {props.name}
      </Typography>
    </IconButton>
  );
}

export default IncidentFolder;
