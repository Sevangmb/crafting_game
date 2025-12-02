import React from 'react';
import { Snackbar, Alert, Slide } from '@mui/material';

function SlideTransition(props) {
    return <Slide {...props} direction="up" />;
}

function NotificationToast({ open, message, severity = 'info', onClose, autoHideDuration = 4000 }) {
    return (
        <Snackbar
            open={open}
            autoHideDuration={autoHideDuration}
            onClose={onClose}
            TransitionComponent={SlideTransition}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
            <Alert
                onClose={onClose}
                severity={severity}
                variant="filled"
                sx={{ width: '100%', boxShadow: 3 }}
            >
                {message}
            </Alert>
        </Snackbar>
    );
}

export default NotificationToast;
