import React, { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
const initialRows = [
  { id: 1, incidentName: 'Incident A', dateCreated: '2023-11-13', timeCreated: '10:30 AM' },
  { id: 2, incidentName: 'Incident B', dateCreated: '2023-11-14', timeCreated: '02:45 PM' },
  { id: 3, incidentName: 'Incident C', dateCreated: '2023-11-15', timeCreated: '08:20 AM' },
  { id: 4, incidentName: 'Incident D', dateCreated: '2023-11-16', timeCreated: '05:15 PM' },
  { id: 5, incidentName: 'Incident E', dateCreated: '2023-11-17', timeCreated: '01:00 PM' },
];

export default function DataTable() {
  const [rows, setRows] = useState(initialRows);

  const columns = [
    { field: 'incidentName', headerName: 'Incident Name', width: 200 },
    { field: 'dateCreated', headerName: 'Date Created', width: 160 },
    { field: 'timeCreated', headerName: 'Time Created', width: 160 },
  ];

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={5}
        checkboxSelection
      />
    </div>
  );
}
