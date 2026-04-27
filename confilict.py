import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': 'password', 'database': 'IITP_Timetable'
}

def run_diagnostic():
    conn = mysql.connector.connect(**DB_CONFIG)
    
    # 1. Check IDE Capacity
    rooms_df = pd.read_sql("SELECT Room_name, Capacity FROM classrooms_labs WHERE Type = 'CLASSROOM'", conn)
    large_rooms = len(rooms_df[rooms_df['Capacity'] >= 100])
    
    courses_df = pd.read_sql("SELECT Course_ID, Type FROM course", conn)
    ide_count = len(courses_df[courses_df['Type'].isin(['IDE', 'IDE_MSE'])])
    
    print("--- 1. IDE CAPACITY CHECK ---")
    print(f"Total IDE/IDE_MSE Courses: {ide_count}")
    print(f"Total Classrooms (Capacity >= 100): {large_rooms}")
    print(f"Total IDE Slots Available (3 slots * {large_rooms} rooms): {large_rooms * 3}")
    if ide_count > (large_rooms * 3):
        print(">> [FATAL BOTTLENECK] You have more IDEs than physical slots available! Add more IDE slots.")
    else:
        print(">> IDE Capacity is mathematically possible.")

    # 2. Check Stage 1 Hoarding
    print("\n--- 2. STAGE 1 HOARDING CHECK ---")
    stage1_df = pd.read_sql("SELECT Room_name, Start_Slot FROM stage1_timetable", conn)
    s1_slots = len(stage1_df)
    print(f"Stage 1 has blocked {s1_slots} individual room-slots.")
    
    # Check if Stage 1 stole the IDE slots
    ide_theft = stage1_df[stage1_df['Start_Slot'].isin([4, 20, 28])]
    print(f"Stage 1 is occupying {len(ide_theft)} rooms during the sacred IDE hours (Slots 4, 20, 28).")
    if len(ide_theft) > 0:
        print(">> [WARNING] First years are blocking Stage 2 IDEs. You must either move Stage 1 or add more IDE slots.")

    # 3. Check Parallel DE Feasibility
    print("\n--- 3. PARALLEL DE CHECK ---")
    enroll_df = pd.read_sql("SELECT Branch, Level, Course_ID FROM student_enrollment", conn)
    de_courses = courses_df[courses_df['Type'].str.startswith('DE')]
    de_mapping = pd.merge(enroll_df, de_courses, on='Course_ID')
    
    max_parallel = de_mapping.groupby(['Branch', 'Level', 'Type'])['Course_ID'].nunique().max()
    print(f"The largest Parallel DE block has {max_parallel} simultaneous courses.")
    print(f"Total Classrooms available in the institute: {len(rooms_df)}")
    if max_parallel > len(rooms_df) // 2:
        print(">> [WARNING] High parallel DE count. Institute might run out of rooms at specific hours.")

    conn.close()

if __name__ == "__main__":
    run_diagnostic()