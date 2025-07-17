# Constellation Scheduler

A modular, extensible Python package for simulating satellite constellation operations, including energy and data management, visibility, and scheduling. The project supports both programmatic (Python API), command-line, and web (FastAPI) interfaces, and outputs structured CSV and JSON logs for downstream analysis.


## Features

- **Satellite pass and visibility simulation** using TLEs and [Skyfield](https://rhodesmill.org/skyfield/)
- **Energy and data storage modeling** for each satellite
- **Configurable targets and ground stations** via YAML
- **Flexible scenario configuration** (start time, duration, timestep, min elevation, slew angle, etc.)
- **Priority-based target selection** and revisit interval enforcement
- **Slew angle modeling** with per-satellite attitude state and maximum slew constraint
- **Energy consumption per imaging, downlink, and idle**
- **Solar charging based on sunlit/shadow segments**
- **Lookahead energy awareness** (prevents actions that would starve future operations)
- **Storage capacity limit and task rejection on overflow**
- **Ground station modeling for downlink** with per-pass bandwidth
- **Outputs results as CSV and JSON** for further analysis
- **Python API, CLI, and FastAPI web interface** for flexible integration

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd constellation_schedular
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
   (Requires Python 3.8+)

---

## Usage

### Command Line

Run a simulation from the project root:
```bash
python main.py --scenario scenario.yaml --targets targets.yaml
```
- Outputs will be saved in the `outputs/` directory as CSV and JSON.

> **Note:** The `de421.bsp` ephemeris file is required for astronomical calculations. If it is not present, Skyfield will automatically download it the first time you run the simulation. You do not need to include this file in the repository.

### Python API

You can import and run simulations programmatically:
```python
from core.scheduler import run_simulation
from utils.config_loader import load_configs

start_time, duration, timestep, satellites, ground_stations, targets = load_configs()
scenario = {
    "start_time": start_time,
    "duration_minutes": duration.total_seconds() / 60,
    "timestep_sec": timestep,
    "satellites": satellites,
    "ground_stations": ground_stations,
}
run_simulation(scenario, targets, "outputs/simulation_log.csv")
```

### Web API (FastAPI)

Start the server:
```bash
uvicorn constellation_schedular.web:app --reload
```
- Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API docs.
- POST to `/simulate/` with scenario and targets as JSON.

---

## Configuration

- **Scenario:** See `scenario.yaml` for simulation parameters and satellite/ground station definitions.
- **Targets:** See `targets.yaml` for imaging targets, priorities, revisit intervals, etc.

---

## Testing

Run unit tests with:
```bash
pytest tests/
```

---

## Extending the Project

- Add new scheduling logic or constraints in `core/scheduler.py`.
- Add new satellite or data models in `core/satellite_model.py`, `core/energy_model.py`, or `core/data_model.py`.
- Integrate new data sources (e.g., cloud cover) via the `utils/` directory.

---

## Planned Features

- **Cloud cover integration:** Ability to ingest cloud fraction data from CSV or remote datasets (e.g., Copernicus/Sentinel) to affect imaging decisions.
- **More advanced scheduling policies and constraints.**
- **Visualization tools for simulation outputs.**

---

## License

MIT License. 