import React from 'react'
import { AppBar,Toolbar,Avatar,Menu,MenuItem } from '@mui/material'
import { useState } from 'react';

function navbar() {
    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);
    const handleClick = (event) => {
      setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
      setAnchorEl(null);
    };

  return (
    

 <AppBar variant='elevation' position="fixed">
 <Toolbar>
   <Avatar sx={{ bgcolor: "Orange", marginLeft: "auto" }} onClick={handleClick}>N</Avatar>
   <Menu
     id="demo-positioned-menu"
     anchorEl={anchorEl}
     open={open}
     onClose={handleClose}
     anchorOrigin={{
       vertical: 'bottom',
       horizontal: 'left',
     }}
     transformOrigin={{
       vertical: 'top',
       horizontal: 'left',
     }}
   >
     <MenuItem onClick={handleClose}>Logout</MenuItem>
   </Menu>

 </Toolbar>
</AppBar>

    )
}

export default navbar