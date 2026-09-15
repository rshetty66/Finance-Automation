import { HashRouter, Route, Routes } from "react-router-dom";
import { BottomNav } from "./components/BottomNav";
import { DashboardScreen } from "./screens/DashboardScreen";
import { RideTrackingScreen } from "./screens/RideTrackingScreen";
import { ScenicRoutesScreen } from "./screens/ScenicRoutesScreen";
import { SafetyScreen } from "./screens/SafetyScreen";
import { ProfileScreen } from "./screens/ProfileScreen";
import { HazardsScreen } from "./screens/HazardsScreen";
import { GroupRidesScreen } from "./screens/GroupRidesScreen";
import { AchievementsScreen } from "./screens/AchievementsScreen";
import { RideHistoryScreen } from "./screens/RideHistoryScreen";
import { CrashOverlay } from "./screens/CrashOverlay";

export default function App() {
  return (
    <HashRouter>
      <div className="min-h-dvh bg-[var(--color-bg)] text-[var(--color-ink)]">
        <div className="mx-auto max-w-md pb-24">
          <Routes>
            <Route path="/" element={<DashboardScreen />} />
            <Route path="/ride" element={<RideTrackingScreen />} />
            <Route path="/routes" element={<ScenicRoutesScreen />} />
            <Route path="/safety" element={<SafetyScreen />} />
            <Route path="/profile" element={<ProfileScreen />} />
            <Route path="/hazards" element={<HazardsScreen />} />
            <Route path="/group-rides" element={<GroupRidesScreen />} />
            <Route path="/achievements" element={<AchievementsScreen />} />
            <Route path="/history" element={<RideHistoryScreen />} />
          </Routes>
        </div>
        <BottomNav />
        <CrashOverlay />
      </div>
    </HashRouter>
  );
}
