import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Stepper,
    Step,
    StepLabel,
    StepContent,
    Typography,
    Box,
    Paper,
} from '@mui/material';
import {
    EmojiEvents,
    Explore,
    Build,
    Inventory,
} from '@mui/icons-material';

const tutorialSteps = [
    {
        label: 'Bienvenue dans le jeu de crafting ! 🎮',
        icon: <EmojiEvents />,
        description: (
            <>
                <Typography variant="body1" paragraph>
                    Bienvenue, aventurier ! Vous êtes sur le point de commencer une aventure épique de collecte et de fabrication.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Ce tutoriel vous guidera à travers les mécaniques de base du jeu.
                </Typography>
            </>
        ),
    },
    {
        label: 'Explorer la carte 🗺️',
        icon: <Explore />,
        description: (
            <>
                <Typography variant="body1" paragraph>
                    Utilisez l'onglet <strong>Carte</strong> pour explorer le monde. Chaque cellule contient des ressources différentes selon le biome.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    • Déplacez-vous avec les boutons directionnels<br />
                    • Collectez des ressources en cliquant sur les matériaux<br />
                    • Attention à votre énergie !
                </Typography>
            </>
        ),
    },
    {
        label: 'Collecter des ressources 📦',
        icon: <Inventory />,
        description: (
            <>
                <Typography variant="body1" paragraph>
                    Les ressources collectées apparaissent dans votre <strong>Inventaire</strong>. Vous pouvez les utiliser pour fabriquer des objets.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    • Consultez l'onglet Inventaire pour voir vos ressources<br />
                    • Certaines ressources sont comestibles et restaurent de l'énergie<br />
                    • Les matériaux ont différentes raretés
                </Typography>
            </>
        ),
    },
    {
        label: 'Fabriquer des objets 🔨',
        icon: <Build />,
        description: (
            <>
                <Typography variant="body1" paragraph>
                    Utilisez l'onglet <strong>Fabrication</strong> pour créer des outils, armes, et stations de travail.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    • Certaines recettes nécessitent des stations de travail<br />
                    • Fabriquez des outils pour collecter des ressources avancées<br />
                    • Gagnez de l'XP en craftant
                </Typography>
            </>
        ),
    },
    {
        label: 'Progresser et débloquer des talents 🌟',
        icon: <EmojiEvents />,
        description: (
            <>
                <Typography variant="body1" paragraph>
                    En collectant et en craftant, vous gagnez de l'XP et montez de niveau. Débloquez des talents pour devenir plus efficace !
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    • Consultez l'onglet Compétences pour voir votre progression<br />
                    • Les talents améliorent vos capacités<br />
                    • Le Dashboard affiche vos statistiques
                </Typography>
            </>
        ),
    },
];

function TutorialDialog({ open, onClose }) {
    const [activeStep, setActiveStep] = useState(0);

    const handleNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleFinish = () => {
        localStorage.setItem('tutorialCompleted', 'true');
        onClose();
    };

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                },
            }}
        >
            <DialogTitle sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <EmojiEvents sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h5" component="div" sx={{ fontWeight: 700 }}>
                        Guide du Débutant
                    </Typography>
                </Box>
            </DialogTitle>
            <DialogContent>
                <Stepper activeStep={activeStep} orientation="vertical">
                    {tutorialSteps.map((step, index) => (
                        <Step key={step.label}>
                            <StepLabel
                                StepIconComponent={() => (
                                    <Box
                                        sx={{
                                            width: 40,
                                            height: 40,
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            bgcolor: activeStep >= index ? 'primary.main' : 'grey.700',
                                            color: 'white',
                                            transition: 'all 0.3s',
                                        }}
                                    >
                                        {step.icon}
                                    </Box>
                                )}
                            >
                                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                    {step.label}
                                </Typography>
                            </StepLabel>
                            <StepContent>
                                <Paper
                                    elevation={0}
                                    sx={{
                                        p: 2,
                                        mt: 1,
                                        bgcolor: 'rgba(255, 255, 255, 0.05)',
                                        borderRadius: 2,
                                    }}
                                >
                                    {step.description}
                                </Paper>
                            </StepContent>
                        </Step>
                    ))}
                </Stepper>
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2 }}>
                <Button onClick={onClose} color="inherit">
                    Passer
                </Button>
                <Box sx={{ flex: '1 1 auto' }} />
                <Button disabled={activeStep === 0} onClick={handleBack}>
                    Précédent
                </Button>
                {activeStep === tutorialSteps.length - 1 ? (
                    <Button variant="contained" onClick={handleFinish}>
                        Terminer
                    </Button>
                ) : (
                    <Button variant="contained" onClick={handleNext}>
                        Suivant
                    </Button>
                )}
            </DialogActions>
        </Dialog>
    );
}

export default TutorialDialog;
