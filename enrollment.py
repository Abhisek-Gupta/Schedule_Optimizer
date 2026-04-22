import mysql.connector
import pandas as pd
import random

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
db_config = {
    'host': 'localhost',
    'user': 'root',          # Replace with your MySQL username
    'password': 'Abhishekarch@#29.',  # Replace with your MySQL password
    'database': 'IITP_Timetable'
}

def generate_enrollments():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return
        
    # ==========================================
    # 2. FETCH DATA
    # ==========================================
    print("Fetching student, course, and curriculum mapping data...")
    students_df = pd.read_sql("SELECT Roll_no, Branch, Department, Level FROM student", conn)
    courses_df = pd.read_sql("SELECT Course_ID, Department, Type FROM course", conn)
    mapping_df = pd.read_sql("SELECT Branch, Level, Course_ID FROM student_enrollment", conn)
    
    conn.close()
    
    # ==========================================
    # 3. BUILD DYNAMIC CURRICULUMS
    # ==========================================
    print("Building branch-specific curriculums for UG, PG, and Ph.D...")
    
    course_type_dict = dict(zip(courses_df['Course_ID'], courses_df['Type']))
    
    dc_curriculum = {} # dict[branch][level] = [course_ids]
    de_curriculum = {} # dict[branch][level][de_type] = [course_ids]
    
    for _, row in mapping_df.iterrows():
        b = row['Branch']
        l = row['Level']
        cid = row['Course_ID']
        
        # Clean up strings to prevent mismatch errors
        ctype = str(course_type_dict.get(cid, 'UNKNOWN')).strip().upper()
        
        # Identify Department Electives dynamically (DE1, DE2, etc.)
        if ctype.startswith('DE'):
            de_curriculum.setdefault(b, {}).setdefault(l, {}).setdefault(ctype, []).append(cid)
        else:
            # Everything else mapped is treated as a Core/Mandatory class for that batch
            dc_curriculum.setdefault(b, {}).setdefault(l, []).append(cid)

    # General IDEs (B.Tech UG2)
    ide_courses = [
        {'id': row['Course_ID'], 'dept': row['Department'], 'enrolled': 0} 
        for _, row in courses_df.iterrows() if str(row['Type']).strip().upper() == 'IDE'
    ]
    
    # M.Sc. Specific IDEs
    mse_ide_courses = [
        {'id': row['Course_ID'], 'dept': row['Department'], 'enrolled': 0} 
        for _, row in courses_df.iterrows() if str(row['Type']).strip().upper() == 'IDE_MSC'
    ]

    de_tracker = {}
    enrollment_queries = []
    unassigned_ide = []
    
    # ==========================================
    # 4. PROCESS INDIVIDUAL STUDENTS
    # ==========================================
    print("Processing individual student assignments...")
    for _, student in students_df.iterrows():
        roll = student['Roll_no']
        branch = student['Branch']
        dept = student['Department']
        level_str = student['Level']
        
        # --- A. FIRST YEAR B.TECH LOGIC (UG1) ---
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
                    
        # --- B. HIGHER YEARS (UG2+, M.Tech, M.Sc) ---
        else:
            # 1. Assign Mandatory (DC/Core) based on the mapping file
            if branch in dc_curriculum and level_str in dc_curriculum[branch]:
                for c in dc_curriculum[branch][level_str]:
                    enrollment_queries.append(f"('{roll}', '{c}')")
                    
            # 2. Assign Electives (DE) - Perfectly Balanced Random Urn
            if branch in de_curriculum and level_str in de_curriculum[branch]:
                for de_type, course_list in de_curriculum[branch][level_str].items():
                    tracker_key = f"{branch}_{level_str}_{de_type}"
                    
                    if tracker_key not in de_tracker or len(de_tracker[tracker_key]) == 0:
                        de_tracker[tracker_key] = list(course_list) 
                        random.shuffle(de_tracker[tracker_key])     
                        
                    chosen_de = de_tracker[tracker_key].pop()
                    enrollment_queries.append(f"('{roll}', '{chosen_de}')")
                    
            # 3. Assign General IDE (B.Tech UG2 Only)
            if level_str == 'UG2':
                available_ides = [ide for ide in ide_courses if ide['dept'] != dept and ide['enrolled'] < 100]
                if available_ides:
                    chosen_ide = random.choice(available_ides)
                    enrollment_queries.append(f"('{roll}', '{chosen_ide['id']}')")
                    chosen_ide['enrolled'] += 1
                else:
                    unassigned_ide.append((roll, 'UG2 IDE'))

            # 4. Assign IDE_MSC (M.Sc. Students Only)
            if level_str.startswith('MS'):
                available_mse_ides = [ide for ide in mse_ide_courses if ide['dept'] != dept and ide['enrolled'] < 100]
                if available_mse_ides:
                    chosen_ide = random.choice(available_mse_ides)
                    enrollment_queries.append(f"('{roll}', '{chosen_ide['id']}')")
                    chosen_ide['enrolled'] += 1
                else:
                    unassigned_ide.append((roll, 'IDE_MSC'))

    # ==========================================
    # 5. GENERATE SQL SCRIPT
    # ==========================================
    output_filename = "student_course_enrollments_master.sql"
    print(f"Writing {len(enrollment_queries)} rows to {output_filename}...")
    
    with open(output_filename, 'w') as f:
        f.write("USE IITP_Timetable;\n")
        # Temporarily disable foreign keys to allow TRUNCATE to reset the table completely
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("TRUNCATE TABLE student_course_enrollment;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        f.write("BEGIN;\n\n")
        
        # Batch insert
        batch_size = 1000
        for i in range(0, len(enrollment_queries), batch_size):
            batch = enrollment_queries[i:i+batch_size]
            values = ",\n".join(batch)
            f.write(f"INSERT IGNORE INTO student_course_enrollment (Roll_no, Course_ID) VALUES \n{values};\n")
            
        f.write("\nCOMMIT;\n")
        
    print(f"Success! {len(enrollment_queries)} enrollment records generated.")
    
    # --- REPORTING ---
    print("\n--- B.Tech UG2 IDE Allocation Stats ---")
    for ide in sorted(ide_courses, key=lambda x: x['enrolled'], reverse=True):
        print(f"{ide['id']} ({ide['dept']}): \t{ide['enrolled']}/100 seats filled")
        
    print("\n--- M.Sc. IDE_MSC Allocation Stats ---")
    if mse_ide_courses:
        for ide in sorted(mse_ide_courses, key=lambda x: x['enrolled'], reverse=True):
            print(f"{ide['id']} ({ide['dept']}): \t{ide['enrolled']}/100 seats filled")
    else:
        print("No IDE_MSC courses found in the current database.")

    if unassigned_ide:
        print(f"\n[WARNING] {len(unassigned_ide)} students could not be assigned an IDE (Capacity reached or no interdisciplinary options available for their department).")

if __name__ == "__main__":
    generate_enrollments()