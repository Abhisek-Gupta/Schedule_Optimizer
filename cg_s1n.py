import pulp
import mysql.connector
import pandas as pd
import networkx as nx
import re

# ==========================================
# 1. CONFIGURATION & TIME DOMAINS
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '##########',
    'database': 'IITP_Timetable'
}

DAYS = 5
SLOTS_PER_DAY = 8
TOTAL_SLOTS = DAYS * SLOTS_PER_DAY

VALID_LAB_STARTS_PER_DAY = [0, 1, 4, 5] 
ALL_VALID_LAB_STARTS = [d * SLOTS_PER_DAY + s for d in range(DAYS) for s in VALID_LAB_STARTS_PER_DAY]
ALL_VALID_LEC_STARTS = list(range(TOTAL_SLOTS))
GROUPS = list(range(1, 25))

W_GAP = 5     
W_OVERLOAD = 10 

# ==========================================
# 2. EVENT DEFINITION
# ==========================================
class Event:
    def __init__(self, e_id, course, e_type, groups, duration, valid_rooms, valid_times, faculty):
        self.id = e_id
        self.course = course
        self.type = e_type
        self.groups = groups
        self.duration = duration
        self.valid_rooms = valid_rooms
        self.valid_times = valid_times
        self.faculty = faculty 

# ==========================================
# 3. DB EXTRACTION & CONFLICT ANALYSIS
# ==========================================
def fetch_context(conn):
    rooms_df = pd.read_sql("SELECT Room_name, Capacity, Type, Department FROM classrooms_labs", conn)
    fac_df = pd.read_sql("SELECT Course_ID, Fac_ID FROM course_instructor", conn)
    
    lec_rooms = rooms_df[(rooms_df['Type'] == 'CLASSROOM') & (rooms_df['Capacity'] >= 270)]['Room_name'].tolist()
    
    lab_dict = {
        'CS1201': rooms_df[(rooms_df['Room_name'] == 'CC1')]['Room_name'].tolist(),
        'CH1201': rooms_df[(rooms_df['Room_name'] == 'CHLAB1')]['Room_name'].tolist(),
        'PH1201': rooms_df[(rooms_df['Room_name'] == 'PHLAB1')]['Room_name'].tolist(),
        'ME1201': rooms_df[(rooms_df['Room_name'] == 'MEWORKSHOP')]['Room_name'].tolist(),
        'EE1201': rooms_df[(rooms_df['Room_name'] == 'EELAB1')]['Room_name'].tolist(),
    }
    
    instructors = {}
    for course in ['MA1201', 'CS1201', 'CH1201', 'ME1201', 'ME1202', 'PH1201', 'EE1201', 'CE1201']:
        facs = fac_df[fac_df['Course_ID'] == course]['Fac_ID'].tolist()
        # Fallback to avoid crashes, though ideally DB should be populated
        instructors[course] = facs if len(facs) >= 2 else [f"{course}_F1", f"{course}_F2"]
        
    return lec_rooms, lab_dict, instructors

def analyze_conflict_graph(events):
    G = nx.Graph()
    for e in events:
        G.add_node(e.id, faculty=e.faculty, groups=set(e.groups))
    
    nodes = list(G.nodes(data=True))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            id1, d1 = nodes[i]
            id2, d2 = nodes[j]
            if d1['faculty'] == d2['faculty'] or not d1['groups'].isdisjoint(d2['groups']):
                G.add_edge(id1, id2)
    
    cliques = list(nx.find_cliques(G))
    max_clique = max(cliques, key=len) if cliques else []
    print(f"--- Conflict Graph Analysis ---")
    print(f"Total Events: {G.number_of_nodes()} | Max Clique: {len(max_clique)}")
    return G

def generate_events(lec_rooms, lab_dict, instructors):
    events = []
    e_counter = 0
    
    def assign_fac(course, g_range):
        first_group = g_range[0]
        f_list = instructors.get(course, [f"{course}_F1", f"{course}_F2"])
        if course in ['MA1201', 'CS1201']:
            return f_list[0] if first_group <= 12 else f_list[1]
        elif course in ['CH1201', 'ME1201', 'ME1202']:
            return f_list[0] if first_group <= 6 else f_list[1]
        else:
            return f_list[0] if first_group <= 18 else f_list[1]

    # 1. Common Courses (Lectures 3 hrs, Labs 3 hrs)
    for course, l_hrs in [('MA1201', 3), ('CS1201', 3)]:
        for _ in range(l_hrs):
            for g_range in [range(1,7), range(7,13), range(13,19), range(19,25)]:
                fac = assign_fac(course, g_range)
                events.append(Event(f"E{e_counter}", course, 'LEC', list(g_range), 1, lec_rooms, ALL_VALID_LEC_STARTS, fac))
                e_counter += 1
                
    for g_range in [range(i, i+3) for i in range(1, 25, 3)]:
        fac = assign_fac('CS1201', g_range)
        events.append(Event(f"E{e_counter}", 'CS1201', 'LAB', list(g_range), 3, lab_dict['CS1201'], ALL_VALID_LAB_STARTS, fac))
        e_counter += 1

    # 2. Track G1-12
    for course in ['CH1201', 'ME1202']:
        for _ in range(3):
            for g_range in [range(1,7), range(7,13)]:
                fac = assign_fac(course, g_range)
                events.append(Event(f"E{e_counter}", course, 'LEC', list(g_range), 1, lec_rooms, ALL_VALID_LEC_STARTS, fac))
                e_counter += 1
                
    for course in ['CH1201', 'ME1201']:
        for g_range in [range(i, i+3) for i in range(1, 13, 3)]:
            fac = assign_fac(course, g_range)
            events.append(Event(f"E{e_counter}", course, 'LAB', list(g_range), 3, lab_dict[course], ALL_VALID_LAB_STARTS, fac))
            e_counter += 1

    # 3. Track G13-24
    for course, l_hrs in [('PH1201', 3), ('EE1201', 3), ('CE1201', 1)]:
        for _ in range(l_hrs):
            for g_range in [range(13,19), range(19,25)]:
                fac = assign_fac(course, g_range)
                events.append(Event(f"E{e_counter}", course, 'LEC', list(g_range), 1, lec_rooms, ALL_VALID_LEC_STARTS, fac))
                e_counter += 1
                
    for course in ['PH1201', 'EE1201']:
        for g_range in [range(i, i+3) for i in range(13, 25, 3)]:
            fac = assign_fac(course, g_range)
            events.append(Event(f"E{e_counter}", course, 'LAB', list(g_range), 3, lab_dict[course], ALL_VALID_LAB_STARTS, fac))
            e_counter += 1

    for g_range in [range(13,19), range(19,25)]:
        fac = assign_fac('CE1201', g_range)
        events.append(Event(f"E{e_counter}", 'CE1201', 'LAB', list(g_range), 3, lec_rooms, ALL_VALID_LAB_STARTS, fac))
        e_counter += 1

    return events

# ==========================================
# 4. ILP FORMULATION & SOLVER
# ==========================================
def solve_timetable(events):
    prob = pulp.LpProblem("IITP_Stage1_Optimization", pulp.LpMinimize)
    
    # Decision Variable: x[event][room][time]
    x = {e.id: {r: {t: pulp.LpVariable(f"x_{e.id}_{r}_{t}", cat=pulp.LpBinary) 
                    for t in e.valid_times} for r in e.valid_rooms} for e in events}

    # 1. Every event must happen exactly once
    for e in events:
        prob += pulp.lpSum([x[e.id][r][t] for r in e.valid_rooms for t in e.valid_times]) == 1

    # 2. No overlapping events for Rooms, Groups, or Faculty
    all_rooms = set(r for e in events for r in e.valid_rooms)
    all_faculties = set(e.faculty for e in events)
    
    for t in range(TOTAL_SLOTS):
        day = t // SLOTS_PER_DAY
        # Room Conflict
        for r in all_rooms:
            active = [x[e.id][r][st] for e in events if r in e.valid_rooms 
                      for st in range(max(0, t-e.duration+1), t+1) 
                      if st in e.valid_times and st // SLOTS_PER_DAY == day]
            if active: prob += pulp.lpSum(active) <= 1
        # Group Conflict
        for g in GROUPS:
            active = [x[e.id][r][st] for e in events if g in e.groups for r in e.valid_rooms 
                      for st in range(max(0, t-e.duration+1), t+1) 
                      if st in e.valid_times and st // SLOTS_PER_DAY == day]
            if active: prob += pulp.lpSum(active) <= 1
        # Faculty Conflict
        for f in all_faculties:
            active = [x[e.id][r][st] for e in events if e.faculty == f for r in e.valid_rooms 
                      for st in range(max(0, t-e.duration+1), t+1) 
                      if st in e.valid_times and st // SLOTS_PER_DAY == day]
            if active: prob += pulp.lpSum(active) <= 1

    # 3. DAILY LECTURE UNIQUENESS (The Fix)
    all_courses = set(e.course for e in events)
    for d in range(DAYS):
        day_slots = range(d * SLOTS_PER_DAY, (d+1) * SLOTS_PER_DAY)
        for course in all_courses:
            for g in GROUPS:
                relevant = [e for e in events if e.course == course and e.type == 'LEC' and g in e.groups]
                if relevant:
                    prob += pulp.lpSum([x[e.id][r][t] for e in relevant for r in e.valid_rooms 
                                        for t in e.valid_times if t in day_slots]) <= 1

    print("Solving ILP...")
    prob.solve(pulp.PULP_CBC_CMD(msg=1, timeLimit=600))
    
    schedule = []
    if pulp.LpStatus[prob.status] in ['Optimal', 'Not Solved']: # Not Solved usually means it found a feasible sol but hit time limit
        for e in events:
            for r in e.valid_rooms:
                for t in e.valid_times:
                    if pulp.value(x[e.id][r][t]) == 1.0:
                        schedule.append((e.id, e.course, e.type, f"G{e.groups[0]}-{e.groups[-1]}", r, t, e.duration, e.faculty))
    return schedule

# ==========================================
# 5. DB INSERTION
# ==========================================
def save_to_database(conn, schedule):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cg_s1 (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Event_ID VARCHAR(20),
            Course_ID VARCHAR(10),
            Type VARCHAR(10),
            `Groups` VARCHAR(20),
            Room_name VARCHAR(20),
            Start_Slot INT,
            Duration INT,
            Fac_ID VARCHAR(10)
        )
    """)
    cursor.execute("TRUNCATE TABLE cg_s1")
    insert_query = "INSERT INTO cg_s1 (Event_ID, Course_ID, Type, `Groups`, Room_name, Start_Slot, Duration, Fac_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(insert_query, schedule)
    conn.commit()
    print(f"Successfully saved {len(schedule)} rows to cg_s1.")

if __name__ == "__main__":
    conn = mysql.connector.connect(**DB_CONFIG)
    lec_rooms, lab_dict, instructors = fetch_context(conn)
    events = generate_events(lec_rooms, lab_dict, instructors)
    analyze_conflict_graph(events)
    final_schedule = solve_timetable(events)
    if final_schedule:
        save_to_database(conn, final_schedule)
    conn.close()
