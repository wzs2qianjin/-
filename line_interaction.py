# multi_segment_ship_editor_interface.py
"""
Multi-segment Ship Lines Editor with hull_interface compatibility
Receives three types of lines from Hull2DLineData, supports interactive adjustment
"""

# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportGeneralTypeIssues=false

from hull_interface import Hull2DLineData, InteractionEvent
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.interpolate import CubicSpline
from typing import List, Tuple, Optional, Dict, Any, Union
import numbers

class MultiSegmentShipEditorInterface:
    """
    Multi-segment Ship Lines Editor with hull_interface compatibility
    Supports interactive adjustment of three types of lines
    """
    
    def __init__(self, hull_2d_data: Hull2DLineData):
        # Store the provided 2D data
        self.hull_2d_data = hull_2d_data
        
        # Create figure and subplots
        self.fig, self.axes = plt.subplots(2, 2, figsize=(16, 12))
        self.ax_side = self.axes[0, 0]    # Side profile
        self.ax_half = self.axes[0, 1]    # Half-breadth
        self.ax_cross = self.axes[1, 0]   # Cross sections
        self.ax_info = self.axes[1, 1]    # Information display
        
        # State variables
        self.dragging = False
        self.dragged_idx = None
        self.dragged_line_type = None  # 'side_profile', 'half_breadth', 'cross_section'
        self.dragged_cross_section_x = None  # x-coordinate of cross section
        
        # Control point collections
        self.control_circles = {
            'side_profile': [],
            'half_breadth': [],
            'cross_section': []
        }
        
        # Curve collections
        self.curve_lines = {
            'side_profile': [],
            'half_breadth': [],
            'cross_section': []
        }
        
        # Currently selected cross section
        self.current_cross_section_x = None
        
        # Axis limits
        self.side_x_limits: Tuple[float, float] = (-1, 13)
        self.side_y_limits: Tuple[float, float] = (-0.5, 4)
        self.half_x_limits: Tuple[float, float] = (-1, 13)
        self.half_y_limits: Tuple[float, float] = (-0.5, 3)
        self.cross_x_limits: Tuple[float, float] = (-3, 3)
        self.cross_y_limits: Tuple[float, float] = (-0.5, 4)
        
        # Control point styling
        self.control_point_radius = 0.06
        self.curve_colors: Dict[str, str] = {
            'side_profile': '#3498db',    # Blue
            'half_breadth': '#2ecc71',    # Green
            'cross_section': '#9b59b6'    # Purple
        }
        
        # Interaction event recording
        self.interaction_events: List[InteractionEvent] = []
        
        print("Multi-segment Ship Lines Editor initialized")
        print(f"Side profile points: {len(hull_2d_data.side_profile)}")
        print(f"Half-breadth points: {len(hull_2d_data.half_breadth)}")
        print(f"Cross sections: {len(hull_2d_data.cross_sections)}")
        
        # Initial drawing
        self.initialize_curves()
        self.draw_all_curves()
        
        # Bind events
        self.connect_events()
        
        # Set up plot properties
        self.setup_plots()
    
    def initialize_curves(self) -> None:
        """Initialize curve data"""
        # Create default data if empty
        if not self.hull_2d_data.side_profile:
            self.hull_2d_data.side_profile = [
                (0.0, 0.0), (1.5, 1.0), (3.0, 1.8),
                (4.0, 2.2), (6.0, 2.5), (8.0, 2.2),
                (9.0, 1.8), (10.5, 1.0), (12.0, 0.0)
            ]
        
        if not self.hull_2d_data.half_breadth:
            self.hull_2d_data.half_breadth = [
                (0.0, 0.5), (2.0, 1.0), (4.0, 1.8),
                (6.0, 2.2), (8.0, 2.0), (10.0, 1.5),
                (12.0, 0.8)
            ]
        
        if not self.hull_2d_data.cross_sections:
            # Create example cross sections
            self.hull_2d_data.cross_sections = {
                3.0: [(0.0, 0.0), (1.0, 0.8), (1.5, 1.5), (1.0, 2.2), (0.0, 2.5), 
                      (-1.0, 2.2), (-1.5, 1.5), (-1.0, 0.8), (0.0, 0.0)],
                6.0: [(0.0, 0.0), (1.5, 0.6), (2.0, 1.8), (1.5, 2.8), (0.0, 3.0),
                      (-1.5, 2.8), (-2.0, 1.8), (-1.5, 0.6), (0.0, 0.0)],
                9.0: [(0.0, 0.0), (1.2, 0.4), (1.8, 1.2), (1.2, 2.0), (0.0, 2.2),
                      (-1.2, 2.0), (-1.8, 1.2), (-1.2, 0.4), (0.0, 0.0)]
            }
        
        # Set current cross section
        if self.hull_2d_data.cross_sections:
            self.current_cross_section_x = list(self.hull_2d_data.cross_sections.keys())[0]
    
    def generate_smooth_curve(self, points: List[Tuple[float, float]], is_closed: bool = False) -> List[Tuple[float, float]]:
        """Generate smooth curve"""
        if len(points) < 2:
            return points
        
        if is_closed:
            return self._generate_closed_curve(points)
        else:
            return self._generate_open_curve(points)
    
    def _generate_open_curve(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Generate open smooth curve"""
        x_control = [p[0] for p in points]
        y_control = [p[1] for p in points]
        
        # Sort x-coordinates for interpolation stability
        sorted_indices = np.argsort(x_control)
        x_sorted = np.array([x_control[i] for i in sorted_indices])
        y_sorted = np.array([y_control[i] for i in sorted_indices])
        
        unique_indices = np.where(np.diff(x_sorted) > 1e-10)[0]
        x_unique = np.concatenate([x_sorted[unique_indices], [x_sorted[-1]]])
        y_unique = np.concatenate([y_sorted[unique_indices], [y_sorted[-1]]])
        
        if len(x_unique) < 2:
            return list(zip(x_sorted.tolist(), y_sorted.tolist()))
        
        try:
            cs = CubicSpline(x_unique, y_unique, bc_type='natural')
            x_curve = np.linspace(min(x_unique), max(x_unique), 100)
            y_curve = cs(x_curve)
            
            # 确保使用实数部分
            x_curve_real = np.real(x_curve) if np.iscomplexobj(x_curve) else x_curve
            y_curve_real = np.real(y_curve) if np.iscomplexobj(y_curve) else y_curve
            # 使用列表推导式而不是直接使用numpy数组
            return [(float(x), float(y)) for x, y in zip(x_curve_real, y_curve_real)]
        except Exception as e:
            print(f"Open curve interpolation failed: {e}")
            return self._linear_interpolation(points)
    
    def _generate_closed_curve(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Generate closed smooth curve"""
        if len(points) < 3:
            return points
        
        # Ensure curve is closed
        if (abs(points[0][0] - points[-1][0]) > 1e-10 or 
            abs(points[0][1] - points[-1][1]) > 1e-10):
            points = points + [points[0]]
        
        x_control = [p[0] for p in points]
        y_control = [p[1] for p in points]
        
        # Use parametric spline curves
        t = np.linspace(0, 1, len(x_control))
        
        try:
            cs_x = CubicSpline(t, x_control, bc_type='periodic')
            cs_y = CubicSpline(t, y_control, bc_type='periodic')
            
            t_curve = np.linspace(0, 1, 100)
            x_curve = cs_x(t_curve)
            y_curve = cs_y(t_curve)
            
            # 确保使用实数部分
            x_curve_real = np.real(x_curve) if np.iscomplexobj(x_curve) else x_curve
            y_curve_real = np.real(y_curve) if np.iscomplexobj(y_curve) else y_curve
        
            # 使用列表推导式而不是直接使用numpy数组
            return [(float(x), float(y)) for x, y in zip(x_curve_real, y_curve_real)]
        except Exception as e:
            print(f"Closed curve interpolation failed: {e}")
            return self._linear_interpolation_closed(points)
    
    def _linear_interpolation(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Linear interpolation fallback"""
        if len(points) < 2:
            return points
        
        x_control = [p[0] for p in points]
        y_control = [p[1] for p in points]
        
        x_curve = np.linspace(min(x_control), max(x_control), 100)
        y_curve = np.interp(x_curve, x_control, y_control)
        
        return list(zip(x_curve.tolist(), y_curve.tolist()))
    
    def _linear_interpolation_closed(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Closed curve linear interpolation fallback"""
        if len(points) < 3:
            return points
        
        # Ensure closure
        if (abs(points[0][0] - points[-1][0]) > 1e-10 or 
            abs(points[0][1] - points[-1][1]) > 1e-10):
            points = points + [points[0]]
        
        result: List[Tuple[float, float]] = []
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            segment_points = 20
            for j in range(segment_points):
                t = j / segment_points
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                result.append((x, y))
        
        return result
    
    def create_circle_patch(self, x: float, y: float, line_type: str) -> Circle:
        """Create circle patch"""
        circle = Circle(
            (x, y), self.control_point_radius,
            facecolor=self.curve_colors[line_type], 
            edgecolor='white',
            linewidth=1.5,
            alpha=0.8
        )
        
        try:
            circle.set_picker(True)
        except:
            circle.set_picker(True)
        
        return circle
    
    def draw_all_curves(self):
        """Draw all curves and control points"""
        self.draw_side_profile()
        self.draw_half_breadth()
        self.draw_cross_section()
        self.update_info_panel()
    
    def draw_side_profile(self) -> None:
        """Draw side profile"""
        # Clear previous elements
        for circle in self.control_circles['side_profile']:
            circle.remove()
        self.control_circles['side_profile'].clear()
        
        for line in self.curve_lines['side_profile']:
            line.remove()
        self.curve_lines['side_profile'].clear()
        
        # Generate smooth curve
        curve_points = self.generate_smooth_curve(self.hull_2d_data.side_profile, False)
        
        # Draw curve
        if curve_points:
            x_curve = [p[0] for p in curve_points]
            y_curve = [p[1] for p in curve_points]
            
            line, = self.ax_side.plot(
                x_curve, y_curve, 
                color=self.curve_colors['side_profile'],
                linewidth=2.5,
                alpha=0.8,
                label='Side Profile'
            )
            self.curve_lines['side_profile'].append(line)
        
        # Draw control points
        for i, (x, y) in enumerate(self.hull_2d_data.side_profile):
            circle = self.create_circle_patch(x, y, 'side_profile')
            self.ax_side.add_patch(circle)
            self.control_circles['side_profile'].append(circle)
    
    def draw_half_breadth(self) -> None:
        """Draw half-breadth diagram"""
        # Clear previous elements
        for circle in self.control_circles['half_breadth']:
            circle.remove()
        self.control_circles['half_breadth'].clear()
        
        for line in self.curve_lines['half_breadth']:
            line.remove()
        self.curve_lines['half_breadth'].clear()
        
        # Generate smooth curve
        curve_points = self.generate_smooth_curve(self.hull_2d_data.half_breadth, False)
        
        # Draw curve
        if curve_points:
            x_curve = [p[0] for p in curve_points]
            y_curve = [p[1] for p in curve_points]
            
            line, = self.ax_half.plot(
                x_curve, y_curve, 
                color=self.curve_colors['half_breadth'],
                linewidth=2.5,
                alpha=0.8,
                label='Half-Breadth'
            )
            self.curve_lines['half_breadth'].append(line)
        
        # Draw control points
        for i, (x, y) in enumerate(self.hull_2d_data.half_breadth):
            circle = self.create_circle_patch(x, y, 'half_breadth')
            self.ax_half.add_patch(circle)
            self.control_circles['half_breadth'].append(circle)
    
    def draw_cross_section(self) -> None:
        """Draw cross section"""
        # Clear previous elements
        for circle in self.control_circles['cross_section']:
            circle.remove()
        self.control_circles['cross_section'].clear()
        
        for line in self.curve_lines['cross_section']:
            line.remove()
        self.curve_lines['cross_section'].clear()
        
        if self.current_cross_section_x is None:
            return
        
         # Safe dictionary access with type checking
        cross_section_key = self.current_cross_section_x
        if cross_section_key not in self.hull_2d_data.cross_sections:
            return
        
        cross_points = self.hull_2d_data.cross_sections.get(self.current_cross_section_x, [])
        if not cross_points:
            return
        
        # Generate smooth curve
        curve_points = self.generate_smooth_curve(cross_points, True)
        
        # Draw curve
        if curve_points:
            x_curve = [p[0] for p in curve_points]
            y_curve = [p[1] for p in curve_points]
            
            line, = self.ax_cross.plot(
                x_curve, y_curve, 
                color=self.curve_colors['cross_section'],
                linewidth=2.5,
                alpha=0.8,
                label=f'Cross Section (x={self.current_cross_section_x})'
            )
            self.curve_lines['cross_section'].append(line)
        
        # Draw control points
        for i, (x, y) in enumerate(cross_points):
            circle = self.create_circle_patch(x, y, 'cross_section')
            self.ax_cross.add_patch(circle)
            self.control_circles['cross_section'].append(circle)
    
    def update_info_panel(self):
        """Update information panel"""
        self.ax_info.clear()
        
        # Display basic information
        info_text = [
            "Ship Lines Editor Information",
            "=" * 30,
            f"Side Profile Points: {len(self.hull_2d_data.side_profile)}",
            f"Half-Breadth Points: {len(self.hull_2d_data.half_breadth)}",
            f"Cross Sections: {len(self.hull_2d_data.cross_sections)}",
            f"Current Cross Section: x={self.current_cross_section_x}",
            f"Data Version: {self.hull_2d_data.line_version}",
            "",
            "Interaction Events:",
            f"Event Count: {len(self.interaction_events)}"
        ]
        
        # Display recent events
        recent_events = self.interaction_events[-5:]  # Show last 5 events
        for event in recent_events:
            info_text.append(f"- {event.event_type}: {event.line_type}[{event.target_point_idx}]")
        
        info_text.extend([
            "",
            "Instructions:",
            "• Drag control points to modify curves",
            "• Three line types can be edited independently",
            "• Interaction events are automatically recorded"
        ])
        
        self.ax_info.text(0.05, 0.95, "\n".join(info_text), 
                         transform=self.ax_info.transAxes,
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8))
        
        self.ax_info.set_xlim(0, 1)
        self.ax_info.set_ylim(0, 1)
        self.ax_info.set_xticks([])
        self.ax_info.set_yticks([])
        self.ax_info.set_title('Information Panel', fontsize=12)
    
    def setup_plots(self):
        """Set up plot properties"""
        # Side profile plot settings
        self.ax_side.set_xlabel('Length Direction (m)', fontsize=12)
        self.ax_side.set_ylabel('Depth Direction (m)', fontsize=12)
        self.ax_side.set_title('Side Profile', fontsize=14, fontweight='bold')
        self.ax_side.grid(True, alpha=0.3)
        self.ax_side.legend(fontsize=10)
        self.ax_side.set_aspect('equal')
        self.ax_side.set_xlim(self.side_x_limits[0], self.side_x_limits[1])
        self.ax_side.set_ylim(self.side_y_limits[0], self.side_y_limits[1])
        
        # Half-breadth plot settings
        self.ax_half.set_xlabel('Length Direction (m)', fontsize=12)
        self.ax_half.set_ylabel('Half-Breadth (m)', fontsize=12)
        self.ax_half.set_title('Half-Breadth Diagram', fontsize=14, fontweight='bold')
        self.ax_half.grid(True, alpha=0.3)
        self.ax_half.legend(fontsize=10)
        self.ax_half.set_aspect('equal')
        self.ax_half.set_xlim(self.half_x_limits[0], self.half_x_limits[1])
        self.ax_half.set_ylim(self.half_y_limits[0], self.half_y_limits[1])
        
        # Cross section plot settings
        self.ax_cross.set_xlabel('Width Direction (m)', fontsize=12)
        self.ax_cross.set_ylabel('Height Direction (m)', fontsize=12)
        self.ax_cross.set_title('Cross Sections', fontsize=14, fontweight='bold')
        self.ax_cross.grid(True, alpha=0.3)
        self.ax_cross.legend(fontsize=10)
        self.ax_cross.set_aspect('equal')
        self.ax_cross.set_xlim(self.cross_x_limits[0], self.cross_x_limits[1])
        self.ax_cross.set_ylim(self.cross_y_limits[0], self.cross_y_limits[1])
        
        # Information panel settings
        self.ax_info.set_title('Information Panel', fontsize=12)
        
        # Overall title
        self.fig.suptitle('Ship Lines Interactive Editor - hull_interface Compatible', 
                         fontsize=16, fontweight='bold', y=0.95)
        
        plt.tight_layout()
    
    def connect_events(self) -> None:
        """Bind event handlers"""
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
    
    def on_press(self, event) -> None:
        """Mouse press event"""
        if event.button != 1 or not event.inaxes:
            return
        
        # Detect control points in each line type
        for line_type in ['side_profile', 'half_breadth', 'cross_section']:
            for i, circle in enumerate(self.control_circles[line_type]):
                center = circle.center
                distance = np.sqrt((event.xdata - center[0])**2 + (event.ydata - center[1])**2)
                
                if distance <= self.control_point_radius * 1.5:
                    self.dragging = True
                    self.dragged_idx = i
                    self.dragged_line_type = line_type
                    
                    if line_type == 'cross_section':
                        self.dragged_cross_section_x = self.current_cross_section_x
                    
                    self.highlight_control_point(i, line_type)
                    
                    # Record interaction event
                    interaction_event = InteractionEvent(
                        event_type="drag_start",
                        line_type=line_type,
                        target_point_idx=i,
                        new_coords=(center[0], center[1]),
                        cross_section_x=self.dragged_cross_section_x
                    )
                    self.interaction_events.append(interaction_event)
                    
                    print(f"Started dragging {line_type} control point {i}")
                    return
    
    def on_drag(self, event: Any) -> None:
        """Mouse drag event"""
        if not self.dragging or self.dragged_idx is None or not event.inaxes:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        # 确保dragged_line_type是字符串
        if self.dragged_line_type is None:
            return
        
        # 使用局部变量确保类型安全
        line_type: str = self.dragged_line_type
        
        # Get new coordinates
        if self.dragged_line_type == 'side_profile':
            new_x = max(self.side_x_limits[0], min(self.side_x_limits[1], event.xdata))
            new_y = max(self.side_y_limits[0], min(self.side_y_limits[1], event.ydata))
            points = self.hull_2d_data.side_profile
        elif self.dragged_line_type == 'half_breadth':
            new_x = max(self.half_x_limits[0], min(self.half_x_limits[1], event.xdata))
            new_y = max(self.half_y_limits[0], min(self.half_y_limits[1], event.ydata))
            points = self.hull_2d_data.half_breadth
        else:  # cross_section
            new_x = max(self.cross_x_limits[0], min(self.cross_x_limits[1], event.xdata))
            new_y = max(self.cross_y_limits[0], min(self.cross_y_limits[1], event.ydata))
            if self.dragged_cross_section_x is not None:
                points = self.hull_2d_data.cross_sections.get(self.dragged_cross_section_x, [])
            else:
                points = []
        
        # Update control point position
        if self.dragged_idx < len(points):
            points[self.dragged_idx] = (new_x, new_y)
            
            # Update control point display
            circle = self.control_circles[line_type][self.dragged_idx]
            circle.center = (new_x, new_y)
            
            # Update curve
            self.update_curve_only(line_type)
            
            # Record interaction event
            interaction_event = InteractionEvent(
                event_type="dragging",
                line_type=self.dragged_line_type,
                target_point_idx=self.dragged_idx,
                new_coords=(new_x, new_y),
                cross_section_x=self.dragged_cross_section_x
            )
            self.interaction_events.append(interaction_event)
    
    def on_release(self, event: Any) -> None:
        """Mouse release event"""
        if self.dragging and self.dragged_idx is not None and self.dragged_line_type is not None:
            # 确保line_type是字符串类型
            line_type: str = self.dragged_line_type
            
            # Record interaction event
            if line_type == 'side_profile':
                points = self.hull_2d_data.side_profile
            elif line_type == 'half_breadth':
                points = self.hull_2d_data.half_breadth
            else:  # cross_section
                if self.dragged_cross_section_x is not None:
                    points = self.hull_2d_data.cross_sections.get(self.dragged_cross_section_x, [])
                else:
                    points = []
            
            if self.dragged_idx < len(points):
                interaction_event = InteractionEvent(
                    event_type="drag_end",
                    line_type=line_type,
                    target_point_idx=self.dragged_idx,
                    new_coords=points[self.dragged_idx],
                    cross_section_x=self.dragged_cross_section_x
                )
                self.interaction_events.append(interaction_event)
                
                # Update data version
                self.hull_2d_data.line_version += 1
            
            print(f"Finished dragging {line_type} control point {self.dragged_idx}")
            
            # Update curve
            self.update_curve_only(line_type)  # 使用line_type而不是self.dragged_line_type
            
            # Reset colors
            self.reset_control_colors()
            
            # Update information panel
            self.update_info_panel()
        
        self.dragging = False
        self.dragged_idx = None
        self.dragged_line_type = None
        self.dragged_cross_section_x = None
    
    def highlight_control_point(self, index: int, line_type: str) -> None:
        """Highlight selected control point"""
        for lt in ['side_profile', 'half_breadth', 'cross_section']:
            for i, circle in enumerate(self.control_circles[lt]):
                if lt == line_type and i == index:
                    circle.set_facecolor('yellow')
                    circle.set_edgecolor('darkorange')
                    circle.set_linewidth(2.5)
                    circle.set_alpha(1.0)
                else:
                    circle.set_facecolor(self.curve_colors[lt])
                    circle.set_edgecolor('white')
                    circle.set_linewidth(1.5)
                    circle.set_alpha(0.8)
        
        self.fig.canvas.draw_idle()
    
    def reset_control_colors(self) -> None:
        """Reset all control point colors"""
        for line_type in ['side_profile', 'half_breadth', 'cross_section']:
            for circle in self.control_circles[line_type]:
                circle.set_facecolor(self.curve_colors[line_type])
                circle.set_edgecolor('white')
                circle.set_linewidth(1.5)
                circle.set_alpha(0.8)
        
        self.fig.canvas.draw_idle()
    
    def update_curve_only(self, line_type: str) -> None:
        """Update only the specified curve type"""
        if line_type == 'side_profile':
            curve_points = self.generate_smooth_curve(self.hull_2d_data.side_profile, False)
            if self.curve_lines['side_profile'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                self.curve_lines['side_profile'][0].set_data(x_curve, y_curve)
        
        elif line_type == 'half_breadth':
            curve_points = self.generate_smooth_curve(self.hull_2d_data.half_breadth, False)
            if self.curve_lines['half_breadth'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                self.curve_lines['half_breadth'][0].set_data(x_curve, y_curve)
        
        elif line_type == 'cross_section' and self.current_cross_section_x is not None:
            cross_points = self.hull_2d_data.cross_sections.get(self.current_cross_section_x, [])
            curve_points = self.generate_smooth_curve(cross_points, True)
            if self.curve_lines['cross_section'] and curve_points:
                x_curve = [p[0] for p in curve_points]
                y_curve = [p[1] for p in curve_points]
                self.curve_lines['cross_section'][0].set_data(x_curve, y_curve)
        
        self.fig.canvas.draw_idle()
    
    def get_interaction_events(self) -> List[InteractionEvent]:
        """Get all interaction events"""
        return self.interaction_events.copy()
    
    def get_updated_hull_data(self) -> Hull2DLineData:
        """Get updated Hull2DLineData"""
        return self.hull_2d_data
    
    def show(self) -> None:
        """Show editor"""
        plt.tight_layout()
        plt.show()