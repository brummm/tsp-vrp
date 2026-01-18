import os
from typing import List
from src.models.location import Location

# Try importing transformers
try:
    from transformers import pipeline
except ImportError:
    pipeline = None

class ReportGenerator:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.pipe = None
        if pipeline:
            try:
                # Load the pipeline. 
                # device_map="auto" attempts to use GPU/MPS if available, otherwise CPU.
                # This requires 'accelerate' and 'torch' installed.
                print(f"Loading local model: {model_name}...")
                self.pipe = pipeline("text-generation", model=model_name, device_map="auto")
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Failed to load local model {model_name}: {e}")
                pass

    def generate_driver_instructions(self, route_idx: int, route: List[Location]) -> str:
        """
        Generates natural language instructions for a driver using a local LLM.
        """
        # Hybrid Approach:
        # 1. Use LLM to generate a friendly, unique intro.
        # 2. Programmatically format the route list to guarantee accuracy (0% hallucination).
        # 3. Use LLM to generate a safety tip or closing.

        intro_prompt = f"Write a single friendly, motivating sentence to start a route sheet for Driver #{route_idx+1}."
        
        intro_text = "Here is your route:"
        if self.pipe:
            try:
                # Generate Intro
                outputs = self.pipe(
                    [{"role": "user", "content": intro_prompt}],
                    max_new_tokens=50,
                    do_sample=True,
                    temperature=0.8
                )
                intro_text = outputs[0]["generated_text"][-1]["content"].strip()
            except:
                pass

        # Programmatic List formatting (Guaranteed Correctness)
        lines = [f"*** {intro_text} ***", ""]
        lines.append("1. 🏭 START at Central Depot")
        
        for i, loc in enumerate(route):
            # Logic for priority display
            if loc.priority == 3:
                prio_str = "CRITICAL (3) 🔴"
            elif loc.priority == 2:
                prio_str = "HIGH (2) 🟠"
            else:
                prio_str = "Normal (1) 🟢"
            
            lines.append(f"{i+2}. 🏥 STOP: {loc.name} - Priority: {prio_str}")
        
        lines.append(f"{len(route)+2}. 🏁 END at Central Depot")
        lines.append("")

        # Closing
        closing_text = "Drive safely!"
        if self.pipe:
            try:
                outputs = self.pipe(
                    [{"role": "user", "content": "Write a short, 5-word safety reminder for a driver."}],
                    max_new_tokens=20,
                    do_sample=True,
                    temperature=0.7
                )
                closing_text = outputs[0]["generated_text"][-1]["content"].strip()
            except:
                pass
        
        lines.append(closing_text)

        return "\n".join(lines)

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