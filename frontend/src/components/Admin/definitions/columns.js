import React from 'react';
import { Button } from '@mui/material';

export const getMaterialColumns = (setEditMatRow, setEditMatOpen) => [
  { field: 'id', headerName: 'ID', width: 80, editable: false },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'rarity', headerName: 'Rareté', width: 140, editable: true, type: 'singleSelect', valueOptions: [
    { value: 'common', label: 'common' },
    { value: 'uncommon', label: 'uncommon' },
    { value: 'rare', label: 'rare' },
    { value: 'epic', label: 'epic' },
    { value: 'legendary', label: 'legendary' }
  ] },
  { field: 'category', headerName: 'Catégorie', width: 140, editable: true, type: 'singleSelect', valueOptions: [
    { value: 'minerais', label: 'minerais' },
    { value: 'bois', label: 'bois' },
    { value: 'gemmes', label: 'gemmes' },
    { value: 'magie', label: 'magie' },
    { value: 'nourriture', label: 'nourriture' },
    { value: 'divers', label: 'divers' }
  ] },
  { field: 'is_food', headerName: 'Nourriture', width: 120, type: 'boolean', editable: true },
  { field: 'energy_restore', headerName: 'Énergie +', width: 120, type: 'number', editable: true },
  { field: 'is_equipment', headerName: 'Equipement', width: 120, type: 'boolean', editable: true },
  { field: 'equipment_slot', headerName: 'Slot', width: 140, editable: true, type: 'singleSelect', valueOptions: [
    { value: 'head', label: 'head' },
    { value: 'chest', label: 'chest' },
    { value: 'legs', label: 'legs' },
    { value: 'feet', label: 'feet' },
    { value: 'main_hand', label: 'main_hand' },
    { value: 'off_hand', label: 'off_hand' },
    { value: 'accessory', label: 'accessory' },
  ] },
  { field: 'attack', headerName: 'Attaque', width: 110, type: 'number', editable: true },
  { field: 'defense', headerName: 'Défense', width: 110, type: 'number', editable: true },
  { field: 'speed_bonus', headerName: 'Vitesse +', width: 120, type: 'number', editable: true },
  { field: 'weight', headerName: 'Poids', width: 110, type: 'number', editable: true },
  { field: 'max_durability', headerName: 'Durabilité max', width: 140, type: 'number', editable: true },
  { field: 'weight_capacity_bonus', headerName: 'Capacité sac +', width: 150, type: 'number', editable: true },
  { field: 'hunger_restore', headerName: 'Faim +', width: 110, type: 'number', editable: true },
  { field: 'thirst_restore', headerName: 'Soif +', width: 110, type: 'number', editable: true },
  { field: 'health_restore', headerName: 'Santé +', width: 110, type: 'number', editable: true },
  { field: 'radiation_change', headerName: 'Radiation', width: 120, type: 'number', editable: true },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 220, editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditMatRow(params.row); setEditMatOpen(true); }}>Modifier</Button>
    )
  },
];

export const getWorkstationColumns = (setEditWsRow, setEditWsOpen) => [
  { field: 'id', headerName: 'ID', width: 80, editable: false },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 220, editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditWsRow(params.row); setEditWsOpen(true); }}>Modifier</Button>
    )
  },
];

export const getRecipeColumns = (materials, workstations, setEditId, setEditOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 220, editable: true },
  {
    field: 'result_material_id',
    headerName: 'Matériau résultat',
    width: 220,
    editable: true,
    type: 'singleSelect',
    valueOptions: (materials || []).map((m) => ({ value: m.id, label: m.name })),
    valueGetter: (v, row) => row.result_material?.id ?? row.result_material_id,
    valueFormatter: (params) => {
      if (!params) return '';
      const val = params.value;
      const m = (materials || []).find((x) => x.id === val);
      return (m?.icon ? `${m.icon} ` : '') + (m?.name || (val ?? ''));
    },
    renderCell: (params) => {
      if (!params) return null;
      const val = params.value ?? params.row?.result_material?.id ?? params.row?.result_material_id;
      const m = (materials || []).find((x) => x.id === val);
      return <span>{m?.icon ? `${m.icon} ` : ''}{m?.name || (val ?? '')}</span>;
    },
  },
  { field: 'result_quantity', headerName: 'Qté', width: 100, type: 'number', editable: true },
  {
    field: 'required_workstation_id',
    headerName: 'Station requise',
    width: 220,
    editable: true,
    type: 'singleSelect',
    valueOptions: (workstations || []).map((w) => ({ value: w.id, label: w.name })),
    valueGetter: (v, row) => row.required_workstation?.id ?? row.required_workstation_id,
    valueFormatter: (params) => {
      if (!params) return '';
      const val = params.value;
      const w = (workstations || []).find((x) => x.id === val);
      return (w?.icon ? `${w.icon} ` : '') + (w?.name || (val ?? ''));
    },
  },
  { field: 'icon', headerName: 'Icône', width: 100, editable: true },
  { field: 'actions', headerName: 'Actions', width: 120, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditId(params.row.id); setEditOpen(true); }}>Modifier</Button>
    )
  },
];

export const getIngredientColumns = (recipes, materials, setEditIngRow, setEditIngOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  {
    field: 'recipe',
    headerName: 'Recette',
    flex: 1,
    minWidth: 220,
    editable: true,
    type: 'singleSelect',
    valueOptions: (recipes || []).map((r) => ({ value: r.id, label: r.name })),
    valueGetter: (v, row) => row.recipe?.id ?? row.recipe,
    valueFormatter: (params) => {
      const r = (recipes || []).find((x) => x.id === params.value);
      return r?.name || params.value;
    },
  },
  {
    field: 'material',
    headerName: 'Matériau',
    flex: 1,
    minWidth: 220,
    editable: true,
    type: 'singleSelect',
    valueOptions: (materials || []).map((m) => ({ value: m.id, label: m.name })),
    valueGetter: (v, row) => row.material?.id ?? row.material,
    valueFormatter: (params) => {
      const m = (materials || []).find((x) => x.id === params.value);
      return (m?.icon ? `${m.icon} ` : '') + (m?.name || params.value);
    },
    renderCell: (params) => {
      const m = (materials || []).find((x) => x.id === (params.value ?? params.row.material?.id ?? params.row.material));
      return <span>{m?.icon ? `${m.icon} ` : ''}{m?.name || params.value}</span>;
    },
  },
  { field: 'quantity', headerName: 'Quantité', width: 120, type: 'number', editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditIngRow(params.row); setEditIngOpen(true); }}>Modifier</Button>
    )
  },
];

export const getMobColumns = (setEditMobRow, setEditMobOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'level', headerName: 'Niveau', width: 110, type: 'number', editable: true },
  { field: 'health', headerName: 'PV', width: 110, type: 'number', editable: true },
  { field: 'attack', headerName: 'Attaque', width: 110, type: 'number', editable: true },
  { field: 'defense', headerName: 'Défense', width: 110, type: 'number', editable: true },
  { field: 'xp_reward', headerName: 'XP', width: 110, type: 'number', editable: true },
  { field: 'aggression_level', headerName: 'Agressivité', width: 140, editable: true },
  { field: 'spawn_rate', headerName: 'Taux apparition', width: 150, type: 'number', editable: true },
  { field: 'biomes_json', headerName: 'Biomes (JSON)', flex: 1, minWidth: 200, editable: true },
  { field: 'loot_table_json', headerName: 'Loot (JSON)', flex: 1, minWidth: 220, editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditMobRow(params.row); setEditMobOpen(true); }}>Modifier</Button>
    )
  },
];

export const getWeaponColumns = (setEditWeaponRow, setEditWeaponOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'attack', headerName: 'Attaque', width: 120, type: 'number', editable: true },
  { field: 'defense', headerName: 'Défense', width: 120, type: 'number', editable: true },
  { field: 'weight', headerName: 'Poids', width: 120, type: 'number', editable: true },
  { field: 'slot', headerName: 'Emplacement', width: 150, editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditWeaponRow(params.row); setEditWeaponOpen(true); }}>Modifier</Button>
    )
  },
];

export const getClothingColumns = (setEditClothingRow, setEditClothingOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'defense', headerName: 'Défense', width: 120, type: 'number', editable: true },
  { field: 'weight', headerName: 'Poids', width: 120, type: 'number', editable: true },
  { field: 'slot', headerName: 'Emplacement', width: 150, editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditClothingRow(params.row); setEditClothingOpen(true); }}>Modifier</Button>
    )
  },
];

export const getVehicleTypeColumns = (setEditVehicleTypeRow, setEditVehicleTypeOpen) => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90, editable: true },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 180, editable: true },
  { field: 'carry_bonus', headerName: 'Capacité +', width: 140, type: 'number', editable: true },
  { field: 'speed_bonus', headerName: 'Vitesse +', width: 140, type: 'number', editable: true },
  { field: 'energy_efficiency', headerName: 'Énergie %', width: 140, type: 'number', editable: true },
  { field: 'max_durability', headerName: 'Durabilité max', width: 160, type: 'number', editable: true },
  { field: 'actions', headerName: 'Actions', width: 140, sortable: false, filterable: false, disableColumnMenu: true,
    renderCell: (params) => (
      <Button size="small" onClick={() => { setEditVehicleTypeRow(params.row); setEditVehicleTypeOpen(true); }}>Modifier</Button>
    )
  },
];

export const getConfigColumns = () => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'key', headerName: 'Clé', flex: 1, minWidth: 200, editable: true },
  { field: 'value', headerName: 'Valeur (JSON)', flex: 1, minWidth: 260, editable: true },
  { field: 'description', headerName: 'Description', flex: 1, minWidth: 220, editable: true },
];

export const getAchievementColumns = () => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90 },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 200 },
  { field: 'category', headerName: 'Catégorie', width: 140 },
  { field: 'requirement_type', headerName: 'Type', width: 160 },
  { field: 'requirement_value', headerName: 'Valeur', width: 120, type: 'number' },
  { field: 'requirement_target', headerName: 'Cible', width: 200 },
  { field: 'reward_xp', headerName: 'XP', width: 110, type: 'number' },
  { field: 'hidden', headerName: 'Caché', width: 100, type: 'boolean' },
];

export const getBuildingTypeColumns = () => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'icon', headerName: 'Icône', width: 90 },
  { field: 'name', headerName: 'Nom', flex: 1, minWidth: 200 },
  { field: 'category', headerName: 'Catégorie', width: 140 },
  { field: 'required_level', headerName: 'Niveau requis', width: 140, type: 'number' },
  { field: 'construction_time', headerName: 'Temps constr.', width: 140, type: 'number' },
  { field: 'energy_regeneration_bonus', headerName: 'Regen énergie', width: 150, type: 'number' },
  { field: 'storage_bonus', headerName: 'Stockage +', width: 130, type: 'number' },
];

export const getBuildingsColumns = () => [
  { field: 'id', headerName: 'ID', width: 80 },
  { field: 'building_type_name', headerName: 'Type', flex: 1, minWidth: 200, valueGetter: (v, row) => row.building_type?.name ?? row.building_type_name },
  { field: 'status', headerName: 'Statut', width: 140 },
  { field: 'construction_progress', headerName: 'Progression', width: 140, type: 'number' },
  { field: 'cell_info', headerName: 'Cellule', flex: 1, minWidth: 180, valueGetter: (v, row) => row.cell_info ? `(${row.cell_info.grid_x}, ${row.cell_info.grid_y}) - ${row.cell_info.biome}` : '' },
];
