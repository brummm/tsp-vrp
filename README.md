# Medical Route Optimization (Project 2)

This project implements a genetic algorithm to solve the Vehicle Routing Problem (VRP) for medical supplies distribution. It now includes a fully local LLM integration for generating driver instructions.

## Features

*   **VRP Solver:** Genetic Algorithm with Ordered Crossover (OX1) and Swap Mutation.
*   **Priority Handling:** Supports Critical, High, and Normal priority deliveries.
*   **Visualization:** Matplotlib-based route plotting.
*   **Local LLM Reporting:** Generates natural language route sheets using a local **Qwen2.5-3B-Instruct** model (no API key required).

## Structure

*   `src/algorithms/`: Genetic Algorithm logic.
*   `src/models/`: Data classes (Location, Vehicle).
*   `src/llm/`: LLM interface for report generation (uses `transformers` pipeline).
*   `notebooks/`: Demo notebook showing the full pipeline.

## Usage

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time you run the report generator, it will download the ~6GB LLM model.*

2.  Run the demo notebook:
    ```bash
    jupyter notebook notebooks/demo.ipynb
    ```

## Development

Run tests:
```bash
python -m unittest discover tests
```