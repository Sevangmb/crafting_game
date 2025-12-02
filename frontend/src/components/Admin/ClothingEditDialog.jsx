import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, MenuItem } from '@mui/material';
import { clothingAPI } from '../../services/api';

export default function ClothingEditDialog({ open, onClose, clothing, onSaved, isStaff }) {
  const [form, setForm] = useState({
    id: null,
    icon: '',
    name: '',
    defense: 0,
    weight: 0,
    slot: 'chest',
    description: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && clothing) {
      setForm({
        id: clothing.id,
        icon: clothing.icon || '',
        name: clothing.name || '',
        defense: clothing.defense ?? 0,
        weight: clothing.weight ?? 0,
        slot: clothing.slot || 'chest',
        description: clothing.description || '',
      });
    }
  }, [open, clothing]);

  const onChange = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: ['defense', 'weight'].includes(field) ? Number(e.target.value) : e.target.value,
    }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await clothingAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier le vêtement</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField label="Icône" fullWidth value={form.icon} onChange={onChange('icon')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={8}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Défense" fullWidth value={form.defense} onChange={onChange('defense')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Poids" fullWidth value={form.weight} onChange={onChange('weight')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField
              select
              label="Emplacement"
              fullWidth
              value={form.slot}
              onChange={onChange('slot')}
              disabled={!isStaff}
            >
              {['head', 'chest', 'legs', 'feet', 'accessory'].map((v) => (
                <MenuItem key={v} value={v}>
                  {v}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Description"
              fullWidth
              multiline
              minRows={2}
              value={form.description}
              onChange={onChange('description')}
              disabled={!isStaff}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button onClick={save} variant="contained" disabled={!isStaff || loading}>
          {loading ? 'Enregistrement...' : 'Enregistrer'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
