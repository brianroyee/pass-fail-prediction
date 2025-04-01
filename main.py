import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import os
from datetime import datetime

class SubjectPerformanceModel:
    def __init__(self):
        self.confirmed_parameters = {
            'preparedness': 50,        # Student preparedness for the subject
            'teaching': 50,            # Teaching effectiveness
            'materials': 50,           # Study materials availability
            'participation': 50,       # Class participation
            'difficulty': 50           # Subject difficulty (higher = harder)
        }
        self.pending_parameters = self.confirmed_parameters.copy()
        self.performance_history = []
        self.time_steps = []
        self.current_time = 0
        self.load_parameters()
        
    def load_parameters(self):
        """Load parameters from JSON file if it exists"""
        if os.path.exists('subject_parameters.json'):
            try:
                with open('subject_parameters.json', 'r') as f:
                    data = json.load(f)
                    for param in self.confirmed_parameters:
                        if param in data:
                            self.confirmed_parameters[param] = data[param]
                            self.pending_parameters[param] = data[param]
            except Exception as e:
                print(f"Error loading parameters: {e}")
    
    def save_parameters(self):
        """Save current parameters to JSON file"""
        try:
            with open('subject_parameters.json', 'w') as f:
                json.dump(self.confirmed_parameters, f, indent=4)
        except Exception as e:
            print(f"Error saving parameters: {e}")
    
    def update_pending_parameters(self, params):
        """Update parameters that haven't been confirmed yet"""
        for param, value in params.items():
            if param in self.pending_parameters:
                self.pending_parameters[param] = value
    
    def confirm_parameters(self):
        """Confirm the pending parameters and recalculate"""
        changes_made = False
        change_log = []
        
        for param in self.confirmed_parameters:
            if self.confirmed_parameters[param] != self.pending_parameters[param]:
                old_val = self.confirmed_parameters[param]
                new_val = self.pending_parameters[param]
                change_log.append(f"{param.replace('_', ' ')}: {old_val} → {new_val}")
                self.confirmed_parameters[param] = new_val
                changes_made = True
        
        if changes_made:
            self.save_parameters()
            self.calculate_performance()
            return "\n".join(change_log)
        return None
    
    def calculate_performance(self):
        """Calculate pass probability based on confirmed parameters"""
        weights = {
            'preparedness': 0.3,
            'teaching': 0.3,
            'materials': 0.2,
            'participation': 0.15,
            'difficulty': -0.05  # Negative weight because higher difficulty lowers pass chance
        }
        
        # Calculate weighted score (0-100 scale)
        score = sum(self.confirmed_parameters[param] * weights[param] 
                 for param in self.confirmed_parameters)
        
        # Ensure score stays within bounds
        score = max(0, min(100, score))
        
        # Store the performance with timestamp
        self.performance_history.append(score)
        self.time_steps.append(self.current_time)
        self.current_time += 1
        
        return score
    
    def predict_pass_fail(self):
        """Determine pass/fail prediction based on current score"""
        if not self.performance_history:
            return "No data", "black", "gray"
        
        current_score = self.performance_history[-1]
        
        if current_score >= 70:
            return "High pass chance", "green", "#ddffdd"
        elif current_score >= 60:
            return "Likely to pass", "darkgreen", "#eeffee"
        elif current_score >= 50:
            return "Borderline", "blue", "#ffffdd"
        elif current_score >= 40:
            return "Risk of failing", "orange", "#ffeeee"
        else:
            return "High fail chance", "red", "#ffdddd"
    
    def predict_trend(self):
        """Predict the performance trend based on recent data"""
        if len(self.performance_history) < 2:
            return "Not enough data", "black"
        
        # Use last 5 points for trend calculation
        x = np.array(self.time_steps[-5:])
        y = np.array(self.performance_history[-5:])
        
        if len(x) < 2:
            return "Not enough data", "black"
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 1.5:
            return "Rapid improvement 📈", "green"
        elif slope > 0.5:
            return "Improving ↗", "darkgreen"
        elif slope > -0.5:
            return "Stable ↔", "blue"
        elif slope > -1.5:
            return "Declining ↘", "orange"
        else:
            return "Rapid decline 📉", "red"
    
    def import_bulk_data(self, data_file):
        """Import bulk data from CSV/JSON file"""
        try:
            # Clear existing data
            self.performance_history = []
            self.time_steps = []
            self.current_time = 0
            
            if data_file.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(data_file)
                # Convert all columns to numeric, filling missing with 50
                for col in self.confirmed_parameters:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(50)
                    else:
                        df[col] = 50  # Default value if column missing
                
                for _, row in df.iterrows():
                    self.confirmed_parameters = {
                        'preparedness': min(max(row.get('preparedness', 50), 0), 100),
                        'teaching': min(max(row.get('teaching', 50), 0), 100),
                        'materials': min(max(row.get('materials', 50), 0), 100),
                        'participation': min(max(row.get('participation', 50), 0), 100),
                        'difficulty': min(max(row.get('difficulty', 50), 0), 100)
                    }
                    self.calculate_performance()
                    
            elif data_file.endswith('.json'):
                with open(data_file) as f:
                    data = json.load(f)
                    for entry in data:
                        self.confirmed_parameters = {
                            'preparedness': min(max(entry.get('preparedness', 50), 0), 100),
                            'teaching': min(max(entry.get('teaching', 50), 0), 100),
                            'materials': min(max(entry.get('materials', 50), 0), 100),
                            'participation': min(max(entry.get('participation', 50), 0), 100),
                            'difficulty': min(max(entry.get('difficulty', 50), 0), 100)
                        }
                        self.calculate_performance()
            
            self.save_parameters()
            return True, f"Successfully imported {len(self.performance_history)} records"
        
        except Exception as e:
            return False, f"Import failed: {str(e)}"

class SubjectEvaluationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subject Pass/Fail Predictor")
        self.root.geometry("1000x600")
        
        self.model = SubjectPerformanceModel()
        
        # Setup GUI
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls with fixed width
        control_frame = ttk.LabelFrame(main_frame, text="Evaluation Parameters", padding="10", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Configure grid for consistent layout
        for i in range(6):  # 5 parameters + button/status
            control_frame.grid_rowconfigure(i, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Parameter labels mapping
        param_labels = {
            'preparedness': "Student Preparedness",
            'teaching': "Teaching Effectiveness",
            'materials': "Study Materials",
            'participation': "Class Participation",
            'difficulty': "Subject Difficulty"
        }
        
        # Sliders for each parameter
        self.sliders = {}
        self.slider_vars = {}
        self.value_labels = {}
        
        for i, param in enumerate(self.model.confirmed_parameters):
            # Parameter label
            label = ttk.Label(control_frame, text=f"{param_labels[param]}:", anchor=tk.W)
            label.grid(row=i, column=0, sticky=tk.W, padx=(0, 5), pady=2)
            
            # Slider
            self.slider_vars[param] = tk.IntVar(value=self.model.pending_parameters[param])
            slider = ttk.Scale(
                control_frame,
                from_=0,
                to=100,
                variable=self.slider_vars[param],
                command=lambda v, p=param: self.slider_changed(p, v)
            )
            slider.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            self.sliders[param] = slider
            
            # Value label with fixed width
            self.value_labels[param] = ttk.Label(control_frame, text="50", width=3, anchor=tk.E)
            self.value_labels[param].grid(row=i, column=2, sticky=tk.E, padx=(0, 5), pady=2)
        
        # Confirm button
        self.confirm_btn = ttk.Button(
            control_frame,
            text="Confirm Parameters",
            command=self.confirm_parameters
        )
        self.confirm_btn.grid(row=5, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        # Pending changes label
        self.pending_changes_label = ttk.Label(
            control_frame, 
            text="No pending changes", 
            foreground="gray",
            wraplength=280
        )
        self.pending_changes_label.grid(row=6, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Info panel
        info_frame = ttk.LabelFrame(control_frame, text="Pass/Fail Prediction", padding="10")
        info_frame.grid(row=7, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        self.current_score_label = ttk.Label(info_frame, text="Pass Probability: -")
        self.current_score_label.pack(anchor=tk.W, pady=5)
        
        self.prediction_label = ttk.Label(
            info_frame, 
            text="Prediction: -", 
            font=('Helvetica', 10, 'bold'),
            padding=5
        )
        self.prediction_label.pack(fill=tk.X, pady=5)
        
        self.trend_label = ttk.Label(info_frame, text="Trend: -")
        self.trend_label.pack(anchor=tk.W, pady=5)
        
        self.last_update_label = ttk.Label(info_frame, text="Last update: Never")
        self.last_update_label.pack(anchor=tk.W, pady=5)
        
        # Bulk Import Section
        bulk_frame = ttk.LabelFrame(control_frame, text="Bulk Data Import", padding="10")
        bulk_frame.grid(row=8, column=0, columnspan=3, sticky=tk.EW, pady=10)

        self.file_path = tk.StringVar()
        ttk.Label(bulk_frame, text="File:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(bulk_frame, textvariable=self.file_path, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Store button references
        self.browse_btn = ttk.Button(bulk_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        self.import_btn = ttk.Button(bulk_frame, text="Import", command=self.import_data)
        self.import_btn.pack(side=tk.LEFT, padx=5)

        self.import_status = ttk.Label(control_frame, text="", foreground="gray")
        self.import_status.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Right panel - Graph
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 5))
        self.figure.set_facecolor('#f0f0f0')
        self.ax.set_title("Pass Probability Over Time")
        self.ax.set_xlabel("Time Steps")
        self.ax.set_ylabel("Pass Probability (%)")
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, marker='o', markersize=5)
        
        # Add threshold lines
        self.ax.axhline(y=70, color='green', linestyle='--', alpha=0.3)
        self.ax.axhline(y=60, color='darkgreen', linestyle='--', alpha=0.3)
        self.ax.axhline(y=50, color='blue', linestyle='--', alpha=0.3)
        self.ax.axhline(y=40, color='orange', linestyle='--', alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def slider_changed(self, param, value):
        """Handle slider changes (updates pending parameters)"""
        int_value = int(float(value))
        self.slider_vars[param].set(int_value)
        self.value_labels[param].config(text=str(int_value))
        
        # Update pending parameters
        self.model.update_pending_parameters({param: int_value})
        
        # Show pending changes
        pending_changes = []
        for p in self.model.confirmed_parameters:
            if self.model.confirmed_parameters[p] != self.model.pending_parameters[p]:
                pending_changes.append(p.replace('_', ' '))
        
        if pending_changes:
            self.pending_changes_label.config(
                text=f"Pending changes: {', '.join(pending_changes)}",
                foreground="blue"
            )
        else:
            self.pending_changes_label.config(text="No pending changes", foreground="gray")
    
    def confirm_parameters(self):
        """Confirm the current parameters and update the model"""
        changes = self.model.confirm_parameters()
        
        if changes:
            # Update the display with new data
            self.update_display()
            
            # Show confirmation message with changes
            messagebox.showinfo(
                "Parameters Confirmed",
                f"The following changes were applied:\n\n{changes}"
            )
        else:
            messagebox.showinfo(
                "No Changes",
                "No parameter changes were made"
            )
        
        # Reset pending changes display
        self.pending_changes_label.config(text="No pending changes", foreground="gray")
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        if filename:
            self.file_path.set(filename)

    def import_data(self):
        filename = self.file_path.get()
        if not filename:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        # Disable UI during import
        self.set_widgets_state('disabled')
        
        # Show loading message
        self.import_status.config(text="Importing data...", foreground="blue")
        self.root.update()
        
        # Process in background
        self.root.after(100, lambda: self.process_import(filename))

    def set_widgets_state(self, state):
        """Safely set state for widgets that support it"""
        widgets_to_disable = [
            *self.sliders.values(),
            self.confirm_btn,
            self.browse_btn,
            self.import_btn
        ]
        
        for widget in widgets_to_disable:
            try:
                widget.configure(state=state)
            except:
                pass  # Skip widgets that don't support state

    def process_import(self, filename):
        try:
            # Verify file exists
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File not found: {filename}")
                
            # Verify file extension
            if not (filename.endswith('.csv') or filename.endswith('.json')):
                raise ValueError("Invalid file type. Please use .csv or .json")
                
            success, message = self.model.import_bulk_data(filename)
            
            if success:
                self.import_status.config(text=message, foreground="green")
                # Force full display update
                self.update_display()
                # Explicitly redraw canvas
                self.canvas.draw()
                messagebox.showinfo("Success", message)
            else:
                raise Exception(message)
                
        except Exception as e:
            self.import_status.config(text=str(e), foreground="red")
            messagebox.showerror("Import Error", str(e))
        finally:
            # Re-enable UI
            self.set_widgets_state('normal')
    
    def update_display(self):
        """Update all displays with current model data"""
        # Update score and prediction
        if self.model.performance_history:
            current_score = self.model.performance_history[-1]
            prediction, text_color, bg_color = self.model.predict_pass_fail()
            trend, trend_color = self.model.predict_trend()
            
            self.current_score_label.config(
                text=f"Pass Probability: {current_score:.1f}%",
                foreground=text_color
            )
            self.prediction_label.config(
                text=f"Prediction: {prediction}",
                foreground=text_color,
                background=bg_color
            )
            self.trend_label.config(
                text=f"Trend: {trend}",
                foreground=trend_color
            )
            self.last_update_label.config(
                text=f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            self.current_score_label.config(text="Pass Probability: -")
            self.prediction_label.config(text="Prediction: -", background="white")
            self.trend_label.config(text="Trend: -")
            self.last_update_label.config(text="Last update: Never")
        
        # Update graph
        if self.model.time_steps and self.model.performance_history:
            self.line.set_data(self.model.time_steps, self.model.performance_history)
            self.ax.set_xlim(0, max(self.model.time_steps) + 1 if len(self.model.time_steps) > 1 else 2)
            self.ax.set_ylim(0, 100)
            self.canvas.draw()
    
    def on_closing(self):
        """Handle window closing"""
        self.model.save_parameters()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SubjectEvaluationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()