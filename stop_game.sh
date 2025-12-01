#!/bin/bash

echo "========================================"
echo "  Arrêt des serveurs du jeu"
echo "========================================"
echo ""

# Arrêter les processus Django
echo "Arrêt du backend Django..."
pkill -f "manage.py runserver"
if [ $? -eq 0 ]; then
    echo "  [OK] Backend arrêté"
else
    echo "  [INFO] Aucun processus Django en cours"
fi

echo ""

# Arrêter les processus Node/React
echo "Arrêt du frontend React..."
pkill -f "react-scripts start"
if [ $? -eq 0 ]; then
    echo "  [OK] Frontend arrêté"
else
    echo "  [INFO] Aucun processus React en cours"
fi

echo ""
echo "========================================"
echo "  Serveurs arrêtés avec succès!"
echo "========================================"
echo ""
