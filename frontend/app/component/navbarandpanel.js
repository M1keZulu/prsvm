"use client";
import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import { Menu, MenuItem } from '@mui/material';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import Avatar from '@mui/material/Avatar';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import { Dashboard } from '@mui/icons-material';
import FolderSpecialIcon from '@mui/icons-material/FolderSpecial';
import VideoCameraFrontIcon from '@mui/icons-material/VideoCameraFront';
import ImageSearchIcon from '@mui/icons-material/ImageSearch';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AssessmentIcon from '@mui/icons-material/Assessment';

//const drawerWidth = 240;

const panelItems = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/'
  },
  {
    text: 'Incidents',
    icon: <FolderSpecialIcon />,
    path: '/'
  },

  {
    text: 'Videos',
    icon: <VideoCameraFrontIcon />,
    path: '/'
  },

  {
    text: 'Re-id',
    icon: <ImageSearchIcon />,
    path: '/'
  },
  {
    text: 'Results',
    icon: <AccountTreeIcon />,
    path: '/'
  },
  {
    text: 'Reports',
    icon: <AssessmentIcon />,
    path: '/'
  },


];



export default function ClippedDrawer() {
  

  const drawerWidth = 240;
  return (
    <Box display={'flex'}>
      <CssBaseline />
     
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>

          <List>
            {panelItems.map((item) => (
              <ListItem
                key={item.text}
                disablePadding
              //onClick={() => history.push(item.path)}
              // className={location.pathname == item.path ? classes.active : null}
              >
                <ListItemButton>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider />

        </Box>
      </Drawer>
    
    </Box>
  );
}