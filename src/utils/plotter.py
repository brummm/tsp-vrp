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
            for seq, loc in enumerate(route, start=1):
                is_gas = getattr(loc, 'type', 'delivery') == 'gas_station'
                
                if is_gas:
                    fc = 'black'
                    marker = '^'
                    size = 120
                    label_text = "Gas Station"
                elif loc.priority == 3:
                    fc = 'red'
                    marker = 'o'
                    size = 80
                    label_text = loc.name
                elif loc.priority == 2:
                    fc = 'orange'
                    marker = 'o'
                    size = 80
                    label_text = loc.name
                else:
                    fc = color
                    marker = 'o'
                    size = 80
                    label_text = loc.name
                    
                plt.scatter(loc.x, loc.y, c=fc, s=size, marker=marker, edgecolors='black', zorder=5)
                # Annotate with sequence number: "1. Hosp. A"
                plt.annotate(f"{seq}. {loc.name}", (loc.x+2, loc.y+2), fontsize=9, fontweight='bold')
                
        plt.title("Optimized Vehicle Routing (VRP Solution)")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()