'use client';
import * as React from 'react';
import Sidebar from '../component/navbarandpanel.js';
import { Box, Grid, IconButton, Typography } from '@mui/material';
import Navbar from '../component/navbar.js';
import  Videocrop from '../component/videoandquery.js'
function page() {
  return (
<>
    <Navbar />
    <Box mt={9}>
      <Grid container sx={{  height: '100vh' }}>
        <Grid item xs={4} md={3} lg={2} xl={2} >
          <Sidebar />
        </Grid>
        <Grid item xs={8} md={9} lg={10} xl={10}>
            <Box   sx={{
        padding: { xs: 2, sm: 2, md: 5, lg: 10, xl: 10 },
      }}     >
        <Videocrop/>
          </Box>
        </Grid>
      </Grid>
    </Box>
  </> 
  )
}

export default page