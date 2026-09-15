import type { Achievement, GroupRide, HazardReport, RideHistoryEntry, RiderProfile } from "../types";

export const defaultProfile: RiderProfile = {
  displayName: "Alex Rider",
  avatarEmoji: "🏍️",
  motorcycle: {
    make: "Triumph",
    model: "Tiger 900 Rally Pro",
    year: 2023,
    color: "Matte Khaki",
    engineSize: 888,
    fuelType: "petrol",
  },
  safetyContacts: [
    { id: "c1", name: "Jordan (Partner)", phone: "+1 (555) 019-2231", relationship: "Partner", notifyOnCrash: true, notifyOnRideStart: true },
    { id: "c2", name: "Sam (Riding Buddy)", phone: "+1 (555) 044-7789", relationship: "Friend", notifyOnCrash: true, notifyOnRideStart: false },
  ],
  preferences: {
    units: "metric",
    routeType: "scenic",
    avoidHighways: true,
    crashDetectionEnabled: true,
    crashDetectionSensitivity: "medium",
    sosCountdownSeconds: 30,
    showHazardAlerts: true,
  },
  memberSince: "2022-04-11",
};

export const seedHazards: HazardReport[] = [
  { id: "h1", type: "pothole", severity: "medium", description: "Deep pothole in the right lane after the bridge", distanceKm: 1.2, reportedAt: "12 min ago", verifiedCount: 6 },
  { id: "h2", type: "gravel", severity: "high", description: "Loose gravel spilled across both lanes on the switchback", distanceKm: 3.8, reportedAt: "34 min ago", verifiedCount: 11 },
  { id: "h3", type: "police", severity: "low", description: "Speed check near the county line", distanceKm: 6.4, reportedAt: "1 hr ago", verifiedCount: 3 },
  { id: "h4", type: "animals", severity: "high", description: "Deer crossing reported at dusk", distanceKm: 9.1, reportedAt: "2 hr ago", verifiedCount: 8 },
  { id: "h5", type: "construction", severity: "medium", description: "Single lane closure, flaggers on site", distanceKm: 14.5, reportedAt: "3 hr ago", verifiedCount: 4 },
];

export const seedAchievements: Achievement[] = [
  { id: "a1", name: "First Mile", description: "Complete your first tracked ride", icon: "🏁", tier: "bronze", progress: 1, target: 1, unlockedAt: "2022-04-12" },
  { id: "a2", name: "Century Club", description: "Ride 100 km in a single trip", icon: "💯", tier: "silver", progress: 100, target: 100, unlockedAt: "2022-06-02" },
  { id: "a3", name: "Switchback Master", description: "Clear 500 total curves", icon: "🌀", tier: "gold", progress: 412, target: 500 },
  { id: "a4", name: "Early Bird", description: "Start 10 rides before 7 AM", icon: "🌅", tier: "bronze", progress: 7, target: 10 },
  { id: "a5", name: "Iron Butt", description: "Log 1,000 km in a month", icon: "⚙️", tier: "platinum", progress: 640, target: 1000 },
  { id: "a6", name: "Safety First", description: "30 rides with zero hard-braking events", icon: "🛡️", tier: "silver", progress: 22, target: 30 },
];

export const seedGroupRides: GroupRide[] = [
  {
    id: "g1",
    name: "Sunday Canyon Blast",
    scheduledFor: "Sun, 8:00 AM",
    meetPoint: "Ridgeline Diner, Hwy 9",
    members: [
      { id: "m1", name: "You", avatarEmoji: "🏍️", role: "leader", isRiding: false },
      { id: "m2", name: "Sam", avatarEmoji: "🛵", role: "sweep", isRiding: false },
      { id: "m3", name: "Priya", avatarEmoji: "🏍️", role: "member", isRiding: false },
      { id: "m4", name: "Marcus", avatarEmoji: "🏍️", role: "member", isRiding: false },
    ],
    distanceKm: 142,
    status: "planning",
  },
  {
    id: "g2",
    name: "Coastal Sunset Cruise",
    scheduledFor: "Fri, 6:30 PM",
    meetPoint: "Pier 40 Overlook",
    members: [
      { id: "m1", name: "You", avatarEmoji: "🏍️", role: "member", isRiding: false },
      { id: "m5", name: "Dana", avatarEmoji: "🏍️", role: "leader", isRiding: false },
    ],
    distanceKm: 58,
    status: "planning",
  },
];

export const seedRideHistory: RideHistoryEntry[] = [
  { id: "r1", name: "Ridge Line Loop", date: "Yesterday", distanceKm: 86, durationSec: 6840, avgSpeed: 45, maxSpeed: 118, routeTag: "Scenic" },
  { id: "r2", name: "Commute — Downtown", date: "2 days ago", distanceKm: 14, durationSec: 1560, avgSpeed: 32, maxSpeed: 71, routeTag: "Daily" },
  { id: "r3", name: "Copper Canyon Run", date: "5 days ago", distanceKm: 132, durationSec: 10200, avgSpeed: 47, maxSpeed: 126, routeTag: "Curvy" },
  { id: "r4", name: "Coastal Serpentine", date: "1 week ago", distanceKm: 71, durationSec: 5580, avgSpeed: 46, maxSpeed: 109, routeTag: "Scenic" },
];

export const weeklyDistanceKm = [22, 0, 45, 18, 0, 86, 32];
