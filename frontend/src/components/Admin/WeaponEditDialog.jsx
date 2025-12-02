import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, MenuItem } from '@mui/material';
import { weaponsAPI } from '../../services/api';

export default function WeaponEditDialog({ open, onClose, weapon, onSaved, isStaff }) {
  const [form, setForm] = useState({
    id: null,
    icon: '',
    name: '',
    attack: 0,
    defense: 0,
    weight: 0,
    slot: 'main_hand',
    description: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && weapon) {
      setForm({
        id: weapon.id,
        icon: weapon.icon || '',
        name: weapon.name || '',
        attack: weapon.attack ?? 0,
        defense: weapon.defense ?? 0,
        weight: weapon.weight ?? 0,
        slot: weapon.slot || 'main_hand',
        description: weapon.description || '',
      });
    }
  }, [open, weapon]);

  const onChange = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: ['attack', 'defense', 'weight'].includes(field) ? Number(e.target.value) : e.target.value,
    }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await weaponsAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier l'arme</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField label="Icône" fullWidth value={form.icon} onChange={onChange('icon')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={8}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Attaque" fullWidth value={form.attack} onChange={onChange('attack')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Défense" fullWidth value={form.defense} onChange={onChange('defense')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Poids" fullWidth value={form.weight} onChange={onChange('weight')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6}>
            <TextField
              select
              label="Emplacement"
              fullWidth
              value={form.slot}
              onChange={onChange('slot')}
              disabled={!isStaff}
            >
              {['main_hand', 'off_hand', 'both_hands'].map((v) => (
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
