import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField } from '@mui/material';
import { vehicleTypesAPI } from '../../services/api';

export default function VehicleTypeEditDialog({ open, onClose, vehicleType, onSaved, isStaff }) {
  const [form, setForm] = useState({
    id: null,
    icon: '',
    name: '',
    carry_bonus: 0,
    speed_bonus: 0,
    energy_efficiency: 0,
    max_durability: 100,
    description: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && vehicleType) {
      setForm({
        id: vehicleType.id,
        icon: vehicleType.icon || '',
        name: vehicleType.name || '',
        carry_bonus: vehicleType.carry_bonus ?? 0,
        speed_bonus: vehicleType.speed_bonus ?? 0,
        energy_efficiency: vehicleType.energy_efficiency ?? 0,
        max_durability: vehicleType.max_durability ?? 100,
        description: vehicleType.description || '',
      });
    }
  }, [open, vehicleType]);

  const onChange = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: ['carry_bonus', 'speed_bonus', 'energy_efficiency', 'max_durability'].includes(field)
        ? Number(e.target.value)
        : e.target.value,
    }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await vehicleTypesAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier le véhicule</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField label="Icône" fullWidth value={form.icon} onChange={onChange('icon')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={8}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Capacité +" fullWidth value={form.carry_bonus} onChange={onChange('carry_bonus')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Vitesse +" fullWidth value={form.speed_bonus} onChange={onChange('speed_bonus')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Énergie %" fullWidth value={form.energy_efficiency} onChange={onChange('energy_efficiency')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Durabilité max" fullWidth value={form.max_durability} onChange={onChange('max_durability')} disabled={!isStaff} />
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
