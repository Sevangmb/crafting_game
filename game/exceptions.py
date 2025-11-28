"""
Custom exceptions for the game
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class InsufficientEnergyError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Pas assez d'énergie pour effectuer cette action."
    default_code = 'insufficient_energy'


class InsufficientMaterialsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Matériaux insuffisants pour cette recette."
    default_code = 'insufficient_materials'


class InvalidDirectionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Direction invalide. Utilisez: north, south, east, west."
    default_code = 'invalid_direction'


class WaterBlockedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Impossible de se déplacer sur une case d'eau."
    default_code = 'water_blocked'


class ItemNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Objet non trouvé dans l'inventaire."
    default_code = 'item_not_found'


class NotEquipmentError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cet objet ne peut pas être équipé."
    default_code = 'not_equipment'


class InvalidEquipmentSlotError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Emplacement d'équipement invalide."
    default_code = 'invalid_equipment_slot'


class WorkstationRequiredError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cette recette nécessite une station de travail."
    default_code = 'workstation_required'

    def __init__(self, workstation_name):
        detail = f"Cette recette nécessite: {workstation_name}"
        super().__init__(detail=detail)


class MaterialDepletedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ce matériau est épuisé sur cette case."
    default_code = 'material_depleted'


class NotFoodError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cet objet ne peut pas être consommé."
    default_code = 'not_food'


class FullEnergyError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Votre énergie est déjà au maximum."
    default_code = 'full_energy'


class InvalidActionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Action invalide."
    default_code = 'invalid_action'


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Ressource introuvable."
    default_code = 'not_found'


class GameException(APIException):
    """Generic game exception"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Une erreur de jeu s'est produite."
    default_code = 'game_error'

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
