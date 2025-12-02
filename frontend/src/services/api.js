import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle 401 errors and clear token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and authentication state
      localStorage.removeItem('token');
      // Don't force redirect - let React handle the state change
      // This prevents the refresh loop
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) =>
    axios.post(`${API_BASE_URL}/auth/login/`, { username, password }),
};

export const playerAPI = {
  getMe: () => api.get('/players/me/'),
  move: (playerId, direction) => api.post(`/players/${playerId}/move/`, { direction }),
  restart: () => api.post('/players/restart/'),
};

export const materialsAPI = {
  getAll: () => api.get('/materials/'),
  create: (data) => api.post('/materials/', data),
  update: (id, data) => api.put(`/materials/${id}/`, data),
  delete: (id) => api.delete(`/materials/${id}/`),
};

export const recipesAPI = {
  getAll: () => api.get('/recipes/'),
  getDuplicates: () => api.get('/recipes/duplicates/'),
  deleteDuplicates: () => api.post('/recipes/delete_duplicates/'),
  create: (data) => api.post('/recipes/', data),
  update: (id, data) => api.put(`/recipes/${id}/`, data),
  delete: (id) => api.delete(`/recipes/${id}/`),
};

export const inventoryAPI = {
  getAll: () => api.get('/inventory/'),
  consume: (inventoryId) => api.post('/inventory/consume/', { inventory_id: inventoryId }),
  drop: (inventoryId, quantity = 1) => api.post('/inventory/drop/', { inventory_id: inventoryId, quantity }),
  pickup: (droppedItemId) => api.post('/inventory/pickup/', { dropped_item_id: droppedItemId }),
};

export const mapAPI = {
  getCurrentCell: () => api.get('/map/current/'),
  getCell: (cellId) => api.get(`/map/${cellId}/`),
  gather: (cellId, materialId) => api.post(`/map/${cellId}/gather/`, { material_id: materialId }),
  scavenge: () => api.post('/map/scavenge/'),
  getWorldState: () => api.get('/map/world_state/'),
};

export const vehicleAPI = {
  getAll: () => api.get('/vehicles/'),
  equip: (vehicleId) => api.post(`/vehicles/${vehicleId}/equip/`),
  unequip: () => api.post('/vehicles/unequip/'),
};

export const craftingAPI = {
  craft: (recipeId, quantity = 1) => api.post('/crafting/craft/', { recipe_id: recipeId, quantity }),
  repairTool: (materialId) => api.post('/crafting/repair_tool/', { material_id: materialId }),
  installWorkstation: (materialId) => api.post('/crafting/install_workstation/', { material_id: materialId }),
};

export const workstationAPI = {
  getAll: () => api.get('/workstations/'),
  getPlayerWorkstations: () => api.get('/player-workstations/'),
  create: (data) => api.post('/workstations/', data),
  update: (id, data) => api.put(`/workstations/${id}/`, data),
  delete: (id) => api.delete(`/workstations/${id}/`),
};

export const recipeIngredientsAPI = {
  getAll: () => api.get('/recipe-ingredients/'),
  create: (data) => api.post('/recipe-ingredients/', data),
  update: (id, data) => api.put(`/recipe-ingredients/${id}/`, data),
  delete: (id) => api.delete(`/recipe-ingredients/${id}/`),
};

export const configAPI = {
  getAll: () => api.get('/config/'),
  getAllConfigs: () => api.get('/config/all_configs/'),
  get: (key) => api.get(`/config/${key}/`),
  create: (data) => api.post('/config/', data),
  update: (id, data) => api.put(`/config/${id}/`, data),
  delete: (id) => api.delete(`/config/${id}/`),
};

export const skillsAPI = {
  getPlayerSkills: () => api.get('/players/skills/'),
  getSkillsTree: () => api.get('/players/skills_tree/'),
};

export const buildingAPI = {
  getTypes: () => api.get('/building-types/'),
  getAvailable: () => api.get('/building-types/available/'),
  getMyBuildings: () => api.get('/buildings/my_buildings/'),
  construct: (buildingTypeId, cellId) => api.post('/buildings/construct/', { building_type_id: buildingTypeId, cell_id: cellId }),
  complete: (buildingId) => api.post(`/buildings/${buildingId}/complete/`),
  getBonuses: () => api.get('/buildings/bonuses/'),
};

export const combatAPI = {
  searchForMob: () => api.post('/combat/search/'),
  startCombat: (mobId = null) => api.post('/combat/start/', { mob_id: mobId }),
  executeCombatAction: (combatState, action) => api.post('/combat/action/', { combat_state: combatState, action }),
  getCombatHistory: (limit = 10) => api.get(`/combat/history/?limit=${limit}`),
};

export const poiAPI = {
  getCurrentPOIs: () => api.get('/poi/current-pois/'),
  getMenu: (poiType) => api.get(`/poi/menu/${poiType}/`),
  purchase: (poiType, materialId, quantity = 1) => api.post('/poi/purchase/', { poi_type: poiType, material_id: materialId, quantity }),
  sell: (poiType, materialId, quantity = 1) => api.post('/poi/sell/', { poi_type: poiType, material_id: materialId, quantity }),
  getSellPrice: (poiType, materialId) => api.post('/poi/get-sell-price/', { poi_type: poiType, material_id: materialId }),
};

// Admin resources
export const mobsAPI = {
  getAll: () => api.get('/mobs/'),
  create: (data) => api.post('/mobs/', data),
  update: (id, data) => api.put(`/mobs/${id}/`, data),
  delete: (id) => api.delete(`/mobs/${id}/`),
};

export const vehicleTypesAPI = {
  getAll: () => api.get('/vehicle-types/'),
  create: (data) => api.post('/vehicle-types/', data),
  update: (id, data) => api.put(`/vehicle-types/${id}/`, data),
  delete: (id) => api.delete(`/vehicle-types/${id}/`),
};

export const weaponsAPI = {
  getAll: () => api.get('/weapons/'),
  create: (data) => api.post('/weapons/', data),
  update: (id, data) => api.put(`/weapons/${id}/`, data),
  delete: (id) => api.delete(`/weapons/${id}/`),
};

export const clothingAPI = {
  getAll: () => api.get('/clothing/'),
  create: (data) => api.post('/clothing/', data),
  update: (id, data) => api.put(`/clothing/${id}/`, data),
  delete: (id) => api.delete(`/clothing/${id}/`),
};

export const achievementsAPI = {
  getAll: () => api.get('/achievements/'),
  getProgress: () => api.get('/achievements/my_progress/'),
  getRecent: () => api.get('/achievements/recent/'),
};

export const shopAPI = {
  getAll: () => api.get('/shops/'),
  getItems: (shopId) => api.get(`/shops/${shopId}/items/`),
  buyItem: (shopId, itemId, quantity, useCard = false) => api.post(`/shops/${shopId}/buy/`, { item_id: itemId, quantity, use_card: useCard }),
  sellItem: (shopId, materialId, quantity) => api.post(`/shops/sell/`, { shop_id: shopId, material_id: materialId, quantity }),
};

export const transactionAPI = {
  getAll: () => api.get('/transactions/'),
  getRecent: (limit = 10) => api.get(`/transactions/recent/?limit=${limit}`),
};

export const bankAPI = {
  getCurrentBanks: () => api.get('/banks/current/'),
  deposit: (bankId, amount) => api.post('/banks/deposit/', { bank_id: bankId, amount }),
  withdraw: (bankId, amount) => api.post('/banks/withdraw/', { bank_id: bankId, amount }),
};

export const equipmentAPI = {
  getAll: () => api.get('/equipment/'),
  equip: (materialId, slot) => api.post('/equipment/equip/', { material_id: materialId, slot }),
  unequip: (slot) => api.post('/equipment/unequip/', { slot }),
};

// Quest System API
export const questsAPI = {
  getAll: () => api.get('/quests/'),
  getAvailable: () => api.get('/quests/available/'),
  getActive: () => api.get('/quests/active/'),
  getCompleted: () => api.get('/quests/completed/'),
  accept: (questId) => api.post(`/quests/${questId}/accept/`),
  abandon: (questId) => api.post(`/quests/${questId}/abandon/`),
  getStats: () => api.get('/quests/stats/'),
};

// Trading System API
export const tradingAPI = {
  createOffer: (toPlayerId, offeredItems, offeredMoney, requestedItems, requestedMoney, message = '', durationHours = 24) =>
    api.post('/trades/create_offer/', {
      to_player_id: toPlayerId,
      offered_items: offeredItems,
      offered_money: offeredMoney,
      requested_items: requestedItems,
      requested_money: requestedMoney,
      message,
      duration_hours: durationHours
    }),
  getReceived: () => api.get('/trades/received/'),
  getSent: () => api.get('/trades/sent/'),
  getHistory: (limit = 50) => api.get(`/trades/history/?limit=${limit}`),
  accept: (tradeId) => api.post(`/trades/${tradeId}/accept/`),
  reject: (tradeId) => api.post(`/trades/${tradeId}/reject/`),
  cancel: (tradeId) => api.post(`/trades/${tradeId}/cancel/`),
  getStats: () => api.get('/trades/stats/'),
};

// Leaderboard System API
export const leaderboardAPI = {
  getAll: (category = null, limit = 100) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (limit) params.append('limit', limit);
    return api.get(`/leaderboards/?${params.toString()}`);
  },
  getCategories: () => api.get('/leaderboards/categories/'),
  getByCategory: (limit = 10) => api.get(`/leaderboards/by_category/?limit=${limit}`),
  getMyRanks: () => api.get('/leaderboards/my_ranks/'),
  getTopPlayers: () => api.get('/leaderboards/top_players/'),
  getPlayerRank: (playerId, category) => api.get(`/leaderboards/player_rank/?player_id=${playerId}&category=${category}`),
  updateAll: () => api.post('/leaderboards/update_all/'),
  updateCategory: (category) => api.post('/leaderboards/update_category/', { category }),
};

// Dynamic Events API
export const eventsAPI = {
  getAll: (eventType = null, isActive = true) => {
    const params = new URLSearchParams();
    if (eventType) params.append('event_type', eventType);
    if (isActive !== null) params.append('is_active', isActive);
    return api.get(`/events/?${params.toString()}`);
  },
  getNearby: (radius = 10) => api.get(`/events/nearby/?radius=${radius}`),
  participate: (eventId) => api.post(`/events/${eventId}/participate/`),
  spawn: (eventType = null, count = 1) => api.post('/events/spawn/', { event_type: eventType, count }),
  cleanup: () => api.post('/events/cleanup/'),
};

// Encounter API
export const encounterAPI = {
  getCurrent: () => api.get('/encounters/current/'),
  attack: () => api.post('/encounters/attack/'),
  flee: () => api.post('/encounters/flee/'),
};

export default api;

