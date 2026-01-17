# Medical Route Optimization (Project 2)

This project implements a genetic algorithm to solve the Vehicle Routing Problem (VRP) for medical supplies distribution. It includes an integration with LLMs to generate natural language driver instructions.

## Features

*   **VRP Solver:** Genetic Algorithm with Ordered Crossover (OX1) and Swap Mutation.
*   **Priority Handling:** Supports Critical, High, and Normal priority deliveries.
*   **Visualization:** Matplotlib-based route plotting.
*   **LLM Reporting:** Generates route sheets using OpenAI (or a built-in mock simulator).

## Structure

*   `src/algorithms/`: Genetic Algorithm logic.
*   `src/models/`: Data classes (Location, Vehicle).
*   `src/llm/`: LLM interface for report generation.
*   `notebooks/`: Demo notebook showing the full pipeline.

## Usage

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the demo notebook:
    ```bash
    jupyter notebook notebooks/demo.ipynb
    ```

3.  (Optional) Set OpenAI Key:
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

## Development

Run tests:
```bash
python -m unittest discover tests
```
