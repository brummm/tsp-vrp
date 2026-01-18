import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import List
from src.models.location import Location

class Plotter:
    @staticmethod
    def plot_solution(routes: List[List[Location]], depot: Location):
        plt.figure(figsize=(24, 20))
        
        # Plot Depot Base
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
            seq = 1
            for loc in route:
                is_gas = getattr(loc, 'type', 'delivery') == 'gas_station'
                is_depot = getattr(loc, 'type', 'delivery') == 'depot'
                
                label_text = f"{seq}. {loc.name}"
                marker = 'o'
                fc = color
                
                if is_gas:
                    fc = 'black'
                    marker = '^'
                    label_text = "Gas Station"
                elif is_depot:
                    fc = 'red'
                    marker = 's'
                    label_text = None
                elif loc.priority == 3:
                    fc = 'red'
                elif loc.priority == 2:
                    fc = 'orange'
                
                size = 120 if is_gas else (100 if is_depot else 80)

                if not is_gas and not is_depot:
                    seq += 1
                
                plt.scatter(loc.x, loc.y, c=fc, s=size, marker=marker, edgecolors='black', zorder=5)
                
                if label_text is not None:
                    plt.annotate(label_text, (loc.x+1, loc.y+1), fontsize=9, fontweight='bold')

        plt.title("Optimized Vehicle Routing (VRP Solution)")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        
        # Custom Legend
        legend_elements = [
            Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, markeredgecolor='black', label='Depot / Refill'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, markeredgecolor='black', label='Critical Priority'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, markeredgecolor='black', label='High Priority'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=10, markeredgecolor='black', label='Normal Priority (Route Color)'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='black', markersize=10, markeredgecolor='black', label='Gas Station'),
        ]
        
        handles, labels = plt.gca().get_legend_handles_labels()
        
        # Deduplicate and merge
        by_label = dict()
        # for h, l in zip(handles, labels):
        #     if l not in by_label:
        #         by_label[l] = h
        for le in legend_elements:
            if le.get_label() not in by_label:
                by_label[le.get_label()] = le
                 
        plt.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()
