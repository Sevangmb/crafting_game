import React from 'react';
import {
    Box,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    IconButton,
    Tooltip,
    Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';

function InventoryFilters({
    searchTerm,
    setSearchTerm,
    categoryFilter,
    setCategoryFilter,
    rarityFilter,
    setRarityFilter,
    sortBy,
    setSortBy,
    viewMode,
    setViewMode,
    showFilters,
    setShowFilters,
    categories,
    totalItems
}) {
    return (
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box sx={{
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                alignItems: { xs: 'stretch', sm: 'center' },
                justifyContent: 'space-between',
                gap: 2
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                    <TextField
                        fullWidth
                        size="small"
                        placeholder="Rechercher un objet..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <SearchIcon />
                                </InputAdornment>
                            ),
                        }}
                        sx={{ maxWidth: 400 }}
                    />
                    <Chip
                        label={`${totalItems} objets`}
                        color="primary"
                        variant="outlined"
                        size="small"
                        sx={{ display: { xs: 'none', sm: 'flex' } }}
                    />
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Basculer les filtres">
                        <IconButton
                            onClick={() => setShowFilters(!showFilters)}
                            color={showFilters ? 'primary' : 'default'}
                        >
                            <FilterListIcon />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={viewMode === 'grid' ? "Vue liste" : "Vue grille"}>
                        <IconButton onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}>
                            {viewMode === 'grid' ? <ViewListIcon /> : <ViewModuleIcon />}
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {showFilters && (
                <Box sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 2,
                    mt: 2,
                    pt: 2,
                    borderTop: 1,
                    borderColor: 'divider'
                }}>
                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Catégorie</InputLabel>
                        <Select
                            value={categoryFilter}
                            label="Catégorie"
                            onChange={(e) => setCategoryFilter(e.target.value)}
                        >
                            <MenuItem value="all">Toutes</MenuItem>
                            {categories.map(cat => (
                                <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 150 }}>
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
                        </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel>Trier par</InputLabel>
                        <Select
                            value={sortBy}
                            label="Trier par"
                            onChange={(e) => setSortBy(e.target.value)}
                        >
                            <MenuItem value="name">Nom</MenuItem>
                            <MenuItem value="quantity">Quantité</MenuItem>
                            <MenuItem value="rarity">Rareté</MenuItem>
                            <MenuItem value="recent">Récent</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            )}
        </Box>
    );
}

export default InventoryFilters;
