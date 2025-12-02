import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, MenuItem, Checkbox, FormControlLabel } from '@mui/material';
import { materialsAPI } from '../../services/api';
import IconUploadField from '../common/IconUploadField';

export default function MaterialEditDialog({ open, onClose, material, onSaved, isStaff }) {
  const [form, setForm] = useState({
    id: null,
    icon: '',
    name: '',
    rarity: 'common',
    category: 'divers',
    is_food: false,
    energy_restore: 0,
    is_equipment: false,
    equipment_slot: '',
    attack: 0,
    defense: 0,
    speed_bonus: 0,
    weight: 1,
    max_durability: 0,
    weight_capacity_bonus: 0,
    hunger_restore: 0,
    thirst_restore: 0,
    health_restore: 0,
    radiation_change: 0,
    description: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && material) {
      setForm({
        id: material.id,
        icon: material.icon || '',
        name: material.name || '',
        rarity: material.rarity || 'common',
        category: material.category || 'divers',
        is_food: !!material.is_food,
        energy_restore: material.energy_restore ?? 0,
        is_equipment: !!material.is_equipment,
        equipment_slot: material.equipment_slot || '',
        attack: material.attack ?? 0,
        defense: material.defense ?? 0,
        speed_bonus: material.speed_bonus ?? 0,
        weight: material.weight ?? 1,
        max_durability: material.max_durability ?? 0,
        weight_capacity_bonus: material.weight_capacity_bonus ?? 0,
        hunger_restore: material.hunger_restore ?? 0,
        thirst_restore: material.thirst_restore ?? 0,
        health_restore: material.health_restore ?? 0,
        radiation_change: material.radiation_change ?? 0,
        description: material.description || '',
      });
    }
  }, [open, material]);

  const onChange = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]:
        field === 'is_food' || field === 'is_equipment'
          ? e.target.checked
          : ['energy_restore', 'attack', 'defense', 'speed_bonus', 'weight', 'max_durability', 'weight_capacity_bonus', 'hunger_restore', 'thirst_restore', 'health_restore', 'radiation_change'].includes(field)
            ? Number(e.target.value)
            : e.target.value,
    }));
  const onIconChange = (value) => setForm((f) => ({ ...f, icon: value }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await materialsAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier le matériau</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <IconUploadField
              value={form.icon}
              onChange={onIconChange}
              disabled={!isStaff}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6}>
            <TextField select label="Rareté" fullWidth value={form.rarity} onChange={onChange('rarity')} disabled={!isStaff}>
              {['common', 'uncommon', 'rare', 'epic', 'legendary'].map((r) => (
                <MenuItem key={r} value={r}>{r}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={6}>
            <TextField select label="Catégorie" fullWidth value={form.category} onChange={onChange('category')} disabled={!isStaff}>
              {['minerais', 'bois', 'gemmes', 'magie', 'nourriture', 'divers'].map((c) => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={6}>
            <FormControlLabel
              control={<Checkbox checked={!!form.is_food} onChange={onChange('is_food')} disabled={!isStaff} />}
              label="Nourriture"
            />
          </Grid>
          <Grid item xs={6}>
            <TextField type="number" label="Énergie +" fullWidth value={form.energy_restore} onChange={onChange('energy_restore')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6}>
            <FormControlLabel
              control={<Checkbox checked={!!form.is_equipment} onChange={onChange('is_equipment')} disabled={!isStaff} />}
              label="Equipement"
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              select
              label="Slot"
              fullWidth
              value={form.equipment_slot || ''}
              onChange={onChange('equipment_slot')}
              disabled={!isStaff || !form.is_equipment}
            >
              {['head', 'chest', 'legs', 'feet', 'main_hand', 'off_hand', 'accessory'].map((s) => (
                <MenuItem key={s} value={s}>{s}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Attaque" fullWidth value={form.attack} onChange={onChange('attack')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Défense" fullWidth value={form.defense} onChange={onChange('defense')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Vitesse +" fullWidth value={form.speed_bonus} onChange={onChange('speed_bonus')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Poids" fullWidth value={form.weight} onChange={onChange('weight')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Durabilité max" fullWidth value={form.max_durability} onChange={onChange('max_durability')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Capacité sac +" fullWidth value={form.weight_capacity_bonus} onChange={onChange('weight_capacity_bonus')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Faim +" fullWidth value={form.hunger_restore} onChange={onChange('hunger_restore')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Soif +" fullWidth value={form.thirst_restore} onChange={onChange('thirst_restore')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={4}>
            <TextField type="number" label="Santé +" fullWidth value={form.health_restore} onChange={onChange('health_restore')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6}>
            <TextField type="number" label="Radiation" fullWidth value={form.radiation_change} onChange={onChange('radiation_change')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={12}>
            <TextField label="Description" fullWidth multiline minRows={2} value={form.description} onChange={onChange('description')} disabled={!isStaff} />
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
