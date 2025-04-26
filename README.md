
# Process Life-Cycle Visualization GUI: 

## Why We Built This GUI

Imagine your computer as a chef juggling a busy kitchen, picking which dish to cook first. That’s CPU scheduling, and our Process Visualization GUI makes it a blast to explore! This Python-based graphical interface turns complex operating system concepts into lively, colorful visuals. It’s perfect for students or tech enthusiasts who want to see how processes get managed without slogging through dense textbooks.

Why visualize? Watching processes flow from “waiting” to “running” to “done” makes learning intuitive and exciting. It’s like seeing the CPU’s hidden dance come to life!

# Features
- Robust Scheduling Algorithms:
    - First-Come, First-Served (FCFS): Executes processes in arrival order, showcasing the simplicity of queue-based scheduling.
    - Shortest Job First (SJF): Optimizes for minimal completion times by prioritizing the shortest tasks, ideal for studying non-preemptive strategies.
    - Round Robin (RR): Demonstrates fair time-sharing with configurable time quanta, perfect for exploring preemptive scheduling dynamics.
    - Priority Scheduling: Highlights priority-driven execution, allowing analysis of how high-priority tasks influence performance
    - Shortest Remaining Time First (SRTF): Illustrates preemptive efficiency by dynamically selecting the task with the least remaining time.

- Intuitive Graphical Interface:





    - Define processes with precise attributes (PID, arrival time, burst time, and priority for Priority scheduling) to simulate real-world scenarios.



    - Generate randomized process sets with a single click to quickly experiment with diverse workloads.



    - Track process execution in a real-time table, displaying critical metrics like completion time, turnaround time, and waiting time.



- Insightful Visualizations:





    - Gantt Chart: Maps the CPU’s scheduling timeline, providing a clear view of process execution order and duration.



    - State Diagram: Uses vibrant colors to trace each process’s state transitions (New, Ready, Running, Waiting, Terminated), revealing scheduling behavior.



    - Queue Display: Visualizes the ready queue and active process, offering a window into the CPU’s decision-making process.



    - Performance Metrics: Quantifies efficiency with metrics like average turnaround time, waiting time, CPU utilization, and throughput, enabling deep analysis.



    - Flexible Customization: Adjust animation speed to study scheduling at your own pace and fine-tune the Round Robin time quantum to investigate its impact on performance.

## Requirements





- Python: 3.6 or later.



# Libraries:





        tkinter (included with Python for the GUI)

        matplotlib (install via pip install matplotlib for visualizations).



# Platforms:
- Windows, macOS, or Linux.

# Getting Started





- Clone or download the project:

        git clone <repository-url>
        cd process-visualization-gui



- Install the visualization library:

        pip install matplotlib



- Launch the GUI:

        python process_visualizer.py


# How to Use





- Open the GUI: Run the script to start the interface.



- Create Processes: Enter details like name, arrival time, duration, and priority (if needed) or click Random for quick samples.



 - Choose an Algorithm: Select FCFS, SJF, RR, Priority, or SRTF from the dropdown menu.



- Run the Simulation: Click Simulate to watch animated charts and diagrams in action.



- View Insights: Check the table for live updates and stats for performance metrics.



- Start Fresh: Click Clear to reset everything.


# Notes





- Works best with a small set of processes for clear, uncluttered visuals.



- Requires valid inputs (no negative times or missing priorities for Priority mode).



- Designed for educational purposes, not real-world CPU management.

# Feedback

Have a suggestion or spot a bug? Open an issue on the repository or reach out to pranika.m1656@gmail.com 
Let’s make this GUI even more awesome!
