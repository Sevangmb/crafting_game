import React from 'react';
import {
    Box,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Checkbox,
    Typography,
    Chip,
    Tooltip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function CraftingFilters({
    globalSearch,
    setGlobalSearch,
    rarityFilter,
    setRarityFilter,
    workstationFilter,
    setWorkstationFilter,
    energyFilter,
    setEnergyFilter,
    craftableOnly,
    setCraftableOnly,
    hasAllIngredients,
    setHasAllIngredients,
    allWorkstations,
    filteredCount,
    showFilters
}) {
    return (
        <Box>
            {/* Barre de recherche compacte */}
            <Box sx={{ mt: 1 }}>
                <TextField
                    fullWidth
                    size="small"
                    placeholder="Rechercher des recettes..."
                    value={globalSearch}
                    onChange={(e) => setGlobalSearch(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                />
            </Box>

            {/* Filtres compacts */}
            {showFilters && (
                <Box sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 1,
                    mt: 1,
                    alignItems: 'center'
                }}>
                    <FormControl size="small" sx={{ minWidth: 100 }}>
                        <InputLabel>Rareté</InputLabel>
                        <Select
                            value={rarityFilter}
                            label="Rareté"
                            onChange={(e) => setRarityFilter(e.target.value)}
                        >
                            <MenuItem value="all">Toutes</MenuItem>
                            <MenuItem value="common">Commune</MenuItem>
                            <MenuItem value="uncommon">Peu commune</MenuItem>
                            <MenuItem value="rare">Rare</MenuItem>
                            <MenuItem value="epic">Épique</MenuItem>
                            <MenuItem value="legendary">Légendaire</MenuItem>
                            <MenuItem value="mythic">Mythique</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Station</InputLabel>
                        <Select
                            value={workstationFilter}
                            label="Station"
                            onChange={(e) => setWorkstationFilter(e.target.value)}
                        >
                            <MenuItem value="all">Toutes</MenuItem>
                            <MenuItem value="none">Aucune</MenuItem>
                            {allWorkstations.map((ws) => (
                                <MenuItem key={ws.id} value={ws.id}>
                                    {ws.icon} {ws.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 110 }}>
                        <InputLabel>Énergie</InputLabel>
                        <Select
                            value={energyFilter}
                            label="Énergie"
                            onChange={(e) => setEnergyFilter(e.target.value)}
                        >
                            <MenuItem value="all">Tous</MenuItem>
                            <MenuItem value="affordable">Abordable</MenuItem>
                            <MenuItem value="expensive">Cher</MenuItem>
                        </Select>
                    </FormControl>

                    <Box sx={{
                        display: 'flex',
                        flexDirection: { xs: 'column', sm: 'row' },
                        gap: 1,
                        alignItems: 'flex-start',
                        width: { xs: '100%', sm: 'auto' }
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, width: { xs: '100%', sm: 'auto' } }}>
                            <Tooltip title="Craftable seulement (station + énergie)">
                                <Checkbox
                                    checked={craftableOnly}
                                    onChange={(e) => setCraftableOnly(e.target.checked)}
                                    size="small"
                                />
                            </Tooltip>
                            <Typography variant="caption" color="text.secondary" sx={{ minWidth: 'fit-content' }}>
                                Craftable
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, width: { xs: '100%', sm: 'auto' } }}>
                            <Tooltip title="Tous les ingrédients disponibles">
                                <Checkbox
                                    checked={hasAllIngredients}
                                    onChange={(e) => setHasAllIngredients(e.target.checked)}
                                    size="small"
                                />
                            </Tooltip>
                            <Typography variant="caption" color="text.secondary" sx={{ minWidth: 'fit-content' }}>
                                Ingrédients OK
                            </Typography>
                        </Box>
                    </Box>

                    <Chip
                        label={`${filteredCount} recette${filteredCount > 1 ? 's' : ''}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                    />
                </Box>
            )}
        </Box>
    );
}

export default CraftingFilters;
