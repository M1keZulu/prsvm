"use client";
import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import { ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import {
  Dashboard,
  FolderSpecial,
  VideoCameraFront,
  ImageSearch,
  AccountTree,
  Assessment
} from '@mui/icons-material';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const panelItems = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/'
  },
  {
    text: 'Incidents',
    icon: <FolderSpecial />,
    path: '/incident'
  },
  {
    text: 'Videos',
    icon: <VideoCameraFront />,
    path: '/video'
  },
  {
    text: 'Re-id',
    icon: <ImageSearch />,
    path: '/re-id'
  },
  {
    text: 'Results',
    icon: <AccountTree />,
    path: '/'
  },
  {
    text: 'Reports',
    icon: <Assessment />,
    path: '/'
  },
];

export default function ClippedDrawer() {
  
  
  return (
    <Box display={'flex'}>
      <CssBaseline />
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: 240, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
        <List>
            {panelItems.map((item) => (
              <Link href={item.path} key={item.text}>
                <ListItemButton
                
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </Link>
            ))}
          </List>
          <Divider />
        </Box>
      </Drawer>
    </Box>
  );
}
