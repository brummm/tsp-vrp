import matplotlib.pyplot as plt
from typing import List
from src.models.location import Location

class Plotter:
    @staticmethod
    def plot_solution(routes: List[List[Location]], depot: Location):
        plt.figure(figsize=(24, 20))
        
        # Plot Depot
        plt.scatter(depot.x, depot.y, c='red', s=150, marker='s', label='Depot', edgecolors='black')
        
        colors = ['b', 'g', 'c', 'm', 'y', 'orange', 'purple']
        
        for idx, route in enumerate(routes):
            color = colors[idx % len(colors)]
            
            # Construct path: Depot -> Locs -> Depot
            xs = [depot.x] + [loc.x for loc in route] + [depot.x]
            ys = [depot.y] + [loc.y for loc in route] + [depot.y]
            
            # Plot path
            plt.plot(xs, ys, c=color, linestyle='-', linewidth=2, alpha=0.7, label=f'Route {idx+1}')
            
            # Plot stops
            seq  = 1
            for loc in route:
                is_gas = getattr(loc, 'type', 'delivery') == 'gas_station'
                
                if is_gas:
                    fc = 'black'
                    marker = '^'
                elif loc.priority == 3:
                    fc = 'red'
                    marker = 'o'
                elif loc.priority == 2:
                    fc = 'orange'
                    marker = 'o'
                else:
                    fc = color
                    marker = 'o'

                label_text = "Gas Station" if is_gas else f"{seq}. {loc.name}"
                size = 120 if is_gas else 80

                if not is_gas:
                    seq += 1
                    
                plt.scatter(loc.x, loc.y, c=fc, s=size, marker=marker, edgecolors='black', zorder=5)
                # Annotate with sequence number: "1. Hosp. A"
                plt.annotate(label_text, (loc.x+2, loc.y+2), fontsize=9, fontweight='bold')
                
        plt.title("Optimized Vehicle Routing (VRP Solution)")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()