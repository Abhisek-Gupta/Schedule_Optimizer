import pulp
import mysql.connector
import pandas as pd
import collections

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

# IDE Anchor Slots: Mon 14:00 (4), Wed 14:00 (20), Thu 14:00 (28)
IDE_SLOTS = [4, 20, 28]

# Objective Function Weights (From Stage 1)
W_GAP = 10     
W_OVERLOAD = 5 

def get_valid_starts(duration):
    if duration == 0: return []
    valid = []
    for d in range(DAYS):
        base = d * SLOTS_PER_DAY
        for s in range(4 - duration + 1): # Morning (09:00 - 13:00)
            valid.append(base + s)
        for s in range(4, 8 - duration + 1): # Afternoon (14:00 - 18:00)
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
# 2. DATA EXTRACTION & GRAPH BUILDING
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

    # Fetch Stage 1 constraints 
    stage1_df = pd.read_sql("SELECT * FROM stage1_timetable", conn)
    stage1_courses = set(stage1_df['Course_ID'].tolist())
    
    blocked_slots = {'rooms': set(), 'faculties': set()}
    stage1_fac_hours = collections.defaultdict(lambda: collections.defaultdict(int))
    
    for _, row in stage1_df.iterrows():
        # Block Rooms & Faculties physically
        for s in range(row['Start_Slot'], row['Start_Slot'] + row['Duration']):
            blocked_slots['rooms'].add((row['Room_name'], s))
            if row['Fac_ID']:
                blocked_slots['faculties'].add((row['Fac_ID'], s))
                
        # Track existing hours for Stage 1 constraints mapping
        if row['Fac_ID']:
            day = row['Start_Slot'] // SLOTS_PER_DAY
            facs = str(row['Fac_ID']).split(',')
            for f in facs:
                stage1_fac_hours[f.strip()][day] += row['Duration']

    # Fetch Stage 2 Courses (Ignoring RM and IK)
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

    # Parallel DE Mappings & Cohort Tracking for Spans
    mapping_df = pd.read_sql("SELECT Branch, Level, Course_ID FROM student_enrollment", conn)
    course_types = dict(zip(target_courses['Course_ID'], target_courses['Type']))
    sync_groups = collections.defaultdict(list)
    cohort_courses = collections.defaultdict(list)
    
    for _, row in mapping_df.iterrows():
        cid = row['Course_ID']
        
        # Track for Cohort Spans (e.g. "CSE_UG2")
        cohort_id = f"{row['Branch']}_{row['Level']}"
        cohort_courses[cohort_id].append(cid)
        
        # Track for Parallel DE Sync
        ctype = str(course_types.get(cid, '')).strip()
        if ctype.startswith('DE'):
            key = f"{cohort_id}_{ctype}"
            if cid not in sync_groups[key]:
                sync_groups[key].append(cid)
                
    parallel_de_groups = [group for group in sync_groups.values() if len(group) > 1]

    return target_courses, classrooms, labs, course_sizes, course_faculties, conflict_edges, blocked_slots, parallel_de_groups, stage1_df, stage1_fac_hours, cohort_courses

# ==========================================
# 3. EVENT SHATTERING
# ==========================================
def generate_events(target_courses, classrooms, labs, course_sizes, course_faculties):
    print("Shattering courses into sub-events...")
    events = []
    
    for _, row in target_courses.iterrows():
        cid = row['Course_ID']
        L = row['L']
        P = row['P']
        ctype = str(row['Type']).strip().upper()
        assigned_lab = row['Lab']
        dept = row['Department']
        
        size = course_sizes[cid]
        facs = course_faculties.get(cid, [])
        
        # 1. Lectures (Anchoring IDEs)
        if L > 0:
            valid_rooms = classrooms[classrooms['Capacity'] >= size]['Room_name'].tolist()
            if not valid_rooms:
                print(f"[WARNING] No classroom large enough for {cid} (Enrolled: {size})")
                continue
                
            v_times = IDE_SLOTS if ctype in ['IDE', 'IDE_MSE'] else get_valid_starts(1)
            for i in range(L):
                events.append(Event(f"{cid}_L{i}", cid, 'LEC', 1, valid_rooms, v_times, facs))

        # 2. Labs (Splitting > 4 hrs)
        if P > 0:
            valid_lab_rooms = [assigned_lab] if pd.notna(assigned_lab) else labs[(labs['Department'] == dept) & (labs['Capacity'] >= size)]['Room_name'].tolist()
            if not valid_lab_rooms: continue
                
            if P > 4:
                dur1, dur2 = P // 2, P - (P // 2)
                events.append(Event(f"{cid}_P1", cid, 'LAB', dur1, valid_lab_rooms, get_valid_starts(dur1), facs))
                events.append(Event(f"{cid}_P2", cid, 'LAB', dur2, valid_lab_rooms, get_valid_starts(dur2), facs))
            else:
                events.append(Event(f"{cid}_P1", cid, 'LAB', P, valid_lab_rooms, get_valid_starts(P), facs))

    return events

# ==========================================
# 4. ILP SOLVER (With Hard/Soft Constraints)
# ==========================================
def solve_stage2(events, conflict_edges, blocked_slots, parallel_de_groups, stage1_fac_hours, cohort_courses):
    print(f"\nBuilding ILP for {len(events)} events...")
    prob = pulp.LpProblem("IITP_Stage2", pulp.LpMinimize)

    # Variables
    x = {}
    for e in events:
        x[e.id] = {}
        for r in e.valid_rooms:
            x[e.id][r] = {}
            for t in e.valid_times:
                # Stage 1 Infrastructure Blocking
                is_blocked = False
                for span_t in range(t, t + e.duration):
                    if (r, span_t) in blocked_slots['rooms']:
                        is_blocked = True; break
                    for f in e.faculties:
                        if (f, span_t) in blocked_slots['faculties']:
                            is_blocked = True; break
                if not is_blocked:
                    x[e.id][r][t] = pulp.LpVariable(f"x_{e.id}_{r}_{t}", cat=pulp.LpBinary)

    print("Loading Hard Constraints...")
    # 1. Completeness
    for e in events:
        available_vars = [x[e.id][r][t] for r in e.valid_rooms for t in e.valid_times if t in x[e.id][r]]
        if available_vars: prob += pulp.lpSum(available_vars) == 1

    # 2. Room Overlap
    all_rooms = set(r for e in events for r in e.valid_rooms)
    for t in range(TOTAL_SLOTS):
        for r in all_rooms:
            active_events = [x[e.id][r][st] for e in events if r in e.valid_rooms 
                             for st in range(max(0, t - e.duration + 1), t + 1) if st in x[e.id][r]]
            if len(active_events) > 1:
                prob += pulp.lpSum(active_events) <= 1

    # 3. Conflict Graph Overlap
    for t in range(TOTAL_SLOTS):
        for c1, c2 in conflict_edges:
            e1_list = [e for e in events if e.course == c1]
            e2_list = [e for e in events if e.course == c2]
            active_e1 = [x[e.id][r][st] for e in e1_list for r in e.valid_rooms for st in range(max(0, t - e.duration + 1), t + 1) if st in x[e.id][r]]
            active_e2 = [x[e.id][r][st] for e in e2_list for r in e.valid_rooms for st in range(max(0, t - e.duration + 1), t + 1) if st in x[e.id][r]]
            if active_e1 and active_e2:
                prob += pulp.lpSum(active_e1) + pulp.lpSum(active_e2) <= 1

    # 4. Lecture Spacing (Max 1 lec per day)
    for d in range(DAYS):
        day_slots = range(d * SLOTS_PER_DAY, (d + 1) * SLOTS_PER_DAY)
        for c in set(e.course for e in events):
            lecs = [e for e in events if e.course == c and e.type == 'LEC']
            starts_today = [x[e.id][r][t] for e in lecs for r in e.valid_rooms for t in e.valid_times if t in day_slots and t in x[e.id][r]]
            if len(starts_today) > 1:
                prob += pulp.lpSum(starts_today) <= 1

    '''# 5. Parallel DE Synchronization
    for group in parallel_de_groups:
        base_course = group[0]
        for other_course in group[1:]:
            base_events = sorted([e for e in events if e.course == base_course and e.type == 'LEC'], key=lambda x: x.id)
            other_events = sorted([e for e in events if e.course == other_course and e.type == 'LEC'], key=lambda x: x.id)
            for be, oe in zip(base_events, other_events):
                for t in range(TOTAL_SLOTS):
                    be_starts = pulp.lpSum([x[be.id][r][t] for r in be.valid_rooms if t in x[be.id][r]])
                    oe_starts = pulp.lpSum([x[oe.id][r][t] for r in oe.valid_rooms if t in x[oe.id][r]])
                    prob += be_starts == oe_starts'''

    print("Loading Stage 1 Soft/Hard Constraints...")
    # 6. Faculty Limits (Hard <= 6, Soft Penalty > 4)
    all_faculties = set(f for e in events for f in e.faculties)
    fac_overload = {}
    
    for f in all_faculties:
        for d in range(DAYS):
            day_slots = range(d * SLOTS_PER_DAY, (d + 1) * SLOTS_PER_DAY)
            s1_hours = stage1_fac_hours[f][d]
            s2_hours = pulp.lpSum([e.duration * x[e.id][r][t] for e in events if f in e.faculties 
                                   for r in e.valid_rooms for t in e.valid_times if t in day_slots and t in x[e.id][r]])
            
            total_daily_hours = s1_hours + s2_hours
            
            # HARD LIMIT
            prob += total_daily_hours <= 8, f"Fac_Max6_{f}_Day{d}"
            
            # SOFT PENALTY TRACKER
            overload_var = pulp.LpVariable(f"overload_{f}_{d}", lowBound=0, cat=pulp.LpContinuous)
            prob += overload_var >= total_daily_hours - 6
            fac_overload[(f, d)] = overload_var

    '''# 7. Cohort Gaps (Minimizing Student Spans)
    cohort_span = {}
    for cohort, c_list in cohort_courses.items():
        cohort_events = [e for e in events if e.course in c_list]
        if not cohort_events: continue
        
        for d in range(DAYS):
            day_slots = range(d * SLOTS_PER_DAY, (d + 1) * SLOTS_PER_DAY)
            max_t = pulp.LpVariable(f"max_t_{cohort}_{d}", lowBound=0, cat=pulp.LpInteger)
            min_t = pulp.LpVariable(f"min_t_{cohort}_{d}", lowBound=0, upBound=SLOTS_PER_DAY, cat=pulp.LpInteger)
            has_class = pulp.LpVariable(f"active_{cohort}_{d}", cat=pulp.LpBinary)
            
            for e in cohort_events:
                for r in e.valid_rooms:
                    for t in e.valid_times:
                        if t in day_slots and t in x[e.id][r]:
                            slot_idx = t % SLOTS_PER_DAY
                            prob += max_t >= (slot_idx + e.duration) * x[e.id][r][t]
                            prob += min_t <= slot_idx * x[e.id][r][t] + 10 * (1 - x[e.id][r][t])
                            
            total_classes = pulp.lpSum([x[e.id][r][t] for e in cohort_events for r in e.valid_rooms 
                                        for t in e.valid_times if t in day_slots and t in x[e.id][r]])
            prob += total_classes <= 50 * has_class
            prob += min_t <= 10 * (1 - has_class)
            
            span_var = pulp.LpVariable(f"span_{cohort}_{d}", lowBound=0, cat=pulp.LpInteger)
            prob += span_var >= max_t - min_t
            cohort_span[(cohort, d)] = span_var'''

    # --- OBJECTIVE FUNCTION ---
    # Penalty for late slots (bounding variable), plus the Gap and Overload penalties
    '''prob += pulp.lpSum([t % SLOTS_PER_DAY * x[e.id][r][t] for e in events for r in e.valid_rooms for t in e.valid_times if t in x[e.id][r]]) + \
            pulp.lpSum([W_OVERLOAD * fac_overload[(f, d)] for f, d in fac_overload]) 
            # pulp.lpSum([W_GAP * cohort_span[(c, d)] for c, d in cohort_span])'''
    prob += 0

    print("\nSolving Stage 2 (Time Limit: 600s)...")
    prob.solve(pulp.PULP_CBC_CMD(msg=True, timeLimit=600, gapRel=0.05))
    print(f"Solver Status: {pulp.LpStatus[prob.status]}")
    
    schedule = []
    if prob.status in [pulp.LpStatusOptimal, pulp.LpStatusNotSolved]:
        for e in events:
            for r in e.valid_rooms:
                for t in e.valid_times:
                    if t in x[e.id][r] and pulp.value(x[e.id][r][t]) == 1.0:
                        fac_str = ",".join(e.faculties) if e.faculties else ""
                        schedule.append({
                            'Event_ID': e.id, 'Course_ID': e.course, 'Type': e.type, 
                            'Student_Groups': 'Mixed (Stage 2)', 'Room_name': r, 
                            'Start_Slot': t, 'Duration': e.duration, 'Instructors': fac_str
                        })
    return schedule

# ==========================================
# 5. MASTER INTEGRATION & DB WRITE
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
    
    # Append Stage 1 Data
    for _, row in stage1_df.iterrows():
        master_records.append((
            row['Event_ID'], row['Course_ID'], row['Type'], row['Groups'],
            row['Room_name'], row['Start_Slot'], row['Duration'], row.get('Fac_ID', '')
        ))
        
    # Append Stage 2 Data
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
    print(f"\n[SUCCESS] Master Timetable created! Inserted {len(master_records)} total events (Stage 1 + Stage 2).")

if __name__ == "__main__":
    conn = mysql.connector.connect(**DB_CONFIG)
    target_courses, classrooms, labs, course_sizes, course_faculties, conflict_edges, blocked_slots, parallel_de_groups, stage1_df, stage1_fac_hours, cohort_courses = fetch_and_build_context(conn)
    events = generate_events(target_courses, classrooms, labs, course_sizes, course_faculties)
    
    stage2_schedule = solve_stage2(events, conflict_edges, blocked_slots, parallel_de_groups, stage1_fac_hours, cohort_courses)
    if stage2_schedule: save_master_timetable(conn, stage2_schedule, stage1_df)
    conn.close()