import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_schema_diagram():
    """Create a visual diagram of the normalized database schema."""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Define colors
    primary_color = '#2E86C1'
    foreign_color = '#F39C12'
    table_color = '#EBF2FA'
    border_color = '#34495E'
    
    # Table definitions with their positions and fields
    tables = {
        'cities': {
            'pos': (2, 9),
            'fields': [
                'city_market_id (PK)',
                'city_name',
                'state',
                'full_city_name'
            ]
        },
        'airports': {
            'pos': (6, 9),
            'fields': [
                'airport_id (PK)',
                'airport_code',
                'city_market_id (FK)'
            ]
        },
        'carriers': {
            'pos': (10, 9),
            'fields': [
                'carrier_id (PK)',
                'carrier_code',
                'carrier_type'
            ]
        },
        'routes': {
            'pos': (6, 6),
            'fields': [
                'route_id (PK)',
                'origin_airport_id (FK)',
                'destination_airport_id (FK)',
                'distance_miles'
            ]
        },
        'flights': {
            'pos': (6, 3),
            'fields': [
                'flight_id (PK)',
                'route_id (FK)',
                'year',
                'quarter',
                'passengers',
                'fare',
                'source_record_id'
            ]
        },
        'market_share': {
            'pos': (10, 3),
            'fields': [
                'flight_id (FK)',
                'carrier_id (FK)',
                'market_share',
                'fare'
            ]
        }
    }
    
    # Draw tables
    table_boxes = {}
    for table_name, table_info in tables.items():
        x, y = table_info['pos']
        fields = table_info['fields']
        
        # Calculate box dimensions
        max_width = max(len(field) for field in [table_name.upper()] + fields)
        box_width = max(2.5, max_width * 0.08)
        box_height = len(fields) * 0.3 + 0.5
        
        # Draw table box
        table_box = FancyBboxPatch(
            (x - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor=table_color,
            edgecolor=border_color,
            linewidth=2
        )
        ax.add_patch(table_box)
        
        # Store box info for connections
        table_boxes[table_name] = {
            'x': x, 'y': y,
            'width': box_width, 'height': box_height
        }
        
        # Draw table name
        ax.text(x, y + box_height/2 - 0.2, table_name.upper(), 
                ha='center', va='center', fontsize=12, fontweight='bold',
                color=primary_color)
        
        # Draw fields
        for i, field in enumerate(fields):
            field_y = y + box_height/2 - 0.5 - (i * 0.3)
            
            # Color code primary keys and foreign keys
            if '(PK)' in field:
                color = primary_color
                fontweight = 'bold'
            elif '(FK)' in field:
                color = foreign_color
                fontweight = 'bold'
            else:
                color = 'black'
                fontweight = 'normal'
            
            ax.text(x, field_y, field, ha='center', va='center', 
                   fontsize=9, color=color, fontweight=fontweight)
    
    # Define relationships
    relationships = [
        ('cities', 'airports', 'city_market_id'),
        ('airports', 'routes', 'origin_airport_id'),
        ('airports', 'routes', 'destination_airport_id'),
        ('routes', 'flights', 'route_id'),
        ('flights', 'market_share', 'flight_id'),
        ('carriers', 'market_share', 'carrier_id')
    ]
    
    # Draw relationships
    for parent, child, fk_name in relationships:
        parent_info = table_boxes[parent]
        child_info = table_boxes[child]
        
        # Calculate connection points
        if parent == 'airports' and child == 'routes':
            # Special handling for airports -> routes (two connections)
            if fk_name == 'origin_airport_id':
                start_x = parent_info['x'] - 0.3
                end_x = child_info['x'] - 0.3
            else:  # destination_airport_id
                start_x = parent_info['x'] + 0.3
                end_x = child_info['x'] + 0.3
        else:
            start_x = parent_info['x']
            end_x = child_info['x']
        
        start_y = parent_info['y'] - parent_info['height']/2
        end_y = child_info['y'] + child_info['height']/2
        
        # Draw connection line
        connection = ConnectionPatch(
            (start_x, start_y), (end_x, end_y),
            "data", "data",
            arrowstyle="->",
            shrinkA=5, shrinkB=5,
            mutation_scale=20,
            fc=foreign_color,
            ec=foreign_color,
            linewidth=2
        )
        ax.add_patch(connection)
    
    # Add title and legend
    ax.text(8, 11.5, 'Normalized US Airlines Database Schema', 
            ha='center', va='center', fontsize=16, fontweight='bold',
            color=primary_color)
    
    # Legend
    legend_x = 13
    legend_y = 8
    
    ax.text(legend_x, legend_y, 'Legend:', fontsize=12, fontweight='bold')
    ax.text(legend_x, legend_y - 0.5, '(PK) = Primary Key', fontsize=10, 
            color=primary_color, fontweight='bold')
    ax.text(legend_x, legend_y - 0.8, '(FK) = Foreign Key', fontsize=10, 
            color=foreign_color, fontweight='bold')
    ax.text(legend_x, legend_y - 1.1, '→ = Relationship', fontsize=10, 
            color=foreign_color)
    
    # Add normalization info
    norm_info = [
        "✅ 1NF: All attributes are atomic",
        "✅ 2NF: No partial dependencies", 
        "✅ 3NF: No transitive dependencies",
        "",
        "Benefits:",
        "• Eliminates data redundancy",
        "• Prevents update anomalies",
        "• Improves data integrity",
        "• Optimizes storage space"
    ]
    
    for i, info in enumerate(norm_info):
        ax.text(1, 2 - i*0.3, info, fontsize=9, 
                fontweight='bold' if info.startswith('✅') or info == 'Benefits:' else 'normal',
                color='green' if info.startswith('✅') else 'black')
    
    plt.tight_layout()
    plt.savefig('normalized_schema_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Schema diagram saved as 'normalized_schema_diagram.png'")

if __name__ == "__main__":
    create_schema_diagram() 