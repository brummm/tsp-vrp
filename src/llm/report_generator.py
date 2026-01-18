import os
from typing import List
from src.models.location import Location

# Try importing transformers
try:
    from transformers import pipeline
except ImportError:
    pipeline = None

class ReportGenerator:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        self.pipe = None
        if pipeline:
            try:
                print(f"Loading local model: {model_name}...")
                # device_map="auto" will use GPU/MPS if available.
                self.pipe = pipeline("text-generation", model=model_name, device_map="auto")
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Failed to load local model {model_name}: {e}")
                pass

    def generate_driver_instructions(self, route_idx: int, route: List[Location]) -> str:
        """
        Generates natural language instructions for a driver using a local LLM.
        """
        # Create a clear, bulleted string of the raw data
        stops_block = "\n".join([f"{i+1}. {loc.name} (Priority: {loc.priority})" for i, loc in enumerate(route)])
        
        # System prompt: Define a persona that is strict about data integrity
        system_content = (
            "You are a Logistics Dispatcher. Write a friendly message to the driver.\n"
            "STRUCTURE:\n"
            "1. Greeting.\n"
            "2. The Route List (You MUST list stops EXACTLY as provided in raw data. Copy them line-by-line. Do not miss any).\n"
            "3. Closing/Safety tip."
        )

        user_content = (
            f"Driver ID: {route_idx+1}\n"
            f"Raw Route Data:\n{stops_block}\n\n"
            "Please generate the full Route Sheet."
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        if self.pipe:
            try:
                outputs = self.pipe(
                    messages, 
                    max_new_tokens=512, # Allow enough space for the full list
                    do_sample=True, 
                    temperature=0.3,    # Low temp for accuracy
                    top_p=0.9
                )
                return outputs[0]["generated_text"][-1]["content"]
            except Exception as e:
                print(f"Generation error: {e}")
                return self._mock_instructions(route_idx, route)
        else:
            return self._mock_instructions(route_idx, route)

    def _mock_instructions(self, route_idx: int, route: List[Location]) -> str:
        lines = [f"*** ROUTE PLAN (SIMULATED LLM OUTPUT) FOR DRIVER {route_idx + 1} ***"]
        lines.append("Good morning! Here is your optimized delivery route for today.")
        lines.append("")
        lines.append("1. 🏭 DEPART from Central Depot.")
        for i, loc in enumerate(route):
            prio_icon = "🔴" if loc.priority == 3 else ("kz" if loc.priority == 2 else "🟢")
            prio_text = "CRITICAL" if loc.priority == 3 else ("HIGH" if loc.priority == 2 else "Normal")
            lines.append(f"{i+2}. 🏥 DELIVER to {loc.name}. Priority: {prio_text} {prio_icon}")
        lines.append(f"{len(route)+2}. 🏁 RETURN to Central Depot.")
        lines.append("\nDrive safely!")
        return "\n".join(lines)
