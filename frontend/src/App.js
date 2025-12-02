import React, { useMemo } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import Login from './components/Login';
import AdminDialog from './components/Admin/AdminDialog';
import NotificationManager from './components/NotificationManager';
import TutorialDialog from './components/TutorialDialog';
import RestartDialog from './components/common/RestartDialog';
import GameLayout from './components/layout/GameLayout';
import theme from './theme';
import { useGameStore, selectPlayer, selectInventory, selectCurrentTab } from './stores/useGameStore';
import { useSkills, useGameData, useAuth, useGameActions } from './hooks';
import { groupInventory } from './utils/inventoryUtils';

// Import Tab Components
import InventoryTab from './components/tabs/InventoryTab';
import CraftingTab from './components/tabs/CraftingTab';
import MapTab from './components/tabs/MapTab';
import DashboardTab from './components/tabs/DashboardTab';
import SkillsTab from './components/tabs/SkillsTab';
import RecipeGraphTab from './components/tabs/RecipeGraphTab';
import CharacterTab from './components/tabs/CharacterTab';
import BuildingTab from './components/tabs/BuildingTab';
import AchievementsTab from './components/tabs/AchievementsTab';
import ShopTab from './components/tabs/ShopTab';
import QuestsTab from './components/tabs/QuestsTab';
import TradingTab from './components/tabs/TradingTab';
import LeaderboardTab from './components/tabs/LeaderboardTab';


function App() {
  // Store state
  const player = useGameStore(selectPlayer);
  const rawInventory = useGameStore(selectInventory);
  const inventory = useMemo(() => rawInventory || [], [rawInventory]);
  const currentTab = useGameStore(selectCurrentTab);
  const setCurrentTab = useGameStore((state) => state.setCurrentTab);
  const setCurrentCell = useGameStore((state) => state.setCurrentCell);

  // Custom Hooks
  const { isAuthenticated, login, logout } = useAuth();
  const { restartDialogOpen, openRestartDialog, closeRestartDialog, restartGame } = useGameActions();
  const { craftingLevel, craftingXp, talents, tree } = useSkills();
  const { fetchPlayerData, refreshInventory } = useGameData();

  const [adminOpen, setAdminOpen] = React.useState(false);
  const [tutorialOpen, setTutorialOpen] = React.useState(() => {
    return !localStorage.getItem('tutorialCompleted');
  });

  // Memoized inventory - wrap inventory in useMemo to prevent dependency issues
  const memoizedInventory = useMemo(() => inventory, [inventory]);
  const groupedInventory = useMemo(() => groupInventory(memoizedInventory), [memoizedInventory]);

  const handlePlayerUpdate = (updatedPlayer) => {
    useGameStore.getState().setPlayer(updatedPlayer);
  };

  const handleCellUpdate = (updatedCell) => {
    setCurrentCell(updatedCell);
  };

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={login} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <GameLayout
        player={player}
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        onOpenAdmin={() => setAdminOpen(true)}
        onRestart={openRestartDialog}
        onLogout={logout}
      >
        {currentTab === 0 && <InventoryTab groupedInventory={groupedInventory} onConsume={fetchPlayerData} />}
        {currentTab === 1 && <CraftingTab inventory={inventory} onCraft={refreshInventory} />}
        {currentTab === 2 && <CharacterTab />}
        {currentTab === 3 && (
          <MapTab
            player={player}
            onPlayerUpdate={handlePlayerUpdate}
            onGather={refreshInventory}
            onCellUpdate={handleCellUpdate}
          />
        )}
        {currentTab === 4 && <BuildingTab onRefresh={refreshInventory} />}
        {currentTab === 5 && <DashboardTab />}
        {currentTab === 6 && (
          <SkillsTab
            craftingLevel={craftingLevel}
            craftingXp={craftingXp}
            talents={talents}
            tree={tree}
          />
        )}
        {currentTab === 7 && <RecipeGraphTab />}
        {currentTab === 8 && <AchievementsTab />}
        {currentTab === 9 && <ShopTab />}
        {currentTab === 10 && <QuestsTab />}
        {currentTab === 11 && <TradingTab />}
        {currentTab === 12 && <LeaderboardTab />}
      </GameLayout>

      <RestartDialog
        open={restartDialogOpen}
        onClose={closeRestartDialog}
        onConfirm={restartGame}
      />

      <AdminDialog open={adminOpen} onClose={() => setAdminOpen(false)} isStaff={!!player?.is_staff} />

      <TutorialDialog open={tutorialOpen} onClose={() => setTutorialOpen(false)} />

      <NotificationManager />
    </ThemeProvider>
  );
}

export default App;
