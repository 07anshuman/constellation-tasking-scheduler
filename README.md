# 🛰️ Constellation Tasking Simulator

A realistic Earth Observation mission scheduler that simulates satellite tasking, visibility, weather filtering, energy and storage constraints. Designed for extensibility and realism.

## Features
- Real orbit propagation using Skyfield and TLEs
- Energy and data constraints modeled over time
- CSV logging of all simulation states
- Modular architecture (`core/` for models, `utils/` for helpers)

## How to Run

```bash
python main.py --scenario scenario.yaml --targets targets.yaml
