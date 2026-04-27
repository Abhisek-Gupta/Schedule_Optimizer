import mysql.connector
import pandas as pd
import collections
import random
import time
import math

# ==========================================
# 1. CONFIGURATION & DOMAINS
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          
    'password': 'password',  
    'database': 'IITP_Timetable'
}

DAYS = 5
SLOTS_PER_DAY = 8
TOTAL_SLOTS = DAYS * SLOTS_PER_DAY

IDE_SLOTS = [4, 12, 20, 28, 36]

def get_valid_starts(duration):
    if duration == 0: return []
    valid = []
    for d in range(DAYS):
        base = d * SLOTS_PER_DAY
        for s in range(4 - duration + 1): 
            valid.append(base + s)
        for s in range(4, 8 - duration + 1): 
            valid.append(base + s)
    return valid

class Event:
    def __init__(self, e_id, course, e_type, duration, valid_rooms, valid_times, faculties):
        self.id = e_id
        self.course = course
        self.type = e_type
        self.duration = duration
        self.valid_rooms = valid_rooms
        self.valid_times = valid_times
        self.faculties = faculties 

# ==========================================
# 2. DATA EXTRACTION (Same as before)
# ==========================================
def fetch_and_build_context(conn):
    print("Fetching Master Data...")
    rooms_df = pd.read_sql("SELECT Room_name, Capacity, Type, Department FROM classrooms_labs", conn)
    classrooms = rooms_df[rooms_df['Type'] == 'CLASSROOM']
    labs = rooms_df[rooms_df['Type'] == 'LAB']
    
    enroll_df = pd.read_sql("SELECT Roll_no, Course_ID FROM student_course_enrollment", conn)
    course_sizes = enroll_df.groupby('Course_ID').size().to_dict()
    
    print("Building Student Conflict Graph...")
    conflict_edges = set()
    student_courses = enroll_df.groupby('Roll_no')['Course_ID'].apply(list).to_dict()
    for courses in student_courses.values():
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                if courses[i] != courses[j]:
                    conflict_edges.add(tuple(sorted([courses[i], courses[j]])))

    stage1_df = pd.read_sql("SELECT * FROM stage1_timetable", conn)
    stage1_courses = set(stage1_df['Course_ID'].tolist())
    
    blocked_slots = {'rooms': set(), 'faculties': set()}
    for _, row in stage1_df.iterrows():
        for s in range(row['Start_Slot'], row['Start_Slot'] + row['Duration']):
            blocked_slots['rooms'].add((row['Room_name'], s))
            if row['Fac_ID']:
                facs = str(row['Fac_ID']).split(',')
                for f in facs:
                    blocked_slots['faculties'].add((f.strip(), s))

    courses_df = pd.read_sql("""
        SELECT Course_ID, Department, L, P, Type, Lab 
        FROM course 
        WHERE Course_ID != 'RM6201' AND Course_ID NOT LIKE 'IK%'
    """, conn)
    
    target_courses = courses_df[
        (~courses_df['Course_ID'].isin(stage1_courses)) & 
        (courses_df['Course_ID'].isin(course_sizes.keys()))
    ]
    
    fac_df = pd.read_sql("SELECT Course_ID, Fac_ID FROM course_instructor", conn)
    course_faculties = fac_df.groupby('Course_ID')['Fac_ID'].apply(list).to_dict()
    
    fac_courses = fac_df.groupby('Fac_ID')['Course_ID'].apply(list).to_dict()
    for courses in fac_courses.values():
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                if courses[i] != courses[j]:
                    conflict_edges.add(tuple(sorted([courses[i], courses[j]])))

    mapping_df = pd.read_sql("SELECT Branch, Level, Course_ID FROM student_enrollment", conn)
    course_types = dict(zip(target_courses['Course_ID'], target_courses['Type']))
    sync_groups = collections.defaultdict(list)
    for _, row in mapping_df.iterrows():
        cid = row['Course_ID']
        ctype = str(course_types.get(cid, '')).strip()
        if ctype.startswith('DE'):
            key = f"{row['Branch']}_{row['Level']}_{ctype}"
            if cid not in sync_groups[key]:
                sync_groups[key].append(cid)
                
    parallel_de_groups = [group for group in sync_groups.values() if len(group) > 1]
    
    return target_courses, classrooms, labs, course_sizes, course_faculties, conflict_edges, blocked_slots, parallel_de_groups, stage1_df

# ==========================================
# 3. EVENT SHATTERING
# ==========================================
def generate_events(target_courses, classrooms, labs, course_sizes, course_faculties):
    print("Shattering courses into sub-events...")
    events = {}
    
    for _, row in target_courses.iterrows():
        cid = row['Course_ID']
        L, P = row['L'], row['P']
        ctype = str(row['Type']).strip().upper()
        assigned_lab = row['Lab']
        dept = row['Department']
        
        size = course_sizes[cid]
        facs = course_faculties.get(cid, [])
        
        if L > 0:
            valid_rooms = classrooms[classrooms['Capacity'] >= size]['Room_name'].tolist()
            if valid_rooms:
                v_times = IDE_SLOTS if ctype in ['IDE', 'IDE_MSE'] else get_valid_starts(1)
                for i in range(L):
                    e_id = f"{cid}_L{i}"
                    events[e_id] = Event(e_id, cid, 'LEC', 1, valid_rooms, v_times, facs)

        if P > 0:
            valid_lab_rooms = [assigned_lab] if pd.notna(assigned_lab) else labs[(labs['Department'] == dept) & (labs['Capacity'] >= size)]['Room_name'].tolist()
            if valid_lab_rooms:
                if P > 4:
                    dur1, dur2 = P // 2, P - (P // 2)
                    events[f"{cid}_P1"] = Event(f"{cid}_P1", cid, 'LAB', dur1, valid_lab_rooms, get_valid_starts(dur1), facs)
                    events[f"{cid}_P2"] = Event(f"{cid}_P2", cid, 'LAB', dur2, valid_lab_rooms, get_valid_starts(dur2), facs)
                else:
                    events[f"{cid}_P1"] = Event(f"{cid}_P1", cid, 'LAB', P, valid_lab_rooms, get_valid_starts(P), facs)

    return events

# ==========================================
# 4. HEURISTIC SEARCH ENGINE (Simulated Annealing + Min-Conflicts)
# ==========================================
def calculate_state_cost(state, events, conflict_edges, blocked_slots):
    """Calculates the total number of hard constraint violations in the current state."""
    cost = 0
    room_usage = collections.defaultdict(list)
    fac_usage = collections.defaultdict(list)
    course_starts = collections.defaultdict(list)
    
    # 1. Populate usage trackers
    for e_id, (r, t) in state.items():
        e = events[e_id]
        for span_t in range(t, t + e.duration):
            room_usage[(r, span_t)].append(e_id)
            for f in e.faculties:
                fac_usage[(f, span_t)].append(e_id)
            course_starts[(e.course, span_t)].append(e_id)

    # 2. Calculate Penalties
    # Room Double-Booking
    for (r, t), e_list in room_usage.items():
        if len(e_list) > 1: cost += (len(e_list) - 1) * 100
        if (r, t) in blocked_slots['rooms']: cost += 100

    # Faculty Double-Booking
    for (f, t), e_list in fac_usage.items():
        if len(e_list) > 1: cost += (len(e_list) - 1) * 100
        if (f, t) in blocked_slots['faculties']: cost += 100

    # Conflict Graph (Students)
    for c1, c2 in conflict_edges:
        for t in range(TOTAL_SLOTS):
            if (c1, t) in course_starts and (c2, t) in course_starts:
                cost += 100 # Lower penalty than physical room overlap, but still hard
                
    return cost

def solve_heuristic(events_dict, conflict_edges, blocked_slots, parallel_de_groups, max_iters=20000):
    print(f"\nInitializing Heuristic Search for {len(events_dict)} events...")
    
    # Bundle Parallel DEs into unified moves
    de_bundles = []
    for group in parallel_de_groups:
        bundle = []
        for c in group:
            bundle.extend([e_id for e_id, e in events_dict.items() if e.course == c and e.type == 'LEC'])
        if bundle: de_bundles.append(bundle)

    # Helper to check if an event is part of a DE bundle
    event_to_bundle = {}
    for b in de_bundles:
        for e_id in b: event_to_bundle[e_id] = b

    # --- INITIAL RANDOM STATE ---
    state = {}
    for e_id, e in events_dict.items():
        # Prevent picking times that are physically impossible due to Stage 1
        valid_t = [t for t in e.valid_times if not any((r, t+dt) in blocked_slots['rooms'] for r in e.valid_rooms for dt in range(e.duration))]
        if not valid_t: valid_t = e.valid_times # Fallback
        
        state[e_id] = (random.choice(e.valid_rooms), random.choice(valid_t))

    current_cost = calculate_state_cost(state, events_dict, conflict_edges, blocked_slots)
    best_state = state.copy()
    best_cost = current_cost
    
    print(f"Initial Random Cost: {current_cost} clashes.")
    
    # --- SIMULATED ANNEALING LOOP ---
    temp = 100.0
    cooling_rate = 0.9995
    
    start_time = time.time()
    
    for i in range(max_iters):
        if current_cost == 0:
            print(f"Perfect schedule found at iteration {i}!")
            break
            
        # 1. Pick a random event to mutate
        e_id = random.choice(list(events_dict.keys()))
        e = events_dict[e_id]
        
        # Save old values to revert if the move is bad
        old_val = state[e_id]
        
        # 2. Mutate (Swap Room and Time)
        new_room = random.choice(e.valid_rooms)
        new_time = random.choice(e.valid_times)
        
        # Check if it's a Parallel DE. If so, force ALL grouped events to the same time
        mutated_bundle = {}
        if e_id in event_to_bundle:
            for b_id in event_to_bundle[e_id]:
                mutated_bundle[b_id] = state[b_id]
                state[b_id] = (random.choice(events_dict[b_id].valid_rooms), new_time)
        else:
            state[e_id] = (new_room, new_time)
            
        # 3. Evaluate New Cost
        new_cost = calculate_state_cost(state, events_dict, conflict_edges, blocked_slots)
        
        # 4. Accept or Reject Move
        if new_cost < current_cost:
            current_cost = new_cost
            if current_cost < best_cost:
                best_cost = current_cost
                best_state = state.copy()
        else:
            # Simulated Annealing acceptance probability to escape local traps
            prob = math.exp((current_cost - new_cost) / temp)
            if random.random() < prob:
                current_cost = new_cost # Accept worse move
            else:
                # Reject move, revert
                if e_id in event_to_bundle:
                    for b_id, old_r_t in mutated_bundle.items():
                        state[b_id] = old_r_t
                else:
                    state[e_id] = old_val
                    
        # Cool down the temperature
        temp = max(temp * cooling_rate, 0.1)
        
        if i % 1000 == 0:
            print(f"Iter {i:5d} | Current Clashes: {current_cost} | Best Clashes: {best_cost} | Temp: {temp:.2f}")

    print(f"\nSearch complete in {time.time() - start_time:.1f} seconds.")
    print(f"Final Best Cost: {best_cost} remaining clashes.")
    
    # Convert state to final schedule format
    schedule = []
    for e_id, (r, t) in best_state.items():
        e = events_dict[e_id]
        fac_str = ",".join(e.faculties) if e.faculties else ""
        schedule.append({
            'Event_ID': e.id, 'Course_ID': e.course, 'Type': e.type, 
            'Student_Groups': 'Mixed (Stage 2)', 'Room_name': r, 
            'Start_Slot': t, 'Duration': e.duration, 'Instructors': fac_str
        })
    return schedule

# ==========================================
# 5. DB WRITE (Same as before)
# ==========================================
def save_master_timetable(conn, stage2_schedule, stage1_df):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS final_institute_timetable (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Event_ID VARCHAR(20),
            Course_ID VARCHAR(10),
            Type VARCHAR(10),
            Student_Groups VARCHAR(50),
            Room_name VARCHAR(20),
            Start_Slot INT,
            Duration INT,
            Instructors VARCHAR(50)
        )
    """)
    cursor.execute("TRUNCATE TABLE final_institute_timetable")
    
    master_records = []
    
    for _, row in stage1_df.iterrows():
        master_records.append((
            row['Event_ID'], row['Course_ID'], row['Type'], row['Groups'],
            row['Room_name'], row['Start_Slot'], row['Duration'], row.get('Fac_ID', '')
        ))
        
    for s in stage2_schedule:
        master_records.append((
            s['Event_ID'], s['Course_ID'], s['Type'], s['Student_Groups'],
            s['Room_name'], s['Start_Slot'], s['Duration'], s['Instructors']
        ))

    insert_query = """
        INSERT INTO final_institute_timetable 
        (Event_ID, Course_ID, Type, Student_Groups, Room_name, Start_Slot, Duration, Instructors)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, master_records)
    conn.commit()
    print(f"\n[SUCCESS] Master Timetable created! Inserted {len(master_records)} total events.")

if __name__ == "__main__":
    conn = mysql.connector.connect(**DB_CONFIG)
    target_courses, classrooms, labs, course_sizes, course_faculties, conflict_edges, blocked_slots, parallel_de_groups, stage1_df = fetch_and_build_context(conn)
    
    events_dict = generate_events(target_courses, classrooms, labs, course_sizes, course_faculties)
    
    # Run the Heuristic Engine
    stage2_schedule = solve_heuristic(events_dict, conflict_edges, blocked_slots, parallel_de_groups)
    
    if stage2_schedule: save_master_timetable(conn, stage2_schedule, stage1_df)
    conn.close()