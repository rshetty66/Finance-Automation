# RideOut — Motorcycle Rider Companion

A mobile-first, installable web app for motorcycle riders: live ride tracking, AI-scored scenic
route discovery, crash detection with automatic SOS, hazard reporting, group rides, and rider
achievements — all in one dark, high-contrast dashboard built for glanceable use on a phone
mounted to your bars (or in your pocket).

Rebuilt from an incomplete React Native prototype into a single, fully working Progressive Web
App so it runs anywhere with a browser, installs to a phone home screen, and needs no native
build toolchain, simulator, or backend to try.

## Features

- **Dashboard** — weekly mileage chart, live weather strip, nearby hazards, next achievement, recent rides.
- **Ride Tracker** — start/pause/stop tracking with live speed, distance, duration and lean-angle readout. Uses the device's real GPS (`navigator.geolocation`) when available and permitted, and falls back to a smooth simulated ride so the flow is always demoable.
- **Scenic Routes** — a route-scoring engine (ported from the original app's curviness/scenic/difficulty algorithm) ranks generated routes by curve density, elevation variety, and points of interest, with a filterable list and a full route detail view (elevation profile, curve breakdown, highlights).
- **Safety & SOS** — crash-detection sensitivity controls, a manual SOS button, an emergency-contacts list, and a full-screen countdown overlay that mirrors what an automatic crash detection alert would look like.
- **Hazards** — nearby hazard feed with severity badges and a quick report form.
- **Group Rides** — upcoming rides, meet points, and rider rosters.
- **Achievements** — badge progress across bronze/silver/gold/platinum tiers.
- **Profile & Settings** — motorcycle info, safety contacts, units, route preferences.

Installable as a PWA (add to home screen) with offline asset caching via `vite-plugin-pwa`.

## Stack

React 19 + TypeScript + Vite, Tailwind CSS v4, Zustand (persisted to `localStorage`), React
Router, lucide-react icons. No backend required — all data is generated client-side or seeded
locally so the app is fully usable out of the box.

## Getting started

```bash
npm install
npm run dev      # start the dev server
npm run build    # type-check and produce a production build in dist/
npm run preview  # preview the production build
```

Open the app on your phone (same network, `npm run dev -- --host`) to test the mobile layout and
GPS tracking with real location data.
