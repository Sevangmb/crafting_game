import React, { useEffect, useMemo, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Grid, TextField, MenuItem } from '@mui/material';
import { materialsAPI, recipesAPI, recipeIngredientsAPI } from '../../services/api';

export default function IngredientEditDialog({ open, onClose, ingredient, onSaved, isStaff }) {
  const [loading, setLoading] = useState(false);
  const [materials, setMaterials] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [form, setForm] = useState({ id: null, recipe: '', material: '', quantity: 1 });

  useEffect(() => {
    if (open) {
      Promise.all([materialsAPI.getAll(), recipesAPI.getAll()]).then(([m, r]) => {
        setMaterials(m.data || []);
        setRecipes(r.data || []);
      });
    }
  }, [open]);

  useEffect(() => {
    if (open && ingredient) {
      setForm({
        id: ingredient.id,
        recipe: ingredient.recipe?.id ?? ingredient.recipe ?? '',
        material: ingredient.material?.id ?? ingredient.material ?? '',
        quantity: ingredient.quantity ?? 1,
      });
    }
  }, [open, ingredient]);

  const onChange = (field) => (e) => setForm((f) => ({ ...f, [field]: field === 'quantity' ? Number(e.target.value) : e.target.value }));

  const save = async () => {
    if (!isStaff) return;
    setLoading(true);
    try {
      await recipeIngredientsAPI.update(form.id, {
        recipe: form.recipe,
        material: form.material,
        quantity: Number(form.quantity) || 1,
      });
      if (onSaved) onSaved();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const materialOptions = useMemo(() => materials.map((m) => ({ value: m.id, label: `${m.icon ? m.icon + ' ' : ''}${m.name}` })), [materials]);
  const recipeOptions = useMemo(() => recipes.map((r) => ({ value: r.id, label: r.name })), [recipes]);

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Modifier l'ingrédient</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField select fullWidth label="Recette" value={form.recipe} onChange={onChange('recipe')} disabled={!isStaff}>
              {recipeOptions.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <TextField select fullWidth label="Matériau" value={form.material} onChange={onChange('material')} disabled={!isStaff}>
              {materialOptions.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <TextField type="number" fullWidth label="Quantité" value={form.quantity} onChange={onChange('quantity')} disabled={!isStaff} />
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
