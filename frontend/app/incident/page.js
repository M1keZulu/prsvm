"use client";

import * as React from 'react';
import IncidentPanel from '../component/incidentpanel.js'
import Sidebar from '../component/navbarandpanel.js';
import { Box, Grid } from '@mui/material';
import Navbar from '../component/navbar.js';
import Tableincident from '../component/table_incident.js';
import { Tab } from '@mui/icons-material';
export default function IncidentAdd() {
  return (
    <>
      <Navbar />
      <Box mt={9}>
        <Grid container sx={{  height: '100vh' }}>
          <Grid item xs={4} md={3} lg={2} xl={2} >
            <Sidebar />
          </Grid>
          <Grid item xs={8} md={9} lg={10} xl={10}>
            <Box  mt={3}  textAlign={'end'} sx={{ paddingRight:4}}>
              <IncidentPanel />
            </Box>

            <Box sx={{padding:4}}>
              <Tableincident/>
            </Box>



          </Grid>
        </Grid>
      </Box>
    </>
  );
}
