import React, { useState } from 'react';
import { Box, TextField, Typography, Button, CircularProgress } from '@mui/material';
import axios from 'axios';

/**
 * Reusable icon upload field component
 * Supports both emoji input and image paste (Ctrl+V)
 */
const IconUploadField = ({ value, onChange, disabled = false, label = "Icône" }) => {
    const [uploading, setUploading] = useState(false);
    const [imagePreview, setImagePreview] = useState(
        value && (value.startsWith('http') || value.startsWith('/media')) ? value : null
    );

    const uploadImage = async (blob) => {
        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('image', blob, 'icon.png');

            const token = localStorage.getItem('token');
            const response = await axios.post('http://127.0.0.1:8000/api/upload/icon/', formData, {
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'multipart/form-data',
                },
            });

            return response.data.url;
        } catch (error) {
            console.error('Upload failed:', error);
            alert('Échec du téléchargement de l\'image');
            return null;
        } finally {
            setUploading(false);
        }
    };

    const handlePaste = async (e) => {
        const items = e.clipboardData?.items;
        if (!items) return;

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                e.preventDefault();
                const blob = items[i].getAsFile();

                // Show preview immediately
                const reader = new FileReader();
                reader.onload = (event) => {
                    setImagePreview(event.target.result);
                };
                reader.readAsDataURL(blob);

                // Upload to server
                const url = await uploadImage(blob);
                if (url) {
                    onChange(url);
                    setImagePreview(url);
                }
                break;
            }
        }
    };

    const handleChange = (e) => {
        const newValue = e.target.value;
        onChange(newValue);
        // Clear image preview if user types text
        if (!newValue.startsWith('http') && !newValue.startsWith('/media')) {
            setImagePreview(null);
        }
    };

    const clearImage = () => {
        onChange('');
        setImagePreview(null);
    };

    return (
        <Box>
            <Typography variant="caption" color="text.secondary" gutterBottom>
                {label} (emoji ou image - Ctrl+V pour coller une capture d'écran)
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                    fullWidth
                    value={imagePreview ? '🖼️ Image téléchargée' : value}
                    onChange={handleChange}
                    onPaste={handlePaste}
                    disabled={disabled || imagePreview || uploading}
                    placeholder="Collez une image ou tapez un emoji"
                />
                {uploading && <CircularProgress size={24} />}
                {imagePreview && !uploading && (
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <img
                            src={imagePreview}
                            alt="Preview"
                            style={{ width: 40, height: 40, objectFit: 'contain', border: '1px solid #ccc', borderRadius: 4 }}
                        />
                        <Button size="small" onClick={clearImage} disabled={disabled}>
                            Supprimer
                        </Button>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default IconUploadField;
