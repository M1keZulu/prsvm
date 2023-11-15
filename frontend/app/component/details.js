import React from 'react'
import { Box,Grid,Typography } from '@mui/material'
function details(props) {
  return (
            <Box sx={{justifyContent:"center",padding:'2% 0% 4% 6%'}}>
              <Grid  container display={'flex'} >
                <Grid item lg={6} sm={6} md={6}>
              <Typography  variant='h5'>{props.Name}</Typography>
              </Grid>
              <Grid item lg={6} sm={6} md={6}>
              <Typography variant='h5'>{props.det}</Typography>
              </Grid>
              </Grid>
            </Box>
           
               )
}

export default details