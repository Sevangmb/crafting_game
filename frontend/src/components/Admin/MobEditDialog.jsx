import React, { useEffect, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, MenuItem } from '@mui/material';
import { mobsAPI } from '../../services/api';

export default function MobEditDialog({ open, onClose, mob, onSaved, isStaff }) {
  const [form, setForm] = useState({
    id: null,
    icon: '',
    name: '',
    level: 1,
    health: 20,
    attack: 5,
    defense: 0,
    xp_reward: 10,
    aggression_level: 'neutral',
    spawn_rate: 0.3,
    biomes_json: '[]',
    loot_table_json: '{}',
    description: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && mob) {
      setForm({
        id: mob.id,
        icon: mob.icon || '',
        name: mob.name || '',
        level: mob.level ?? 1,
        health: mob.health ?? 20,
        attack: mob.attack ?? 5,
        defense: mob.defense ?? 0,
        xp_reward: mob.xp_reward ?? 10,
        aggression_level: mob.aggression_level || 'neutral',
        spawn_rate: mob.spawn_rate ?? 0.3,
        biomes_json: mob.biomes_json || '[]',
        loot_table_json: mob.loot_table_json || '{}',
        description: mob.description || '',
      });
    }
  }, [open, mob]);

  const onChange = (field) => (e) =>
    setForm((f) => ({
      ...f,
      [field]: ['level', 'health', 'attack', 'defense', 'xp_reward', 'spawn_rate'].includes(field)
        ? Number(e.target.value)
        : e.target.value,
    }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await mobsAPI.update(form.id, form);
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier l'animal</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField label="Icône" fullWidth value={form.icon} onChange={onChange('icon')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={8}>
            <TextField label="Nom" fullWidth value={form.name} onChange={onChange('name')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Niveau" fullWidth value={form.level} onChange={onChange('level')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="PV" fullWidth value={form.health} onChange={onChange('health')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Attaque" fullWidth value={form.attack} onChange={onChange('attack')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Défense" fullWidth value={form.defense} onChange={onChange('defense')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="XP" fullWidth value={form.xp_reward} onChange={onChange('xp_reward')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField type="number" label="Taux apparition" fullWidth value={form.spawn_rate} onChange={onChange('spawn_rate')} disabled={!isStaff} />
          </Grid>
          <Grid item xs={6} sm={3}>
            <TextField
              select
              label="Agressivité"
              fullWidth
              value={form.aggression_level}
              onChange={onChange('aggression_level')}
              disabled={!isStaff}
            >
              {['passive', 'neutral', 'aggressive'].map((v) => (
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
          <Grid item xs={12}>
            <TextField
              label="Biomes (JSON)"
              fullWidth
              multiline
              minRows={2}
              value={form.biomes_json}
              onChange={onChange('biomes_json')}
              disabled={!isStaff}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Loot (JSON)"
              fullWidth
              multiline
              minRows={2}
              value={form.loot_table_json}
              onChange={onChange('loot_table_json')}
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
