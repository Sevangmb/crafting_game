import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField } from '@mui/material';
import { workstationAPI } from '../../services/api';

export default function WorkstationEditDialog({ open, onClose, workstation, onSaved, isStaff }) {
  const [form, setForm] = useState({ id: null, icon: '', name: '', description: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && workstation) {
      setForm({
        id: workstation.id,
        icon: workstation.icon || '',
        name: workstation.name || '',
        description: workstation.description || '',
      });
    }
  }, [open, workstation]);

  const onChange = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await workstationAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier la station</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField label="Icône" fullWidth value={form.icon} onChange={onChange('icon')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={8}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={12}>
            <TextField label="Description" fullWidth multiline minRows={2} value={form.description} onChange={onChange('description')} disabled={!isStaff} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button onClick={save} variant="contained" disabled={!isStaff || loading}>Enregistrer</Button>
      </DialogActions>
    </Dialog>
  );
}
