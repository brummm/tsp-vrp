import os
from typing import List
from src.models.location import Location

# Try importing openai, handle if not installed or configured
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ReportGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except:
                pass # Fallback to mock

    def generate_driver_instructions(self, route_idx: int, route: List[Location]) -> str:
        """
        Generates natural language instructions for a driver.
        """
        stops_str = ", ".join([f"{loc.name} (Priority {loc.priority})" for loc in route])
        prompt = (f"Generate a friendly and concise route plan for Driver #{route_idx+1}. "
                  f"The sequence of stops is: {stops_str}. "
                  "Start from the Central Depot, visit these stops in exact order, and finally return to the Central Depot. "
                  "Highlight any High or Critical priority stops.")

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful logistics assistant for a medical delivery company."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200
                )
                return response.choices[0].message.content
            except Exception as e:
                # Log error or silence it
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
