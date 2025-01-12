# ICBM Strategy Game with RNaD AI

A turn-based strategy game implementing DeepMind's RNaD (Regularized Nash Dynamics) algorithm, featuring fog of war mechanics, resource management, and strategic deployment.

## Project Goals

1. **RNaD AI Implementation**
   - Implement DeepMind's RNaD algorithm locally
   - Train models using GPU acceleration
   - Create AI opponent for strategic gameplay

2. **GUI Development**
   - Human-playable interface
   - Visual representation of 10x20 game board
   - Asset deployment and movement interface
   - Game state visualization

3. **API Development**
   - Enable AI vs Human gameplay
   - Game state management
   - Move validation and execution

## Game Overview

### Basic Mechanics
- 10x20 grid board (each player controls 10x10 area)
- 125 points for asset purchases
- 100 starting victory points
- 5 VP loss per turn
- Citadel destruction = instant 100 VP loss

### Asset Types
1. **Static Assets**
   - Citadel (0 pts, 3x3 visibility)
   - Launch Site (5 pts)

2. **Offensive Assets**
   - ICBM (5 pts, range 25, speed 4)
   - Cruise Missile (3 pts, range 25, speed 2)
   - Artillery (1 pt, range 5, speed 2)

3. **Defensive Assets**
   - Long Range Interceptor (8 pts, range 25, speed 4)
   - Short Range Interceptor (4 pts, range 8, speed 3)
   - Point Defense (2 pts, range 3, speed 3)

4. **Scouting Assets**
   - Recon Satellite (25 pts, range 25, speed 8)
   - Recon Plane (5 pts, range 25, speed 3)
   - Long Range Radar (20 pts, stationary, 5x5 vision)
   - Short Range Radar (10 pts, stationary, 3x3 vision)

### Key Rules
- Manhattan distance movement
- Units destroy each other upon occupying same tile
- Fog of war until scouted
- Mobile units must deploy from launch sites
- Revealed units stay visible until moved/destroyed

## Implementation Plan

1. Core Game Logic
   - State representation
   - Move validation
   - Combat resolution
   - Victory tracking

2. GUI Development
   - Game board visualization
   - Unit representation
   - Move input handling
   - State visualization

3. API Layer
   - Game state serialization
   - Move validation endpoints
   - State update handling

4. RNaD Implementation
   - Algorithm adaptation
   - Training infrastructure
   - Model integration

## Development Requirements
- Python 3.x
- GPU support for training
- Required packages TBD

## References
- ["Mastering the game of Stratego with model-free multiagent reinforcement learning"](https://www.science.org/doi/10.1126/science.add4679)
- Open source RNaD implementation

## Contributing
TBD

## License
TBD# ICBM-Game
