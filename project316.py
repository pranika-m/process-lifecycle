import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import random
from matplotlib.animation import FuncAnimation

class ProcessVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Visualization Tool")
        self.root.geometry("1400x900")
        
        self.processes = []
        self.all_processes = []
        self.state_colors = {
            'New': '#FF9999', 'Ready': '#99FF99', 'Running': '#9999FF',
            'Waiting': '#FFFF99', 'Terminated': '#CC99FF'
        }
        
        # Main canvas with scrollbars
        self.main_canvas = tk.Canvas(self.root)
        self.v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.root, orient="horizontal", command=self.main_canvas.xview)
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame inside the canvas
        self.main_frame = ttk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # Configure main_frame with three columns for centering
        self.main_frame.grid_columnconfigure(0, weight=1)  # Left gap
        self.main_frame.grid_columnconfigure(1, weight=0)  # Content
        self.main_frame.grid_columnconfigure(2, weight=1)  # Right gap
        
        # Top section: Controls and Process Table
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Control Panel (left)
        self.control_panel = ttk.LabelFrame(self.top_frame, text="Control Panel", padding="5")
        self.control_panel.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        
        # Process Table (right)
        self.table_panel = ttk.LabelFrame(self.top_frame, text="Process Table", padding="5")
        self.table_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Bottom section: Visualizations (hidden initially)
        self.visual_frame = ttk.Frame(self.main_frame)
        self.visual_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.visual_frame.grid_remove()  # Initially hidden
        
        # Create UI components
        self.create_controls(self.control_panel)
        self.create_process_table(self.table_panel)
        self.create_visualizations(self.visual_frame)
        
        # Configure grid weights
        self.main_frame.grid_rowconfigure(0, weight=0)  # Top frame sizes to content
        self.main_frame.grid_rowconfigure(1, weight=1)  # Visual frame expands vertically
        self.top_frame.grid_columnconfigure(1, weight=1)  # Table panel expands horizontally
        
        # Bind canvas scrolling
        self.main_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

    def create_controls(self, parent):
        """Create input fields, buttons, and ready queue display."""
        fields = ["PID", "Arrival Time", "Burst Time", "Priority"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(parent, text=f"{field}:").grid(row=i, column=0, pady=2, sticky="w")
            entry = ttk.Entry(parent, width=20)
            entry.grid(row=i, column=1, pady=2, sticky="ew")
            self.entries[field] = entry
        
        ttk.Label(parent, text="Algorithm:").grid(row=4, column=0, pady=2, sticky="w")
        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_combo = ttk.Combobox(parent, textvariable=self.algo_var, 
                                      values=["FCFS", "SJF", "RR", "Priority", "SRTF"], width=20)
        self.algo_combo.grid(row=4, column=1, pady=2, sticky="ew")
        self.algo_combo.bind("<<ComboboxSelected>>", self.toggle_quantum)
        
        ttk.Label(parent, text="Quantum (RR):").grid(row=5, column=0, pady=2, sticky="w")
        self.quantum_entry = ttk.Entry(parent, state="disabled", width=20)
        self.quantum_entry.grid(row=5, column=1, pady=2, sticky="ew")
        self.quantum_entry.insert(0, "2")
        
        ttk.Label(parent, text="Animation Speed (ms):").grid(row=6, column=0, pady=2, sticky="w")
        self.speed_entry = ttk.Entry(parent, width=20)
        self.speed_entry.grid(row=6, column=1, pady=2, sticky="ew")
        self.speed_entry.insert(0, "500")
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Add Process", command=self.add_process).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Random", command=self.generate_random).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Simulate", command=self.start_simulation).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_all).grid(row=0, column=3, padx=5)
        
        # Ready Queue display
        self.ready_frame = ttk.LabelFrame(parent, text="Ready Queue", padding="5")
        self.ready_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="nsew")
        self.ready_queue_list = tk.Listbox(self.ready_frame, height=5, width=25)
        self.ready_queue_list.pack(fill="both", expand=True)

    def toggle_quantum(self, event=None):
        """Enable/disable quantum entry based on algorithm."""
        self.quantum_entry.config(state="normal" if self.algo_var.get() == "RR" else "disabled")

    def create_process_table(self, parent):
        """Create the process table with scrollbars."""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, 
                                 columns=("PID", "AT", "BT", "Priority", "State", "TAT", "WT"), 
                                 show="headings")
        self.table.heading("PID", text="PID")
        self.table.heading("AT", text="Arrival")
        self.table.heading("BT", text="Burst")
        self.table.heading("Priority", text="Priority")
        self.table.heading("State", text="State")
        self.table.heading("TAT", text="TAT")
        self.table.heading("WT", text="Waiting")
        self.table.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        vsb.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=vsb.set)

    def create_visualizations(self, parent):
        """Create visualizations with titles and proper alignment."""
        gantt_frame = ttk.LabelFrame(parent, text="Gantt Chart", padding="5")
        gantt_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        self.gantt_fig, self.gantt_ax = plt.subplots(figsize=(12, 3))
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_fig, master=gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill="both", expand=True)
        gantt_toolbar_frame = ttk.Frame(gantt_frame)
        gantt_toolbar_frame.pack(fill="x")
        self.gantt_toolbar = NavigationToolbar2Tk(self.gantt_canvas, gantt_toolbar_frame)
        
        state_frame = ttk.LabelFrame(parent, text="Process State Diagram", padding="5")
        state_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.state_fig, self.state_ax = plt.subplots(figsize=(12, 3))
        self.state_canvas = FigureCanvasTkAgg(self.state_fig, master=state_frame)
        self.state_canvas.get_tk_widget().pack(fill="both", expand=True)
        state_toolbar_frame = ttk.Frame(state_frame)
        state_toolbar_frame.pack(fill="x")
        self.state_toolbar = NavigationToolbar2Tk(self.state_canvas, state_toolbar_frame)
        
        queue_frame = ttk.LabelFrame(parent, text="Process Queues", padding="5")
        queue_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        self.queue_fig, self.queue_ax = plt.subplots(figsize=(12, 2))
        self.queue_canvas = FigureCanvasTkAgg(self.queue_fig, master=queue_frame)
        self.queue_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding="10")
        self.metrics_frame.grid(row=3, column=0, sticky="nsew", pady=5)

    def add_process(self):
        """Add a process to the table."""
        try:
            pid = self.entries["PID"].get()
            at = float(self.entries["Arrival Time"].get())
            bt = float(self.entries["Burst Time"].get())
            priority = float(self.entries["Priority"].get())
            
            if not pid or at < 0 or bt <= 0 or priority < 0:
                raise ValueError("Invalid input values")
            
            process = {
                'pid': pid, 'arrival': at, 'burst': bt, 'priority': priority,
                'remaining': bt, 'state': 'New', 'states': [(0, 'New')],
                'first_run': None, 'completion': None
            }
            self.processes.append(process)
            self.update_table()
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def generate_random(self):
        """Generate random processes."""
        self.processes.clear()
        for i in range(5):
            bt = random.uniform(1, 10)
            process = {
                'pid': f"P{i}", 'arrival': random.uniform(0, 5),
                'burst': bt, 'priority': random.randint(1, 5),
                'remaining': bt, 'state': 'New', 'states': [(0, 'New')],
                'first_run': None, 'completion': None
            }
            self.processes.append(process)
        self.update_table()

    def update_table(self, time=None):
        """Update the process table dynamically."""
        for item in self.table.get_children():
            self.table.delete(item)
        process_list = self.all_processes if self.all_processes else self.processes
        self.table['height'] = max(len(process_list), 1)  # Dynamic height, min 1
        for p in process_list:
            if time is None:
                state = p['state']
            else:
                state = self.get_state_at_time(p, time)
            tat = f"{p['tat']:.2f}" if 'tat' in p else '-'
            wt = f"{p['wt']:.2f}" if 'wt' in p else '-'
            self.table.insert("", "end", values=(p['pid'], f"{p['arrival']:.2f}", f"{p['burst']:.2f}", p['priority'], state, tat, wt))

    def get_state_at_time(self, process, time):
        """Get the state of a process at a specific time."""
        for t, s in reversed(process['states']):
            if t <= time:
                return s
        return 'New'

    def start_simulation(self):
        """Run the simulation and show visualizations."""
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to simulate")
            return
        
        self.visual_frame.grid()
        self.all_processes = list(self.processes)
        self.color_map = {}
        colors = plt.cm.tab10.colors
        for i, p in enumerate(self.all_processes):
            self.color_map[p['pid']] = colors[i % len(colors)]
        
        self.current_time = 0
        self.gantt_data = []
        self.ready_queue = []
        self.running_process = None
        self.processes = sorted(self.processes, key=lambda x: x['arrival'])
        self.simulation_steps = []
        self.execution_order = []
        
        algorithm = self.algo_var.get()
        self.quantum = float(self.quantum_entry.get()) if algorithm == "RR" else None
        self.algorithm = algorithm
        
        prev_running = None
        while self.processes or self.ready_queue or self.running_process:
            arrived = [p for p in self.processes if p['arrival'] <= self.current_time]
            for p in arrived:
                p['state'] = 'Ready'
                p['states'].append((self.current_time, 'Ready'))
                self.ready_queue.append(p)
                self.processes.remove(p)
            
            if self.running_process and self.algorithm == "SRTF" and self.ready_queue:
                min_ready = min(self.ready_queue, key=lambda x: x['remaining'])
                if min_ready['remaining'] < self.running_process['remaining']:
                    self.running_process['state'] = 'Ready'
                    self.running_process['states'].append((self.current_time, 'Ready'))
                    self.ready_queue.append(self.running_process)
                    self.running_process = min_ready
                    self.ready_queue.remove(min_ready)
                    self.running_process['state'] = 'Running'
                    self.running_process['states'].append((self.current_time, 'Running'))
            
            if not self.running_process and self.ready_queue:
                self.select_next_process()
            
            if self.running_process != prev_running:
                if self.running_process:
                    self.execution_order.append(self.running_process['pid'])
                prev_running = self.running_process
            
            if self.running_process:
                if self.running_process['first_run'] is None:
                    self.running_process['first_run'] = self.current_time
                
                self.running_process['remaining'] -= 1
                self.gantt_data.append({
                    'pid': self.running_process['pid'],
                    'start': self.current_time,
                    'end': self.current_time + 1
                })
                
                if self.running_process['remaining'] <= 0:
                    self.running_process['completion'] = self.current_time + 1
                    self.running_process['state'] = 'Terminated'
                    self.running_process['states'].append((self.current_time + 1, 'Terminated'))
                    self.running_process['tat'] = self.running_process['completion'] - self.running_process['arrival']
                    self.running_process['wt'] = self.running_process['tat'] - self.running_process['burst']
                    self.running_process = None
                elif self.algorithm == "RR" and (self.current_time - self.gantt_data[-1]['start']) >= self.quantum:
                    self.running_process['state'] = 'Ready'
                    self.running_process['states'].append((self.current_time, 'Ready'))
                    self.ready_queue.append(self.running_process)
                    self.running_process = None
            
            state = {
                'time': self.current_time,
                'gantt_data': list(self.gantt_data),
                'ready_queue': [p['pid'] for p in self.ready_queue],
                'running_process': self.running_process['pid'] if self.running_process else None
            }
            self.simulation_steps.append(state)
            self.current_time += 1
        
        # Ensure final table update to show all processes as Terminated
        self.update_table()
        
        self.calculate_metrics()
        
        interval = int(self.speed_entry.get())
        self.anim = FuncAnimation(self.gantt_fig, self.update_gantt, frames=range(len(self.simulation_steps)), 
                                 interval=interval, repeat=False, cache_frame_data=False)
        self.state_anim = FuncAnimation(self.state_fig, self.update_states, frames=range(len(self.simulation_steps)), 
                                       interval=interval, repeat=False, cache_frame_data=False)
        self.queue_anim = FuncAnimation(self.queue_fig, self.update_queues, frames=range(len(self.simulation_steps)), 
                                       interval=interval, repeat=False, cache_frame_data=False)
        self.gantt_canvas.draw()
        self.state_canvas.draw()
        self.queue_canvas.draw()

    def select_next_process(self):
        """Select the next process based on the algorithm."""
        if not self.ready_queue:
            return
        
        if self.algorithm == "FCFS":
            self.running_process = self.ready_queue.pop(0)
        elif self.algorithm == "SJF" or self.algorithm == "SRTF":
            self.running_process = min(self.ready_queue, key=lambda x: x['remaining'])
            self.ready_queue.remove(self.running_process)
        elif self.algorithm == "RR":
            self.running_process = self.ready_queue.pop(0)
        elif self.algorithm == "Priority":
            self.running_process = min(self.ready_queue, key=lambda x: x['priority'])
            self.ready_queue.remove(self.running_process)
        
        self.running_process['state'] = 'Running'
        self.running_process['states'].append((self.current_time, 'Running'))

    def show_execution_order(self):
        """Show execution order in the ready queue listbox."""
        self.ready_frame.config(text="Execution Order")
        self.ready_queue_list.delete(0, tk.END)
        for pid in self.execution_order:
            self.ready_queue_list.insert(tk.END, pid)

    def update_gantt(self, frame):
        """Update the Gantt chart during animation."""
        self.gantt_ax.clear()
        state = self.simulation_steps[frame]
        gantt_data = state['gantt_data']
        for entry in gantt_data:
            self.gantt_ax.broken_barh([(entry['start'], entry['end'] - entry['start'])], 
                                     (0, 1), facecolors=self.color_map[entry['pid']])
            self.gantt_ax.text(entry['start'] + (entry['end'] - entry['start'])/2, 
                              0.5, entry['pid'], ha='center', va='center')
        
        self.gantt_ax.set_ylim(0, 1)
        self.gantt_ax.set_xlim(0, state['time'] + 1)
        self.gantt_ax.set_title("Gantt Chart")
        self.gantt_ax.set_yticks([])
        self.gantt_canvas.draw()
        
        self.update_table(state['time'])
        self.ready_queue_list.delete(0, tk.END)
        for pid in state['ready_queue']:
            self.ready_queue_list.insert(tk.END, pid)
        
        if frame == len(self.simulation_steps) - 1:
            self.show_execution_order()

    def update_states(self, frame):
        """Update the state diagram during animation."""
        self.state_ax.clear()
        state = self.simulation_steps[frame]
        current_time = state['time']
        self.state_ax.set_title("Process States")
        self.state_ax.set_ylim(-0.5, len(self.all_processes) - 0.5)
        self.state_ax.set_xlim(0, max(p.get('completion', current_time) for p in self.all_processes) + 1)
        
        for i, p in enumerate(self.all_processes):
            for j, (time, state_name) in enumerate(p['states']):
                if time > current_time:
                    break
                next_time = p['states'][j + 1][0] if j + 1 < len(p['states']) else (current_time if state_name != 'Terminated' else time + 1)
                duration = min(next_time, current_time) - time
                if duration > 0:
                    self.state_ax.barh(i, duration, left=time, height=0.8, align='center', 
                                      color=self.state_colors[state_name])
                    if duration > 1:
                        self.state_ax.text(time + duration / 2, i, state_name, ha='center', va='center', fontsize=8)
        
        self.state_ax.set_yticks(range(len(self.all_processes)))
        self.state_ax.set_yticklabels([p['pid'] for p in self.all_processes])
        self.state_canvas.draw()

    def update_queues(self, frame):
        """Update the process queue display during animation."""
        self.queue_ax.clear()
        state = self.simulation_steps[frame]
        ready_queue = state['ready_queue']
        running_process = state['running_process']
        self.queue_ax.set_title("Process Queues")
        self.queue_ax.set_ylim(0, 3)
        self.queue_ax.set_xlim(0, max(5, len(ready_queue) + 1))
        
        for i, pid in enumerate(ready_queue):
            self.queue_ax.add_patch(plt.Rectangle((i, 1), 0.8, 0.8, facecolor=self.state_colors['Ready']))
            self.queue_ax.text(i + 0.4, 1.4, pid, ha='center', va='center')
        
        if running_process:
            self.queue_ax.add_patch(plt.Rectangle((0, 2), 0.8, 0.8, facecolor=self.state_colors['Running']))
            self.queue_ax.text(0.4, 2.4, running_process, ha='center', va='center')
        
        self.queue_ax.set_yticks([1.4, 2.4])
        self.queue_ax.set_yticklabels(['Ready', 'Running'])
        self.queue_ax.set_xticks([])
        self.queue_canvas.draw()

    def calculate_metrics(self):
        """Calculate and display performance metrics."""
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        total_time = max(p['completion'] for p in self.all_processes)
        avg_tat = sum(p['tat'] for p in self.all_processes) / len(self.all_processes)
        avg_wt = sum(p['wt'] for p in self.all_processes) / len(self.all_processes)
        cpu_util = sum(p['burst'] for p in self.all_processes) / total_time * 100
        throughput = len(self.all_processes) / total_time
        
        metrics = [
            f"Avg TAT: {avg_tat:.2f}",
            f"Avg WT: {avg_wt:.2f}",
            f"CPU Util: {cpu_util:.2f}%",
            f"Throughput: {throughput:.2f} proc/unit"
        ]
        
        for i, metric in enumerate(metrics):
            ttk.Label(self.metrics_frame, text=metric).grid(row=0, column=i, padx=10)

    def clear_all(self):
        """Reset the interface and hide visualizations."""
        self.processes.clear()
        self.all_processes.clear()
        self.update_table()
        self.state_ax.clear()
        self.gantt_ax.clear()
        self.queue_ax.clear()
        self.state_canvas.draw()
        self.gantt_canvas.draw()
        self.queue_canvas.draw()
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        if hasattr(self, 'anim') and self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None
        if hasattr(self, 'state_anim') and self.state_anim is not None:
            self.state_anim.event_source.stop()
            self.state_anim = None
        if hasattr(self, 'queue_anim') and self.queue_anim is not None:
            self.queue_anim.event_source.stop()
            self.queue_anim = None
        self.ready_queue_list.delete(0, tk.END)
        self.ready_frame.config(text="Ready Queue")
        self.visual_frame.grid_remove()

def main():
    root = tk.Tk()
    app = ProcessVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()