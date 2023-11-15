"use client";

import * as React from 'react';
import Sidebar from '../component/navbarandpanel.js';
import { Box, Grid, IconButton, Typography } from '@mui/material';
import Navbar from '../component/navbar.js';
import IncidentFolder from '../component/incidentfolder.js';

function videopage() {
  return (
    <>
    <Navbar />
    <Box mt={9}>
      <Grid container sx={{  height: '100vh' }}>
        <Grid item xs={4} md={3} lg={2} xl={2} >
          <Sidebar />
        </Grid>
        <Grid item xs={8} md={9} lg={10} xl={10}>
            <Box sx={{display:"flex", flexDirection:"row", flexWrap:"wrap"}} p={4}>
            <IncidentFolder name="maingate_incident"/>
            <IncidentFolder name="corridors_incident"/>
            <IncidentFolder name="newbuilding_incident"/>
          </Box>
        </Grid>
      </Grid>
    </Box>
  </>  )
}

export default videopage