#!/usr/bin/env python3
"""
ManipulatorAI Data Flow Diagram Generator
Creates a visual representation of the data flow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_data_flow_diagram():
    """Create a comprehensive data flow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Color scheme
    colors = {
        'external': '#FF6B6B',      # Red for external services
        'api': '#4ECDC4',           # Teal for API layer
        'processing': '#45B7D1',    # Blue for processing
        'database': '#96CEB4',      # Green for databases
        'queue': '#FECA57',         # Yellow for queues
        'ai': '#A8E6CF',           # Light green for AI
        'monitoring': '#FFB6C1'     # Pink for monitoring
    }
    
    # Define components with positions
    components = {
        # External Layer
        'Facebook/Instagram': (1, 9, colors['external']),
        'Client Apps': (1, 7, colors['external']),
        'OpenAI/Azure': (9, 8, colors['ai']),
        
        # API Layer
        'Webhook Endpoints': (3, 9, colors['api']),
        'Conversation API': (3, 7, colors['api']),
        'FastAPI App': (3, 5, colors['api']),
        
        # Processing Layer
        'Task Manager': (5, 8, colors['processing']),
        'Conversation Engine': (5, 6, colors['processing']),
        'Celery Workers': (5, 4, colors['processing']),
        
        # Queue Layer
        'Redis Queues': (7, 6, colors['queue']),
        'Task Results': (7, 4, colors['queue']),
        
        # Database Layer
        'PostgreSQL': (1, 3, colors['database']),
        'MongoDB': (3, 3, colors['database']),
        'Redis Cache': (5, 2, colors['database']),
        
        # Monitoring
        'Flower Dashboard': (9, 4, colors['monitoring']),
        'Health Endpoints': (9, 6, colors['monitoring']),
    }
    
    # Draw components
    boxes = {}
    for name, (x, y, color) in components.items():
        box = FancyBboxPatch(
            (x-0.4, y-0.2), 0.8, 0.4,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=8, fontweight='bold')
        boxes[name] = (x, y)
    
    # Define data flows
    flows = [
        # External to API
        ('Facebook/Instagram', 'Webhook Endpoints', '1. Webhook Events'),
        ('Client Apps', 'Conversation API', '2. Direct API Calls'),
        
        # API to Processing
        ('Webhook Endpoints', 'Task Manager', '3. Queue Tasks'),
        ('Conversation API', 'Conversation Engine', '4. Process Messages'),
        ('FastAPI App', 'Task Manager', '5. Async Tasks'),
        
        # Processing flows
        ('Task Manager', 'Redis Queues', '6. Task Queuing'),
        ('Celery Workers', 'Conversation Engine', '7. Background Processing'),
        ('Conversation Engine', 'OpenAI/Azure', '8. AI Requests'),
        
        # Database interactions
        ('Conversation Engine', 'PostgreSQL', '9. Product Queries'),
        ('Conversation Engine', 'MongoDB', '10. Store Conversations'),
        ('Task Manager', 'Redis Cache', '11. Cache Results'),
        
        # Results and monitoring
        ('Celery Workers', 'Task Results', '12. Store Results'),
        ('Celery Workers', 'Flower Dashboard', '13. Task Monitoring'),
        ('FastAPI App', 'Health Endpoints', '14. Health Checks'),
    ]
    
    # Draw flows
    for i, (start, end, label) in enumerate(flows):
        if start in boxes and end in boxes:
            x1, y1 = boxes[start]
            x2, y2 = boxes[end]
            
            # Create arrow
            arrow = ConnectionPatch(
                (x1, y1), (x2, y2), "data", "data",
                arrowstyle="->", shrinkA=20, shrinkB=20,
                mutation_scale=15, fc="black", alpha=0.6
            )
            ax.add_patch(arrow)
            
            # Add label
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x, mid_y + 0.1, str(i+1), ha='center', va='center', 
                   fontsize=6, bbox=dict(boxstyle="circle", facecolor='white', alpha=0.8))
    
    # Add title and legend
    ax.text(5, 9.7, 'ManipulatorAI Data Flow Architecture', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Create legend
    legend_elements = [
        mpatches.Patch(color=colors['external'], label='External Services'),
        mpatches.Patch(color=colors['api'], label='API Layer'),
        mpatches.Patch(color=colors['processing'], label='Processing Layer'),
        mpatches.Patch(color=colors['queue'], label='Queue & Cache'),
        mpatches.Patch(color=colors['database'], label='Databases'),
        mpatches.Patch(color=colors['ai'], label='AI Services'),
        mpatches.Patch(color=colors['monitoring'], label='Monitoring')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Add data flow explanation
    explanation = """
Data Flow Explanation:
1-2: External inputs (webhooks, API calls)
3-5: Request routing and task creation
6-7: Asynchronous task processing
8: AI service integration
9-11: Database operations
12-14: Results and monitoring
    """
    
    ax.text(0.5, 1.5, explanation, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle="round", facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def create_conversation_flow_diagram():
    """Create a detailed conversation flow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define conversation flow steps
    steps = [
        (2, 9, "Customer Message", '#FF6B6B'),
        (2, 8, "API Validation", '#4ECDC4'),
        (2, 7, "Branch Detection", '#45B7D1'),
        (1, 6, "Manipulator Branch\n(Product-focused)", '#96CEB4'),
        (3, 6, "Convincer Branch\n(Discovery-focused)", '#96CEB4'),
        (2, 5, "Conversation Engine", '#45B7D1'),
        (1, 4, "Product Matching", '#FECA57'),
        (2, 4, "AI Processing", '#A8E6CF'),
        (3, 4, "Context Analysis", '#FECA57'),
        (2, 3, "Response Generation", '#45B7D1'),
        (2, 2, "Store Conversation", '#96CEB4'),
        (2, 1, "Return Response", '#4ECDC4'),
    ]
    
    # Draw steps
    for i, (x, y, text, color) in enumerate(steps):
        # Draw box
        box = FancyBboxPatch(
            (x-0.5, y-0.15), 1, 0.3,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Draw arrows (except for branch splits and rejoins)
        if i > 0 and i < len(steps) - 1:
            if i == 3:  # Branch split
                # Arrow from Branch Detection to Manipulator
                arrow1 = ConnectionPatch(
                    (2, 7-0.15), (1, 6+0.15), "data", "data",
                    arrowstyle="->", shrinkA=5, shrinkB=5,
                    mutation_scale=15, fc="black", alpha=0.6
                )
                ax.add_patch(arrow1)
                # Arrow from Branch Detection to Convincer
                arrow2 = ConnectionPatch(
                    (2, 7-0.15), (3, 6+0.15), "data", "data",
                    arrowstyle="->", shrinkA=5, shrinkB=5,
                    mutation_scale=15, fc="black", alpha=0.6
                )
                ax.add_patch(arrow2)
            elif i == 5:  # Branch rejoin
                # Arrow from Manipulator to Conversation Engine
                arrow1 = ConnectionPatch(
                    (1, 6-0.15), (2, 5+0.15), "data", "data",
                    arrowstyle="->", shrinkA=5, shrinkB=5,
                    mutation_scale=15, fc="black", alpha=0.6
                )
                ax.add_patch(arrow1)
                # Arrow from Convincer to Conversation Engine
                arrow2 = ConnectionPatch(
                    (3, 6-0.15), (2, 5+0.15), "data", "data",
                    arrowstyle="->", shrinkA=5, shrinkB=5,
                    mutation_scale=15, fc="black", alpha=0.6
                )
                ax.add_patch(arrow2)
            elif i not in [4, 6, 7, 8]:  # Skip branch steps and parallel processing
                prev_step = steps[i-1]
                if i == 9:  # Multiple inputs to Response Generation
                    # From Product Matching
                    arrow1 = ConnectionPatch(
                        (1, 4-0.15), (2, 3+0.15), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5,
                        mutation_scale=15, fc="black", alpha=0.6
                    )
                    ax.add_patch(arrow1)
                    # From AI Processing
                    arrow2 = ConnectionPatch(
                        (2, 4-0.15), (2, 3+0.15), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5,
                        mutation_scale=15, fc="black", alpha=0.6
                    )
                    ax.add_patch(arrow2)
                    # From Context Analysis
                    arrow3 = ConnectionPatch(
                        (3, 4-0.15), (2, 3+0.15), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5,
                        mutation_scale=15, fc="black", alpha=0.6
                    )
                    ax.add_patch(arrow3)
                else:
                    arrow = ConnectionPatch(
                        (prev_step[0], prev_step[1]-0.15), (x, y+0.15), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5,
                        mutation_scale=15, fc="black", alpha=0.6
                    )
                    ax.add_patch(arrow)
    
    # Add parallel processing arrows
    # From Conversation Engine to parallel processes
    for target_x in [1, 2, 3]:
        arrow = ConnectionPatch(
            (2, 5-0.15), (target_x, 4+0.15), "data", "data",
            arrowstyle="->", shrinkA=5, shrinkB=5,
            mutation_scale=15, fc="black", alpha=0.6
        )
        ax.add_patch(arrow)
    
    # Add title
    ax.text(5, 9.5, 'ManipulatorAI Conversation Processing Flow', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Add side explanations
    manipulator_text = """
Manipulator Branch:
• Customer interacted with ad
• Product-focused conversation
• Direct sales approach
• Feature highlighting
• Pricing discussions
    """
    
    convincer_text = """
Convincer Branch:
• Direct message/inquiry
• Discovery-focused
• Needs assessment
• Solution matching
• Consultative approach
    """
    
    ax.text(5.5, 7, manipulator_text, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
    
    ax.text(5.5, 5, convincer_text, ha='left', va='top', fontsize=9,
           bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.8))
    
    # Add data examples
    data_examples = """
Example Data Flow:

Input: "Interested in CRM software"
↓
Validation: Schema check, customer ID validation
↓
Branch: Manipulator (from ad interaction)
↓
Product Match: BasicCRM (score: 0.92)
AI Response: "Great choice! Our BasicCRM..."
Context: Small business, retail industry
↓
Generated Response: Personalized sales message
↓
Storage: MongoDB conversation + PostgreSQL analytics
↓
Output: JSON response with next actions
    """
    
    ax.text(6, 3, data_examples, ha='left', va='top', fontsize=8,
           bbox=dict(boxstyle="round", facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create diagrams
    print("Creating ManipulatorAI data flow diagrams...")
    
    # Main data flow diagram
    fig1 = create_data_flow_diagram()
    fig1.savefig('/Users/Kazi/Desktop/Manipulator-Demo/docs/data_flow_architecture.png', 
                dpi=300, bbox_inches='tight')
    print("✅ Created data_flow_architecture.png")
    
    # Conversation flow diagram
    fig2 = create_conversation_flow_diagram()
    fig2.savefig('/Users/Kazi/Desktop/Manipulator-Demo/docs/conversation_flow_diagram.png', 
                dpi=300, bbox_inches='tight')
    print("✅ Created conversation_flow_diagram.png")
    
    plt.show()
    print("🎯 Diagrams created successfully!")
