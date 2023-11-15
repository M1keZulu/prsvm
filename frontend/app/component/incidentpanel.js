"use client";

import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import { useState } from 'react';
import { ListItem, TextField, Typography, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

export default function TemporaryDrawer() {
  const [state, setState] = React.useState({
    right: false,
  });

  const toggleDrawer = (anchor, open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }

    setState({ ...state, [anchor]: open });
  };

  const list = (anchor) => (
    <Box
      sx={{ width: '70vh', height: '100%' }}
      role="presentation"

    >
      <List >
        <ListItem>   
        <IconButton sx={{ marginLeft: 'auto' }} onClick={toggleDrawer(anchor, false)}><CloseIcon sx={{ color: 'red' }} />
        </IconButton>
        </ListItem>
        <ListItem>
          <Typography variant='h6'>New incident</Typography>
        </ListItem>
        <ListItem><TextField sx={{ width: '100%' }} id="outlined-basic" label="Incident" variant="outlined" ></TextField>
        </ListItem>
        <ListItem >
          <Button
            sx={{ background: "green", color: '#1976D2', '&:hover': { backgroundColor: 'green', color: "white" } }}

            onClick={toggleDrawer(anchor, false)} variant="contained">Add incident</Button>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <div>
      <Button sx={{paddingLeft:"50px",paddingRight:"50px"}} onClick={toggleDrawer('right', true)} variant='contained' component="label" >+ New Incident</Button>
      <Drawer
        anchor="right"
        open={state['right']}
        onClose={toggleDrawer('right', false)}
      >
        {list('right')}
      </Drawer>
    </div>

  );
}
