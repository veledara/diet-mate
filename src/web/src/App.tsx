import React from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AnalyticsPage from "./pages/AnalyticsPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import AchievementsPage from "./pages/AchievementsPage";
import SettingsPage from "./pages/SettingsPage";
import { BottomNav } from "./components/BottomNav/BottomNav";

const App: React.FC = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/achievements" element={<AchievementsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>

      <BottomNav />
    </div>
  );
};

export default App;
