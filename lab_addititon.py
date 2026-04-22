import mysql.connector
import pandas as pd
import random

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Replace with your MySQL username
    'password': 'Abhishekarch@#29.',  # Replace with your MySQL password
    'database': 'IITP_Timetable'
}

def generate_lab_assignments():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return

    # ==========================================
    # 2. FETCH DATA FROM EXISTING TABLES
    # ==========================================
    print("Fetching courses with P > 0 and available labs...")
    
    # Fetch all courses that have practical components (P > 0)
    courses_df = pd.read_sql("SELECT Course_ID, Department FROM course WHERE P > 0", conn)
    
    # Fetch all rooms designated as 'LAB'
    labs_df = pd.read_sql("SELECT Room_name, Department FROM classrooms_labs WHERE Type = 'LAB'", conn)
    
    conn.close()

    # ==========================================
    # 3. BUILD DEPARTMENT-TO-LAB MAPPING
    # ==========================================
    dept_labs = {}
    for _, row in labs_df.iterrows():
        dept = row['Department']
        room = row['Room_name']
        if dept not in dept_labs:
            dept_labs[dept] = []
        dept_labs[dept].append(room)

    # ==========================================
    # 4. ASSIGN LABS RANDOMLY UNIFORMLY
    # ==========================================
    update_queries = []
    unassigned_courses = []

    for _, course in courses_df.iterrows():
        c_id = course['Course_ID']
        dept = course['Department']

        # Check if the department actually has any labs defined
        if dept in dept_labs and len(dept_labs[dept]) > 0:
            # Select uniformly random lab from the same department
            chosen_lab = random.choice(dept_labs[dept])
            update_queries.append(f"UPDATE course SET Lab = '{chosen_lab}' WHERE Course_ID = '{c_id}';")
        else:
            unassigned_courses.append((c_id, dept))

    # ==========================================
    # 5. GENERATE THE SQL UPDATE SCRIPT
    # ==========================================
    output_filename = "update_course_labs.sql"
    print(f"Writing assignments to {output_filename}...")
    
    with open(output_filename, 'w') as f:
        f.write("USE IITP_Timetable;\n\n")
        
        # 1. Add the column (Using ADD COLUMN IF NOT EXISTS logic implicitly by ignoring error if it exists, 
        # but pure SQL requires checking or simple execution). 
        # We will add it directly. If you run it twice, this first line might throw an error, 
        # but the UPDATEs will still work.
        f.write("-- 1. Add the new 'Lab' column to the course table\n")
        f.write("ALTER TABLE course ADD COLUMN Lab VARCHAR(20) DEFAULT NULL;\n\n")
        
        f.write("-- 2. Update courses where P > 0\n")
        f.write("BEGIN;\n\n")
        
        for q in update_queries:
            f.write(q + "\n")
            
        f.write("\nCOMMIT;\n")

    print(f"Success! Generated {len(update_queries)} lab assignments.")
    
    # Warnings for edge cases
    if unassigned_courses:
        print("\n[WARNING] The following practical courses could not be assigned a lab because their department has no labs defined in the 'classrooms_labs' table:")
        for c, d in unassigned_courses:
            print(f"  - {c} (Dept: {d})")

if __name__ == "__main__":
    generate_lab_assignments()