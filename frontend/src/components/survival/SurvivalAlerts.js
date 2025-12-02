import React, { useEffect } from 'react';
import { Alert, Box, Collapse } from '@mui/material';
import { Restaurant, WaterDrop, Favorite, FitnessCenter, Science } from '@mui/icons-material';

const SurvivalAlerts = ({ player }) => {
    const [alerts, setAlerts] = React.useState([]);

    useEffect(() => {
        if (!player) return;

        const newAlerts = [];

        // Critical health
        if (player.health <= 20) {
            newAlerts.push({
                severity: 'error',
                icon: <Favorite />,
                message: `Santé critique: ${player.health}/${player.max_health} - Vous devez vous soigner immédiatement!`
            });
        } else if (player.health <= 50) {
            newAlerts.push({
                severity: 'warning',
                icon: <Favorite />,
                message: `Santé basse: ${player.health}/${player.max_health} - Pensez à vous soigner.`
            });
        }

        // Critical hunger
        if (player.hunger === 0) {
            newAlerts.push({
                severity: 'error',
                icon: <Restaurant />,
                message: 'Vous mourez de faim! Vous perdez de la santé!'
            });
        } else if (player.hunger < 20) {
            newAlerts.push({
                severity: 'error',
                icon: <Restaurant />,
                message: `Faim critique: ${player.hunger}/${player.max_hunger} - Trouvez de la nourriture rapidement!`
            });
        } else if (player.hunger < 30) {
            newAlerts.push({
                severity: 'warning',
                icon: <Restaurant />,
                message: `Vous avez faim: ${player.hunger}/${player.max_hunger} - Les actions coûtent 50% d'énergie en plus.`
            });
        }

        // Critical thirst
        if (player.thirst === 0) {
            newAlerts.push({
                severity: 'error',
                icon: <WaterDrop />,
                message: 'Vous mourez de soif! Vous perdez de la santé!'
            });
        } else if (player.thirst < 10) {
            newAlerts.push({
                severity: 'error',
                icon: <WaterDrop />,
                message: `Soif critique: ${player.thirst}/${player.max_thirst} - Trouvez de l'eau immédiatement!`
            });
        } else if (player.thirst < 20) {
            newAlerts.push({
                severity: 'warning',
                icon: <WaterDrop />,
                message: `Vous avez soif: ${player.thirst}/${player.max_thirst} - Les actions coûtent 50% d'énergie en plus.`
            });
        }

        // Radiation warning
        if (player.radiation > 80) {
            newAlerts.push({
                severity: 'error',
                icon: <Science />,
                message: `Radiation mortelle: ${player.radiation}/100 - Évacuez la zone et prenez des anti-radiations!`
            });
        } else if (player.radiation > 50) {
            newAlerts.push({
                severity: 'warning',
                icon: <Science />,
                message: `Radiation dangereuse: ${player.radiation}/100 - Vous subissez des dégâts de radiation.`
            });
        }

        // Overencumbered
        if (player.is_overencumbered) {
            newAlerts.push({
                severity: 'error',
                icon: <FitnessCenter />,
                message: `Surchargé! ${player.current_carry_weight?.toFixed(1)}kg / ${player.effective_carry_capacity?.toFixed(1)}kg - Vous ne pouvez pas vous déplacer!`
            });
        } else if (player.current_carry_weight / player.effective_carry_capacity > 0.8) {
            newAlerts.push({
                severity: 'warning',
                icon: <FitnessCenter />,
                message: `Inventaire presque plein: ${player.current_carry_weight?.toFixed(1)}kg / ${player.effective_carry_capacity?.toFixed(1)}kg`
            });
        }

        // Low energy
        if (player.energy < 10) {
            newAlerts.push({
                severity: 'warning',
                icon: <Favorite />,
                message: `Énergie très basse: ${player.energy}/${player.max_energy} - Reposez-vous ou consommez de la nourriture.`
            });
        }

        setAlerts(newAlerts);
    }, [player]);

    if (alerts.length === 0) return null;

    return (
        <Box sx={{ mb: 2 }}>
            {alerts.map((alert, index) => (
                <Collapse key={index} in={true}>
                    <Alert
                        severity={alert.severity}
                        icon={alert.icon}
                        sx={{ mb: 1 }}
                    >
                        {alert.message}
                    </Alert>
                </Collapse>
            ))}
        </Box>
    );
};

export default SurvivalAlerts;
