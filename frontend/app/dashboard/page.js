"use client";

import React from 'react'
import Sidebar from '../component/navbarandpanel.js'
import Barchart from '../component/barchart.js'
import Navbar from '../component/navbar.js'
import { Box, Toolbar, Typography,Grid } from '@mui/material'
import Details from '../component/details.js';
const Thismy = () => {
  return (
    <>
    <Navbar />
    <Box mt={9}>
      <Grid container sx={{  height: '100vh' }}>
        <Grid item xs={4} md={3} lg={2} xl={2} >
          <Sidebar />
        </Grid>
        <Grid item xs={8} md={9} lg={10} xl={10}>
            <Typography mt={4} textAlign={'center'} variant='h5'>Account Details</Typography>
          <Box sx={{padding:'2% 30% 2% 30%',justifyContent:"center"}}>
            <Box borderRadius={2} border={5}  borderColor={'whitesmoke'} >
              
              <Details Name="Name" det = 'Shan'/>
              <Details Name="Account Created" det = '23-Aug-2023'/>
              <Details Name="No of incident" det = '5'/>
              <Details Name="Queries requested" det = '2'/>


             </Box>
          </Box>
          <Box  sx={{width:"100%",display:"flex",justifyContent:"flex-center"}}>
           <Barchart/>
          </Box>
          <Box  sx={{width:"100%",display:"flex",justifyContent:"flex-center"}} >
           <Barchart/>
          </Box>
        </Grid>
      </Grid>
    </Box>
  </>


  )
}

export default Thismy