from flask import Flask, request, jsonify
from flask_cors import CORS
import sys # For printing to stderr for debug clarity

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Root route for basic health check
@app.route('/')
def home():
    return "✅ CPU Scheduling Simulator Backend is running!"

# Helper function to calculate metrics
# This function now expects 'original_processes' to be the processes list in the order
# they were provided by the frontend, so metrics align correctly.
def calculate_metrics(original_processes, execution_order):
    n = len(original_processes)
    if n == 0:
        return {
            'waiting_time': [],
            'turnaround_time': [],
            'avg_waiting_time': 0,
            'avg_turnaround_time': 0,
            'total_time': 0,
            'completion_time': []
        }

    # Initialize lists, aligned with the original_processes order
    waiting_time = [0] * n
    turnaround_time = [0] * n
    completion_time = [0] * n
    
    # Map PIDs to their final completion times from the execution order
    process_final_completion_time = {}
    for block in execution_order:
        process_final_completion_time[block['pid']] = block['end']
    
    # Calculate metrics based on the original process order
    for i, proc in enumerate(original_processes):
        pid = proc['pid']
        # The completion time is the last 'end' time of any segment for this PID
        completion_time[i] = process_final_completion_time.get(pid, 0)
        
        turnaround_time[i] = completion_time[i] - proc['arrival']
        waiting_time[i] = turnaround_time[i] - proc['burst']
        
        # Ensure waiting time is non-negative
        if waiting_time[i] < 0:
            waiting_time[i] = 0
    
    avg_waiting_time = sum(waiting_time) / n
    avg_turnaround_time = sum(turnaround_time) / n
    total_time = max(block['end'] for block in execution_order) if execution_order else 0

    return {
        'waiting_time': waiting_time,
        'turnaround_time': turnaround_time,
        'avg_waiting_time': avg_waiting_time,
        'avg_turnaround_time': avg_turnaround_time,
        'total_time': total_time,
        'completion_time': completion_time
    }

# Simulation logic functions, now only return execution_order
def simulate_fcfs_logic(processes_copy): # Renamed to clearly indicate it's a working copy
    # FCFS: Sort processes by arrival time (on the copy)
    processes_copy.sort(key=lambda x: x['arrival'])
    execution_order = []
    current_time = 0
    
    for proc in processes_copy:
        start_time = max(current_time, proc['arrival'])
        end_time = start_time + proc['burst']
        
        execution_order.append({
            'pid': proc['pid'],
            'start': start_time,
            'end': end_time,
            'duration': proc['burst']
        })
        current_time = end_time
    return execution_order

def simulate_sjf_logic(processes_copy):
    execution_order = []
    current_time = 0
    n = len(processes_copy)
    completed_count = 0
    
    # Track processes that are not yet completed
    active_processes = {p['pid']: dict(p) for p in processes_copy} # Use dict copy to prevent modifying original
    
    while completed_count < n:
        # Find all processes that have arrived and not yet completed
        available_pids = [pid for pid, p_data in active_processes.items()
                           if p_data['arrival'] <= current_time and 'completed' not in p_data]
        
        if not available_pids:
            # If no processes are available, increment time (CPU is idle)
            # Find the next earliest arrival time among non-completed processes
            next_arrival_time = float('inf')
            remaining_pids = [pid for pid, p_data in active_processes.items() if 'completed' not in p_data]
            if remaining_pids:
                next_arrival_time = min(active_processes[pid]['arrival'] for pid in remaining_pids)

            if next_arrival_time == float('inf') or next_arrival_time > current_time:
                # Advance time to next arrival or just by 1 if no more arrivals and queue is empty
                time_to_advance = max(1, next_arrival_time - current_time) if next_arrival_time != float('inf') else 1
                current_time += time_to_advance
                continue
            else: # Should not happen if logic is perfect, but for safety against infinite loop
                current_time += 1 # Advance by 1 if there's an immediate arrival not caught
                continue # Re-evaluate queue

        # Select the process with the shortest burst time among available ones
        # If burst times are equal, tie-break by arrival time, then PID (for consistency)
        selected_pid = min(available_pids, key=lambda pid: (active_processes[pid]['burst'], active_processes[pid]['arrival'], pid))
        current_process_data = active_processes[selected_pid]
        
        start_time = current_time
        end_time = start_time + current_process_data['burst']
        
        execution_order.append({
            'pid': current_process_data['pid'],
            'start': start_time,
            'end': end_time,
            'duration': current_process_data['burst']
        })
        
        current_time = end_time
        
        # Mark the process as completed
        active_processes[selected_pid]['completed'] = True
        completed_count += 1
        
    return execution_order

def simulate_priority_logic(processes_copy, priorities):
    # Associate priority with each process in the copy
    for i, proc in enumerate(processes_copy):
        proc['priority'] = priorities[i] # This modifies the copy, which is fine
    
    execution_order = []
    current_time = 0
    n = len(processes_copy)
    completed_count = 0
    
    active_processes = {p['pid']: dict(p) for p in processes_copy}

    while completed_count < n:
        available_pids = [pid for pid, p_data in active_processes.items() 
                           if p_data['arrival'] <= current_time and 'completed' not in p_data]
        
        if not available_pids:
            # Similar idle time handling as SJF
            next_arrival_time = float('inf')
            remaining_pids = [pid for pid, p_data in active_processes.items() if 'completed' not in p_data]
            if remaining_pids:
                next_arrival_time = min(active_processes[pid]['arrival'] for pid in remaining_pids)

            if next_arrival_time == float('inf') or next_arrival_time > current_time:
                time_to_advance = max(1, next_arrival_time - current_time) if next_arrival_time != float('inf') else 1
                current_time += time_to_advance
                continue
            else:
                current_time += 1
                continue
        
        # Select process with the highest priority (lowest priority number)
        # Tie-break by arrival time, then PID
        selected_pid = min(available_pids, key=lambda pid: (active_processes[pid]['priority'], active_processes[pid]['arrival'], pid))
        current_process_data = active_processes[selected_pid]
        
        start_time = current_time
        end_time = start_time + current_process_data['burst']
        
        execution_order.append({
            'pid': current_process_data['pid'],
            'start': start_time,
            'end': end_time,
            'duration': current_process_data['burst']
        })
        
        current_time = end_time
        
        active_processes[selected_pid]['completed'] = True
        completed_count += 1
        
    return execution_order

def simulate_rr_logic(processes_copy, quantum):
    # Prepare processes with mutable state
    process_states = {p['pid']: dict(p) for p in processes_copy}
    for pid in process_states:
        process_states[pid]['remaining'] = process_states[pid]['burst']
        process_states[pid]['completed'] = False
        process_states[pid]['in_queue'] = False # Custom flag to prevent duplicate queueing

    execution_order = []
    ready_queue_pids = [] # Stores PIDs in the ready queue
    current_time = 0
    idle_time = 0
    
    # Set of PIDs that haven't been completed yet
    remaining_pids_overall = {p['pid'] for p in processes_copy}

    while remaining_pids_overall:
        # Add processes that have arrived and are not yet in the queue or completed
        newly_arrived_and_not_queued = []
        for pid in remaining_pids_overall:
            proc = process_states[pid]
            if not proc['completed'] and not proc['in_queue'] and proc['arrival'] <= current_time:
                newly_arrived_and_not_queued.append(pid)
        
        # Sort newly arrived for deterministic queue order (by arrival, then pid)
        newly_arrived_and_not_queued.sort(key=lambda pid: (process_states[pid]['arrival'], pid))

        for pid in newly_arrived_and_not_queued:
            if not process_states[pid]['in_queue'] and not process_states[pid]['completed']: # Double check before adding
                ready_queue_pids.append(pid)
                process_states[pid]['in_queue'] = True

        if not ready_queue_pids:
            # If queue is empty, CPU is idle. Find the next event (earliest arrival).
            next_arrival_time = float('inf')
            for pid in remaining_pids_overall:
                proc = process_states[pid]
                if not proc['completed'] and not proc['in_queue'] and proc['arrival'] > current_time:
                    next_arrival_time = min(next_arrival_time, proc['arrival'])
            
            if next_arrival_time == float('inf'): # No more arrivals and queue is empty, so all must be done
                break # All processes finished

            # Advance time to the next arrival
            time_to_advance = next_arrival_time - current_time
            if time_to_advance > 0:
                idle_time += time_to_advance
                current_time = next_arrival_time
            continue # Re-evaluate queue after time advance

        # Get process from front of the queue
        current_pid = ready_queue_pids.pop(0)
        current_proc = process_states[current_pid]
        current_proc['in_queue'] = False # Process taken from queue

        # Determine time slice to execute
        time_slice = min(quantum, current_proc['remaining'])
        
        start_exec_time = current_time
        end_exec_time = current_time + time_slice
        
        execution_order.append({
            'pid': current_proc['pid'],
            'start': start_exec_time,
            'end': end_exec_time,
            'duration': time_slice
        })
        
        current_time = end_exec_time
        current_proc['remaining'] -= time_slice

        # Add any processes that arrive during this execution slice
        newly_arrived_during_slice = []
        for pid in remaining_pids_overall:
            proc = process_states[pid]
            # Process must not be completed, not in queue, and arrived during this slice
            if not proc['completed'] and not proc['in_queue'] and \
               proc['arrival'] > start_exec_time and proc['arrival'] <= current_time:
                newly_arrived_during_slice.append(pid)
        
        newly_arrived_during_slice.sort(key=lambda pid: (process_states[pid]['arrival'], pid))
        
        # Insert newly arrived processes into the queue before re-adding current process if applicable
        for pid in newly_arrived_during_slice:
            if not process_states[pid]['in_queue'] and not process_states[pid]['completed']:
                ready_queue_pids.append(pid)
                process_states[pid]['in_queue'] = True

        # Re-queue if not finished, or mark as completed
        if current_proc['remaining'] > 0:
            if not current_proc['in_queue']: # Ensure it's not already somehow re-queued by arrival logic
                ready_queue_pids.append(current_pid)
                current_proc['in_queue'] = True
        else:
            current_proc['completed'] = True
            if current_pid in remaining_pids_overall: # Remove from tracking set
                remaining_pids_overall.remove(current_pid)

    return execution_order, idle_time

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    algorithm = data['algorithm']
    pids = data['pids']
    arrival = data['arrival']
    burst = data['burst']
    
    # Create the original list of processes. This list's order is preserved
    # and used for calculating and presenting metrics consistently.
    original_processes_for_metrics = [{
        'pid': pid,
        'arrival': arr,
        'burst': bur
    } for pid, arr, bur in zip(pids, arrival, burst)]

    execution_order = []
    idle_time = 0 # Only RR uses this explicitly

    try:
        # Determine which simulation logic to run
        if algorithm == 'fcfs':
            execution_order = simulate_fcfs_logic(original_processes_for_metrics.copy())
        elif algorithm == 'sjf':
            execution_order = simulate_sjf_logic(original_processes_for_metrics.copy())
        elif algorithm == 'priority':
            priority = data.get('priority')
            if priority is None:
                return jsonify({'error': 'Priority values are required for Priority Scheduling'}), 400
            execution_order = simulate_priority_logic(original_processes_for_metrics.copy(), priority)
        elif algorithm == 'rr':
            quantum = data.get('quantum')
            if quantum is None:
                return jsonify({'error': 'Time quantum is required for Round Robin'}), 400
            execution_order, idle_time = simulate_rr_logic(original_processes_for_metrics.copy(), quantum)
        else:
            return jsonify({'error': 'Invalid algorithm specified'}), 400
        
        # Calculate metrics using the original processes list and the derived execution order
        metrics = calculate_metrics(original_processes_for_metrics, execution_order)
        
        # Add idle time if relevant (from RR)
        if algorithm == 'rr':
            metrics['idle_time'] = idle_time
        
        # Return the response, always using the original processes list for consistency on frontend
        return jsonify({
            'processes': original_processes_for_metrics,
            'execution_order': execution_order, # Can be used for Gantt chart
            'gantt': execution_order, # Redundant, but kept for compatibility with frontend code
            **metrics
        })
    except Exception as e:
        # Catch any exceptions that occur during simulation and return a proper error response
        print(f"An error occurred during simulation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr) # Print full traceback for detailed debugging
        return jsonify({'error': f'Backend simulation error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

