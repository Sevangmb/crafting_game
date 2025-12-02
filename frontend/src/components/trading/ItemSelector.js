import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Avatar,
  IconButton,
  Badge,
  InputAdornment,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Search as SearchIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

const ItemSelector = ({
  inventory,
  selectedItems = [],
  onItemsChange,
  title = "Sélectionner des items",
  maxItems = 10
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [quantities, setQuantities] = useState({});

  // Filter inventory based on search
  const filteredInventory = inventory.filter(item =>
    item.material?.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Check if item is selected
  const isSelected = (materialId) => {
    return selectedItems.some(item => item.material_id === materialId);
  };

  // Get selected quantity for an item
  const getSelectedQuantity = (materialId) => {
    const selected = selectedItems.find(item => item.material_id === materialId);
    return selected ? selected.quantity : 0;
  };

  // Handle quantity change
  const handleQuantityChange = (materialId, newQuantity) => {
    const inventoryItem = inventory.find(item => item.material?.id === materialId);
    if (!inventoryItem) return;

    // Clamp between 0 and available quantity
    const clampedQuantity = Math.max(0, Math.min(newQuantity, inventoryItem.quantity));

    setQuantities(prev => ({
      ...prev,
      [materialId]: clampedQuantity
    }));
  };

  // Add item to selection
  const handleAddItem = (materialId) => {
    const inventoryItem = inventory.find(item => item.material?.id === materialId);
    if (!inventoryItem) return;

    const quantity = quantities[materialId] || 1;
    if (quantity <= 0) return;

    // Check if already selected
    if (isSelected(materialId)) {
      // Update quantity
      const updated = selectedItems.map(item =>
        item.material_id === materialId
          ? { ...item, quantity }
          : item
      );
      onItemsChange(updated);
    } else {
      // Check max items limit
      if (selectedItems.length >= maxItems) {
        return;
      }
      // Add new item
      onItemsChange([...selectedItems, { material_id: materialId, quantity }]);
    }

    // Reset quantity input
    setQuantities(prev => ({ ...prev, [materialId]: 1 }));
  };

  // Remove item from selection
  const handleRemoveItem = (materialId) => {
    onItemsChange(selectedItems.filter(item => item.material_id !== materialId));
  };

  // Get material details for selected items
  const getSelectedItemDetails = () => {
    return selectedItems.map(selected => {
      const inventoryItem = inventory.find(item => item.material?.id === selected.material_id);
      return {
        ...selected,
        material: inventoryItem?.material,
      };
    });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>

      {/* Selected Items Summary */}
      {selectedItems.length > 0 && (
        <Box mb={2}>
          <Typography variant="subtitle2" gutterBottom>
            Items sélectionnés ({selectedItems.length}/{maxItems})
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {getSelectedItemDetails().map((item) => (
              <Chip
                key={item.material_id}
                label={`${item.material?.icon || '📦'} ${item.material?.name || 'Item'} (${item.quantity})`}
                onDelete={() => handleRemoveItem(item.material_id)}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
          <Divider sx={{ mt: 2 }} />
        </Box>
      )}

      {/* Search */}
      <TextField
        fullWidth
        size="small"
        placeholder="Rechercher un item..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: searchQuery && (
            <InputAdornment position="end">
              <IconButton size="small" onClick={() => setSearchQuery('')}>
                <CloseIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{ mb: 2 }}
      />

      {/* Inventory Grid */}
      <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
        <Grid container spacing={1}>
          {filteredInventory.length === 0 && (
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                {searchQuery ? 'Aucun item trouvé' : 'Inventaire vide'}
              </Typography>
            </Grid>
          )}

          {filteredInventory.map((item) => {
            const materialId = item.material?.id;
            const selected = isSelected(materialId);
            const currentQuantity = quantities[materialId] || 1;

            return (
              <Grid item xs={12} sm={6} md={4} key={item.id}>
                <Card
                  sx={{
                    border: selected ? 2 : 0,
                    borderColor: 'primary.main',
                    bgcolor: selected ? 'action.selected' : 'background.paper',
                  }}
                >
                  <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Badge
                        badgeContent={item.quantity}
                        color="secondary"
                        max={999}
                      >
                        <Avatar
                          sx={{
                            bgcolor: 'primary.main',
                            width: 40,
                            height: 40,
                            fontSize: '1.5rem',
                          }}
                        >
                          {item.material?.icon || '📦'}
                        </Avatar>
                      </Badge>
                      <Box flex={1} minWidth={0}>
                        <Typography variant="body2" fontWeight="bold" noWrap>
                          {item.material?.name || 'Item'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Disponible: {item.quantity}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Quantity Selector */}
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(materialId, currentQuantity - 1)}
                        disabled={currentQuantity <= 1}
                      >
                        <RemoveIcon fontSize="small" />
                      </IconButton>

                      <TextField
                        size="small"
                        type="number"
                        value={currentQuantity}
                        onChange={(e) => handleQuantityChange(materialId, parseInt(e.target.value) || 1)}
                        inputProps={{
                          min: 1,
                          max: item.quantity,
                          style: { textAlign: 'center', padding: '4px' }
                        }}
                        sx={{ width: 60 }}
                      />

                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(materialId, currentQuantity + 1)}
                        disabled={currentQuantity >= item.quantity}
                      >
                        <AddIcon fontSize="small" />
                      </IconButton>

                      <Button
                        size="small"
                        variant={selected ? "outlined" : "contained"}
                        onClick={() => selected ? handleRemoveItem(materialId) : handleAddItem(materialId)}
                        disabled={!selected && selectedItems.length >= maxItems}
                        sx={{ ml: 'auto' }}
                      >
                        {selected ? 'Retirer' : 'Ajouter'}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Box>

      {selectedItems.length >= maxItems && (
        <Typography variant="caption" color="warning.main" display="block" mt={1}>
          Limite de {maxItems} items atteinte
        </Typography>
      )}
    </Box>
  );
};

export default ItemSelector;
