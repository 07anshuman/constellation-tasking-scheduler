from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from core.scheduler import run_simulation

app = FastAPI()

class SimulationRequest(BaseModel):
    scenario: Dict[str, Any]
    targets: List[Dict[str, Any]]
    output_path: str = "outputs/api_simulation.csv"

@app.post("/simulate/")
def simulate_endpoint(req: SimulationRequest):
    run_simulation(req.scenario, req.targets, req.output_path)
    # Optionally, you can read and return the JSON output
    json_path = req.output_path.replace('.csv', '.json')
    with open(json_path) as jf:
        results = jf.read()
    return {"status": "ok", "output": req.output_path, "results": results}