import pulp
import mysql.connector
import pandas as pd
import re
from collections import defaultdict
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)

# ==========================================
# 1. CONFIGURATION
# ==========================================
DB_CONFIG = {'host': 'localhost', 'user': 'root', 'password': 'dfghklcv', 'database': 'IITP_Timetable'}
DAYS, SLOTS_PER_DAY = 5, 8 
TOTAL_SLOTS = DAYS * SLOTS_PER_DAY
CPU_CORES = os.cpu_count() or 4

IDE_SLOTS_2PM = [4, 20, 36] 
DEX_SLOTS = [d * SLOTS_PER_DAY + s for d in range(DAYS) for s in [3, 4, 5, 6]]
VALID_LAB_STARTS = [d * SLOTS_PER_DAY + s for d in range(DAYS) for s in [0, 4]] 

# Restricted to exactly 5 temp rooms
TEMP_ROOMS = [f'R{i}' for i in range(1, 6)]

# Weights
W_SKIP = 1000000000
W_TEMP_BASE = 1000000 # Base penalty for any temp room
W_ROOM_PREF = 50       

class Event:
    def __init__(self, e_id, course, e_type, c_type, groups, duration, v_rooms, faculty, year, dept, is_shared):
        self.id, self.course, self.type, self.c_type = e_id, course, e_type, c_type
        self.groups, self.duration, self.valid_rooms = groups, duration, v_rooms
        self.faculty, self.year, self.dept, self.is_shared = faculty, year, dept, is_shared
        self.diagnostic = ""

# ==========================================
# 2. DATA EXTRACTION
# ==========================================
def fetch_context(conn):
    rooms_df = pd.read_sql("SELECT Room_name, Capacity, Type, Department FROM classrooms_labs ORDER BY Capacity ASC", conn)
    fac_df = pd.read_sql("SELECT Course_ID, Fac_ID FROM course_instructor", conn)
    courses_df = pd.read_sql("SELECT Course_id, L, P, Type, Department, Lab FROM course", conn)
    
    enroll_query = "SELECT Course_ID, REGEXP_REPLACE(Roll_No, '[0-9]', '') as Branch, COUNT(*) as Count FROM student_course_enrollment GROUP BY Course_ID, Branch HAVING Count > 0"
    enroll_df = pd.read_sql(enroll_query, conn)
    valid_ids = set(enroll_df['Course_ID'].unique())

    batches = enroll_df[['Branch', 'Course_ID']].copy()
    batches['Year'] = batches['Course_ID'].apply(lambda x: re.search(r'\d', str(x)).group() if re.search(r'\d', str(x)) else "1")
    unique_batches = batches[['Branch', 'Year']].drop_duplicates()

    homeroom_registry, assigned_rooms = {}, set()
    DEPT_MAP = {'CS': 'CSE', 'AI': 'CSE', 'CE': 'CEE', 'CH': 'CHM', 'ME': 'ME', 'EE': 'EE', 'EC': 'ECE', 'CB': 'CBE', 'MM': 'MME', 'EP': 'PHY', 'MC': 'MATH', 'ES': 'HSS'}

    for _, b_row in unique_batches.iterrows():
        branch, year = b_row['Branch'], b_row['Year']
        if year == "1": continue 
        db_dept = DEPT_MAP.get(branch, branch)
        mask = (rooms_df['Department'] == db_dept) & (rooms_df['Type'] == 'CLASSROOM') & (~rooms_df['Room_name'].isin(assigned_rooms))
        dept_rooms = rooms_df[mask]
        if not dept_rooms.empty:
            room_name = dept_rooms.iloc[0]['Room_name']
            homeroom_registry[(db_dept, year)] = room_name
            assigned_rooms.add(room_name)

    aud_map = {}
    for c_id, group in enroll_df.groupby('Course_ID'):
        year = re.search(r'\d', str(c_id)).group() if re.search(r'\d', str(c_id)) else "1"
        branches = group['Branch'].unique().tolist()
        aud_map[c_id] = {'branches': branches, 'is_shared': len(branches) > 1, 'tags': [f"{br}_Y{year}" for br in branches], 'total_count': group['Count'].sum(), 'year': year}
    
    lab_dict = {
        'CS1201': rooms_df[rooms_df['Room_name'] == 'CC1']['Room_name'].tolist(),
        'CH1201': rooms_df[rooms_df['Room_name'] == 'CHLAB1']['Room_name'].tolist(),
        'PH1201': rooms_df[rooms_df['Room_name'] == 'PHLAB1']['Room_name'].tolist(),
        'ME1201': rooms_df[rooms_df['Room_name'] == 'MEWORKSHOP']['Room_name'].tolist(),
        'EE1201': rooms_df[rooms_df['Room_name'] == 'EELAB1']['Room_name'].tolist()
    }
    
    return rooms_df, fac_df.groupby('Course_ID')['Fac_ID'].apply(list).to_dict(), courses_df, aud_map, valid_ids, homeroom_registry, lab_dict


# ==========================================
# 3. event GENERATION
# ==========================================


def generate_events(courses_df, rooms_df, instructors, aud_map, valid_ids, homeroom_registry, lab_dict):
    events, hr_table_data = [], []
    all_homerooms = list(set(homeroom_registry.values())) # Collect all homerooms branchwise aur yearwise, Ide can use any room bcoz there is no other 2nd year class going on in that time
                                                            # Core courses k li
    for _, row in courses_df.iterrows():
        c_id = row['Course_id']
        if "IKS" in str(c_id).upper() or str(c_id).startswith("IK") or c_id not in valid_ids: continue  #IKS ko 
        info = aud_map[c_id]
        f_list = instructors.get(c_id, [f"{c_id}_F1", f"{c_id}_F2"])
        dept, count, year, c_type = row['Department'], info['total_count'], info['year'], row['Type']

        def get_v_rooms(r_type, req_cap, force_lab):
            if r_type == 'LAB':
                if force_lab and force_lab.strip() != "": return [force_lab]
                return rooms_df[(rooms_df['Type'] == 'LAB') & (rooms_df['Capacity'] >= req_cap)]['Room_name'].tolist() + TEMP_ROOMS
            
            # IDE RULE: Can use ANY homeroom from any branch
            if c_type == "IDE":
                return all_homerooms + TEMP_ROOMS

            # DC RULE: Strictly homeroom of the specific department
            if c_type == "DC" and not info['is_shared']:
                h_room = homeroom_registry.get((dept, year))
                return [h_room] if h_room else TEMP_ROOMS[:1]

            # DE or Shared DC
            dept_pool = rooms_df[(rooms_df['Department'] == dept) & (rooms_df['Capacity'] >= req_cap) & (rooms_df['Type'] == 'CLASSROOM')]
            common_pool = rooms_df[(rooms_df['Department'].str.upper() == 'COMMON') & (rooms_df['Capacity'] >= req_cap)]
            return dept_pool['Room_name'].tolist() + common_pool['Room_name'].tolist() + TEMP_ROOMS

        num_lectures = int(row['L']) if pd.notnull(row['L']) else 0
        p_val = int(row['P']) if pd.notnull(row['P']) else 0
        lab_sessions = [p_val // 2, p_val - (p_val // 2)] if p_val > 4 else ([p_val] if p_val > 0 else [])

        if year == "1":
            y1_rooms = rooms_df[(rooms_df['Capacity'] >= 200) & (rooms_df['Type'] == 'CLASSROOM')]['Room_name'].tolist()
            for s in range(num_lectures):
                for g_idx, g_range in enumerate([range(1,7), range(7,13), range(13,19), range(19,25)]):
                    fac = f_list[0] if g_range[0] <= 12 else f_list[min(1, len(f_list)-1)]
                    events.append(Event(f"Y1_{c_id}_L{s}_G{g_idx}", c_id, 'LEC', c_type, [f"G{x}" for x in g_range], 1, y1_rooms + TEMP_ROOMS, fac, "1", dept, False))
            if lab_sessions:
                l_room = lab_dict.get(c_id, []) + TEMP_ROOMS
                g_start, g_end = (13, 25) if c_id in ['PH1201', 'EE1201', 'CE1201'] else (1, 13)
                if c_id == 'CS1201': g_end = 25
                for sess_idx, dur in enumerate(lab_sessions):
                    for i in range(g_start, g_end, 3):
                        fac = f_list[0] if i <= 12 else f_list[min(1, len(f_list)-1)]
                        events.append(Event(f"Y1_{c_id}_P{sess_idx}_G{i}", c_id, 'LAB', c_type, [f"G{x}" for x in range(i, i+3)], dur, l_room, fac, "1", dept, False))
        else:
            fac = f_list[0] if f_list else "Staff"
            for s in range(num_lectures):
                events.append(Event(f"{c_id}_L{s}", c_id, 'LEC', c_type, info['tags'], 1, get_v_rooms('CLASSROOM', count, None), fac, year, dept, info['is_shared']))
            for sess_idx, dur in enumerate(lab_sessions):
                events.append(Event(f"{c_id}_Lab{sess_idx}", c_id, 'LAB', c_type, info['tags'], dur, get_v_rooms('LAB', count, row['Lab']), fac, year, dept, info['is_shared']))
        
        if c_type == "DC" and not info['is_shared']:
            hr_table_data.append((c_id, c_type, homeroom_registry.get((dept, year), "NONE")))
    return events, hr_table_data


# ==========================================
# 4. SOLVER
# ==========================================


def solve_timetable(events):
    prob = pulp.LpProblem("IITP_Final_Unified_Solver", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", [(e.id, r, t) for e in events for r in e.valid_rooms for t in range(TOTAL_SLOTS)], cat=pulp.LpBinary)
    skip = pulp.LpVariable.dicts("skip", [e.id for e in events], cat=pulp.LpBinary)

    obj_terms = [skip[e.id] * W_SKIP for e in events]
    for e in events:
        for r_idx, r in enumerate(e.valid_rooms):
            # SCALED PENALTY: Temp rooms scale their penalty with index (R1 is cheaper than R5)
            if r in TEMP_ROOMS:
                temp_idx = TEMP_ROOMS.index(r)
                penalty = W_TEMP_BASE + (temp_idx * 10000) 
            else:
                penalty = (r_idx * W_ROOM_PREF)
                
            for t in range(TOTAL_SLOTS):
                if (e.id, r, t) in x:
                    obj_terms.append(x[(e.id, r, t)] * penalty)
    
    prob += pulp.lpSum(obj_terms)

    fac_clq, room_clq, aud_clq = defaultdict(list), defaultdict(list), defaultdict(list)

    for e in events:
        v_times = range(TOTAL_SLOTS)
        if e.c_type == 'IDE' and e.year == "2": v_times = IDE_SLOTS_2PM
        elif "DE" in str(e.c_type): v_times = DEX_SLOTS
        elif e.type == 'LAB': v_times = VALID_LAB_STARTS
        if e.year == "2" and e.c_type == "DC" and e.type != "LAB":
            v_times = [t for t in v_times if t not in IDE_SLOTS_2PM]
        
        final_v_times = [t for t in v_times if (t % SLOTS_PER_DAY) + e.duration <= SLOTS_PER_DAY]
        prob += pulp.lpSum([x[(e.id, r, t)] for r in e.valid_rooms for t in final_v_times if (e.id, r, t) in x]) + skip[e.id] == 1

        for r in e.valid_rooms:
            for t in final_v_times:
                if (e.id, r, t) in x:
                    for offset in range(e.duration):
                        tp = t + offset
                        if e.type != "LAB":
                            fac_clq[(e.faculty, tp)].append(x[(e.id, r, t)])
                        room_clq[(r, tp)].append(x[(e.id, r, t)])
                        if "DE" not in str(e.c_type):
                            for g in e.groups: aud_clq[(g, tp)].append(x[(e.id, r, t)])

    for clq in fac_clq.values(): prob += pulp.lpSum(clq) <= 1
    for clq in room_clq.values(): prob += pulp.lpSum(clq) <= 1
    for clq in aud_clq.values(): prob += pulp.lpSum(clq) <= 1

    print(f"Solving with {CPU_CORES} threads...")
    prob.solve(pulp.PULP_CBC_CMD(msg=1, timeLimit=1200, threads=CPU_CORES))
    
    res, dropped = [], []
    for e in events:
        if pulp.value(skip[e.id]) == 1.0: 
            dropped.append((e.id, e.course, e.type, ", ".join(e.groups), e.faculty, "Conflict/Capacity Error"))
        else:
            for r in e.valid_rooms:
                for t in range(TOTAL_SLOTS):
                    if (e.id, r, t) in x and pulp.value(x[(e.id, r, t)]) == 1.0:
                        res.append((e.id, str(e.course).strip().upper(), e.type, str(e.groups), r, t, e.duration, e.faculty))
    return res, dropped

# ==========================================
# 5. DB STORAGE
# ==========================================
def save_all_data(conn, schedule, hr_data, dropped):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS final_really_last_final (ID INT AUTO_INCREMENT PRIMARY KEY, Event_ID VARCHAR(50), Course_ID VARCHAR(20), Type VARCHAR(10), `Groups` TEXT, Room_name VARCHAR(20), Start_Slot INT, Duration INT, Fac_ID VARCHAR(50))")
    cursor.execute("TRUNCATE TABLE final_really_last_final")
    cursor.executemany("INSERT INTO final_really_last_final (Event_ID, Course_ID, Type, `Groups`, Room_name, Start_Slot, Duration, Fac_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", schedule)
    
    cursor.execute("CREATE TABLE IF NOT EXISTS nha (Course_ID VARCHAR(20), Type VARCHAR(10), Homeroom VARCHAR(20))")
    cursor.execute("TRUNCATE TABLE nha")
    cursor.executemany("INSERT INTO nha (Course_ID, Type, Homeroom) VALUES (%s,%s,%s)", hr_data)
    
    cursor.execute("CREATE TABLE IF NOT EXISTS drop_diagnostics (Event_ID VARCHAR(50), Course_ID VARCHAR(20), Type VARCHAR(10), `Groups` TEXT, Fac_ID VARCHAR(50), Reason TEXT)")
    cursor.execute("TRUNCATE TABLE drop_diagnostics")
    cursor.executemany("INSERT INTO drop_diagnostics (Event_ID, Course_ID, Type, `Groups`, Fac_ID, Reason) VALUES (%s,%s,%s,%s,%s,%s)", dropped)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_conn = mysql.connector.connect(**DB_CONFIG)
    rooms_data, fac_map, courses_data, aud_info, v_ids, hr_registry, l_dict = fetch_context(db_conn)
    all_events, hr_table = generate_events(courses_data, rooms_data, fac_map, aud_info, v_ids, hr_registry, l_dict)
    final_sched, dropped_list = solve_timetable(all_events)
    save_all_data(db_conn, final_sched, hr_table, dropped_list)
    print(f"Process complete. Scheduled: {len(final_sched)}, Dropped: {len(dropped_list)}")
