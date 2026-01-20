from typing import List
from src.models.location import Location

# Try importing transformers
try:
    from transformers import pipeline
except ImportError:
    pipeline = None

# Global cache to prevent re-loading the model in Jupyter notebooks
_SHARED_PIPELINE = None

class ReportGenerator:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-3B-Instruct"):
        global _SHARED_PIPELINE
        self.pipe = None
        
        if pipeline:
            # Check if we already have the model loaded in memory
            if _SHARED_PIPELINE is not None:
                self.pipe = _SHARED_PIPELINE
                print("Using cached LLM model.")
            else:
                try:
                    print(f"Loading local model: {model_name}...")
                    # Optimization: Use auto-dtype (usually float16) to speed up and save RAM
                    _SHARED_PIPELINE = pipeline(
                        "text-generation", 
                        model=model_name, 
                        device_map="auto",
                        dtype="auto"
                    )
                    self.pipe = _SHARED_PIPELINE
                    print("Model loaded successfully.")
                except Exception as e:
                    print(f"Failed to load local model {model_name}: {e}")
                    pass

    def generate_driver_instructions(self, route_idx: int, route: List[Location]) -> str:
        """
        Generates natural language instructions for a driver using a local LLM.
        """
        # 1. Pre-process the data in Python (Guaranteed Accuracy)
        formatted_stops = []
        for loc in route:
            # Determine priority label in Python
            prio_label = "Normal"
            if loc.priority == 2:
                prio_label = "Immediate"
            elif loc.priority == 3:
                prio_label = "High"
            
            # Simple line for the LLM to format
            line = loc.name if loc.type == 'depot' or loc.type == 'gas_station' else f"- {loc.name} (Priority: {prio_label})"
            formatted_stops.append(line)

        stops_block = "\n".join(formatted_stops)
        
        # 2. Strong Instruction Prompt
        messages = [
            {"role": "system", "content": "You are a Logistics Dispatcher. Write a friendly, informal daily note for a driver. Keep it natural and non-formal."},
            {"role": "user", "content": (
                "Write a short note for the driver today.\n"
                "1. Start with a friendly greeting.\n"
                "2. List these stops exactly as shown:\n"
                f"{stops_block}\n"
                "3. End with a casual safety reminder.\n"
                "DO NOT use email formatting (no Subject/Dear/Best regards)."
            )}
        ]

        if not self.pipe:
            print("Model not loaded.")
            return None

        try:
            outputs = self.pipe(
                messages, 
                max_new_tokens=256, # Optimization: Reduced from 512
                do_sample=True, 
                temperature=0.7,
                top_p=0.9
            )
            generated_text = outputs[0]["generated_text"][-1]["content"]
            return generated_text.strip()
        except Exception as e:
            print(f"Generation error: {e}")
            return None
