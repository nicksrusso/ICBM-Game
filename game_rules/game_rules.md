# ICBM Strategy Game Rules

## Overview
- Military strategy game where players buy and deploy assets
- Goal: Destroy enemy citadel while defending your own
- Two players: Red and Blue
- Each player starts with 125 purchase points
- Game begins with secret deployment phase

## Scoring
- Players start with 100 victory points
- Game ends when a player reaches 0 victory points
- 5 victory points lost per turn (turns cannot be passed)
- Citadel destruction = instant 100 point loss and game over
- Objective: Reduce opponent's points while preserving yours

## Board
- 10x20 grid layout
- Each player controls 10x10 deployment area

## Turn Structure
1. Players alternate turns
2. During turn:
   - Launch offensive/defensive assets
   - Launch scouting assets
   - Move assets (manhattan distance up to speed value)
   - "Pilot" mobile assets to reachable tiles
3. Turn ends after chosen policies
4. Resolution sequence:
   - Move assets
   - Resolve combat
   - Reveal scouting results
   - Switch to opponent

## Combat Rules
- Assets destroy each other if ending turn on same tile
- Offensive assets destroy launch sites and deployed assets when reaching site

## Scouting
- Assets within visibility range are "seen"
- Seen assets remain visible until moved/destroyed
- Mobile scouts (satellite/plane) have 0 visibility until launched

## Asset Types

### Static Assets
- **Citadel**: Home base (free, required)
- **Launch Site**: Required for mobile asset launches

### Offensive Assets
- **ICBM**: Long range missile
- **Cruise Missile**: Medium range, slower
- **Artillery**: Short range, economical

### Defensive Assets
- **Long Range Interceptor**: Fast, long range
- **Short Range Interceptor**: Medium range
- **Point Defense**: Very short range

### Scouting Assets
- **Recon Satellite**: Fast, expensive
- **Recon Plane**: Slower, cheaper
- **Long Range Radar**: Static, long range
- **Short Range Radar**: Static, short range

## Game Phases

### Deployment Phase
1. Secret purchasing and deployment
2. Mobile assets must deploy to launch sites
3. Static assets cannot share locations
4. Multiple mobile assets can share launch site

### Game Phase
1. Initial scouting reveal
2. Players take turns executing policies
3. Continue until victory condition met