import React, { useEffect, useMemo, useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, TextField, Grid, MenuItem } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { materialsAPI, workstationAPI, recipesAPI, recipeIngredientsAPI } from '../../services/api';

export default function RecipeEditDialog({ open, onClose, recipeId, onSaved, isStaff }) {
  const [loading, setLoading] = useState(false);
  const [materials, setMaterials] = useState([]);
  const [workstations, setWorkstations] = useState([]);
  const [recipe, setRecipe] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [selIng, setSelIng] = useState([]);

  const loadLookups = async () => {
    const [m, w] = await Promise.all([materialsAPI.getAll(), workstationAPI.getAll()]);
    setMaterials(m.data || []);
    setWorkstations(w.data || []);
  };

  const loadRecipe = async (id) => {
    setLoading(true);
    try {
      const [r, ings] = await Promise.all([
        recipesAPI.getAll(),
        recipeIngredientsAPI.getAll(),
      ]);
      const rec = (r.data || []).find((x) => x.id === id) || null;
      setRecipe(rec);
      setIngredients((ings.data || []).filter((i) => i.recipe === id || i.recipe?.id === id));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && recipeId) {
      loadLookups();
      loadRecipe(recipeId);
    }
  }, [open, recipeId]);

  const materialOptions = useMemo(() => materials.map((m) => ({ value: m.id, label: m.name })), [materials]);
  const workstationOptions = useMemo(() => workstations.map((w) => ({ value: w.id, label: w.name })), [workstations]);
  const materialById = useMemo(() => Object.fromEntries(materials.map((m) => [m.id, m])), [materials]);

  const handleChange = (field) => (e) => {
    setRecipe((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSave = async () => {
    if (!isStaff || !recipe) return;
    const payload = {
      name: recipe.name,
      description: recipe.description || '',
      icon: recipe.icon || '',
      result_material_id: recipe.result_material_id || recipe.result_material?.id,
      result_quantity: Number(recipe.result_quantity) || 1,
      required_workstation_id: recipe.required_workstation_id ?? (recipe.required_workstation?.id || null),
    };
    await recipesAPI.update(recipe.id, payload);
    if (onSaved) onSaved();
    onClose();
  };

  const addIngredient = async () => {
    if (!isStaff || !recipe) return;
    const defaultMat = materials[0]?.id;
    if (!defaultMat) return;
    await recipeIngredientsAPI.create({ recipe: recipe.id, material: defaultMat, quantity: 1 });
    await loadRecipe(recipe.id);
  };

  const deleteIngredients = async () => {
    if (!isStaff || !selIng.length) return;
    for (const id of selIng) await recipeIngredientsAPI.delete(id);
    await loadRecipe(recipeId);
    setSelIng([]);
  };

  const ingColumns = useMemo(() => [
    { field: 'id', headerName: 'ID', width: 80 },
    {
      field: 'material',
      headerName: 'Matériau',
      flex: 1,
      minWidth: 220,
      editable: true,
      type: 'singleSelect',
      valueOptions: materialOptions,
      valueGetter: (v, row) => row.material?.id ?? row.material, // ensure field value is an id
      valueFormatter: (params) => materialById[params.value]?.name || params.value,
      renderCell: (params) => {
        const mat = materialById[params.value] || materialById[params.row.material?.id] || materialById[params.row.material];
        return <span>{mat?.icon ? `${mat.icon} ` : ''}{mat?.name || params.value}</span>;
      },
    },
    { field: 'quantity', headerName: 'Quantité', width: 120, editable: true, type: 'number' },
  ], [materialOptions, materialById]);

  const processIngUpdate = async (newRow, oldRow) => {
    try {
      const payload = {
        recipe: recipe.id,
        material: newRow.material?.id || newRow.material,
        quantity: Number(newRow.quantity) || 1,
      };
      await recipeIngredientsAPI.update(newRow.id, payload);
      return newRow;
    } catch (e) {
      console.error(e);
      return oldRow;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Modifier la recette</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField label="Nom" fullWidth value={recipe?.name || ''} onChange={handleChange('name')} disabled={!isStaff} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField label="Icône" fullWidth value={recipe?.icon || ''} onChange={handleChange('icon')} disabled={!isStaff} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField select label="Matériau résultat" fullWidth value={(recipe?.result_material_id) || (recipe?.result_material?.id) || ''} onChange={(e) => setRecipe((r) => ({ ...r, result_material_id: Number(e.target.value) }))} disabled={!isStaff}>
                {materialOptions.map((opt) => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField type="number" label="Quantité" fullWidth value={recipe?.result_quantity || 1} onChange={handleChange('result_quantity')} disabled={!isStaff} />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField select label="Station requise" fullWidth value={(recipe?.required_workstation_id) || (recipe?.required_workstation?.id) || ''} onChange={(e) => setRecipe((r) => ({ ...r, required_workstation_id: e.target.value ? Number(e.target.value) : null }))} disabled={!isStaff}>
                <MenuItem value="">Aucune</MenuItem>
                {workstationOptions.map((opt) => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField label="Description" fullWidth multiline minRows={2} value={recipe?.description || ''} onChange={handleChange('description')} disabled={!isStaff} />
            </Grid>
          </Grid>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Box component="span" sx={{ fontWeight: 600 }}>Ingrédients</Box>
          <Box>
            <Button variant="contained" size="small" onClick={addIngredient} disabled={!isStaff} sx={{ mr: 1 }}>+ Ajouter</Button>
            <Button variant="outlined" color="error" size="small" onClick={deleteIngredients} disabled={!isStaff || selIng.length === 0}>Supprimer</Button>
          </Box>
        </Box>
        <div style={{ height: 360, width: '100%' }}>
          <DataGrid
            rows={ingredients}
            columns={ingColumns}
            loading={loading}
            checkboxSelection
            disableRowSelectionOnClick
            onRowSelectionModelChange={(m) => setSelIng(m)}
            processRowUpdate={processIngUpdate}
            onProcessRowUpdateError={(e) => console.error(e)}
            editMode="row"
            hideFooter
          />
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button onClick={handleSave} variant="contained" disabled={!isStaff || !recipe}>Enregistrer</Button>
      </DialogActions>
    </Dialog>
  );
}
