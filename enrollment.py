import mysql.connector
import pandas as pd
import random

# 1. Database Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',          # Replace with your MySQL username
    'password': 'Abhishekarch@#29.',  # Replace with your MySQL password
    'database': 'IITP_Timetable'
}

def generate_enrollments():
    print("Connecting to database...")
    conn = mysql.connector.connect(**db_config)
    
    # 2. Fetch Data
    print("Fetching student, course, and curriculum mapping data...")
    students_df = pd.read_sql("SELECT Roll_no, Branch, Department, Level FROM student", conn)
    courses_df = pd.read_sql("SELECT Course_ID, Department, Type FROM course", conn)
    
    # NEW: Fetch the batch-level curriculum mapping you provided
    mapping_df = pd.read_sql("SELECT Branch, Level, Course_ID FROM student_enrollment", conn)
    
    # 3. Organize Courses & Curriculums
    print("Building branch-specific curriculums...")
    
    # Quick lookup dictionaries for course metadata
    course_type_dict = dict(zip(courses_df['Course_ID'], courses_df['Type']))
    course_dept_dict = dict(zip(courses_df['Course_ID'], courses_df['Department']))
    
    # Mappings to hold the exact required courses per Branch and Level
    dc_curriculum = {} # dict[branch][level] = [course_ids]
    de_curriculum = {} # dict[branch][level][de_type] = [course_ids]
    
    # Populate the curriculums directly from your student_enrollment table
    for _, row in mapping_df.iterrows():
        b = row['Branch']
        l = row['Level']
        cid = row['Course_ID']
        
        ctype = course_type_dict.get(cid, 'UNKNOWN')
        
        # Only map what is explicitly stated in the DB, ignoring unmapped PG courses
        if ctype == 'DC':
            dc_curriculum.setdefault(b, {}).setdefault(l, []).append(cid)
        elif str(ctype).startswith('DE'):
            de_curriculum.setdefault(b, {}).setdefault(l, {}).setdefault(ctype, []).append(cid)

    # IDEs are interdisciplinary and chosen from the general course pool
    ide_courses = [
        {'id': row['Course_ID'], 'dept': row['Department'], 'enrolled': 0} 
        for _, row in courses_df.iterrows() if row['Type'] == 'IDE'
    ]

    # Tracker for DE Urn algorithm
    de_tracker = {}
    enrollment_queries = []
    
    # 4. Process Each Student
    print("Processing individual student enrollments...")
    for _, student in students_df.iterrows():
        roll = student['Roll_no']
        branch = student['Branch']
        dept = student['Department']
        level_str = student['Level']
        
        # --- A. FIRST YEAR LOGIC (UG1) ---
        if 'UG1' in level_str:
            group = int(level_str.split('_G')[1])
            
            # Common to all 1st years
            common = ['MA1201', 'IK1201', 'CS1201']
            for c in common:
                enrollment_queries.append(f"('{roll}', '{c}')")
                
            # Group specific rotations
            if 1 <= group <= 12:
                for c in ['CH1201', 'ME1201', 'ME1202']:
                    enrollment_queries.append(f"('{roll}', '{c}')")
            elif 13 <= group <= 24:
                for c in ['PH1201', 'EE1201', 'CE1201']:
                    enrollment_queries.append(f"('{roll}', '{c}')")
                    
        # --- B. SECOND YEAR ONWARDS (UG2, UG3, UG4) ---
        else:
            # For UG2, UG3, UG4, 'level_str' exactly matches the Level in student_enrollment
            year_level = level_str 
            
            # 1. Assign DC (Department Core) - ONLY from explicit mapping
            if branch in dc_curriculum and year_level in dc_curriculum[branch]:
                for c in dc_curriculum[branch][year_level]:
                    enrollment_queries.append(f"('{roll}', '{c}')")
                    
            # 2. Assign DE (Department Electives) - Random Urn Algorithm from mapping
            if branch in de_curriculum and year_level in de_curriculum[branch]:
                for de_type, course_list in de_curriculum[branch][year_level].items():
                    tracker_key = f"{branch}_{year_level}_{de_type}"
                    
                    if tracker_key not in de_tracker or len(de_tracker[tracker_key]) == 0:
                        de_tracker[tracker_key] = list(course_list) 
                        random.shuffle(de_tracker[tracker_key])     
                        
                    chosen_de = de_tracker[tracker_key].pop()
                    enrollment_queries.append(f"('{roll}', '{chosen_de}')")
                    
            # 3. Assign IDE (Interdisciplinary Electives) - UG2 Only
            if year_level == 'UG2':
                available_ides = [
                    ide for ide in ide_courses 
                    if ide['dept'] != dept and ide['enrolled'] < 100
                ]
                
                if available_ides:
                    chosen_ide = random.choice(available_ides)
                    enrollment_queries.append(f"('{roll}', '{chosen_ide['id']}')")
                    chosen_ide['enrolled'] += 1
                else:
                    print(f"Warning: No available IDE seats for student {roll}")

    # 5. Write to SQL File
    output_filename = "student_individual_enrollment_v2.sql"
    print(f"Writing {len(enrollment_queries)} rows to {output_filename}...")
    
    with open(output_filename, 'w') as f:
        f.write("USE IITP_Timetable;\n")
        f.write("BEGIN;\n\n")
        
        batch_size = 1000
        for i in range(0, len(enrollment_queries), batch_size):
            batch = enrollment_queries[i:i+batch_size]
            values = ",\n".join(batch)
            f.write(f"INSERT IGNORE INTO student_course_enrollment (Roll_no, Course_ID) VALUES \n{values};\n")
            
        f.write("\nCOMMIT;\n")
        
    print(f"Success! {len(enrollment_queries)} enrollment records ready.")

if __name__ == "__main__":
    generate_enrollments()