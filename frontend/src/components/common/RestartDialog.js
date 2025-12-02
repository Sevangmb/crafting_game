import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

function RestartDialog({ open, onClose, onConfirm }) {
    return (
        <Dialog
            open={open}
            onClose={onClose}
        >
            <DialogTitle>Recommencer la partie?</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Êtes-vous sûr de vouloir recommencer? Cela réinitialisera votre position,
                    votre inventaire et vos statistiques. Cette action est irréversible.
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Annuler
                </Button>
                <Button onClick={onConfirm} color="error" variant="contained">
                    Recommencer
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default RestartDialog;
