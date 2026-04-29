import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# ==========================================
# 1. CONFIGURATION & TIME DOMAINS
# ==========================================
DB_CONFIG = {
    'host': os.getenv('HOST'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'database': os.getenv('DATABASE')
}

def generate_missing_instructor_assignments():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return

    # ==========================================
    # 2. FETCH DATA
    # ==========================================
    print("Fetching faculty, courses, and current assignments...")
    
    faculties_df = pd.read_sql("SELECT Fac_ID, Department FROM faculty", conn)
    
    # Fetch all courses EXCEPT RM6201 and any course starting with IK
    courses_df = pd.read_sql("""
        SELECT Course_ID, Department 
        FROM course 
        WHERE Course_ID != 'RM6201' AND Course_ID NOT LIKE 'IK%'
    """, conn)
    
    existing_assignments_df = pd.read_sql("SELECT Course_ID, Fac_ID FROM course_instructor", conn)
    
    conn.close()

    # ==========================================
    # 3. INITIALIZE FACULTY LOADS
    # ==========================================
    # Map each department to its list of faculties
    dept_faculties = {}
    for _, row in faculties_df.iterrows():
        dept = row['Department']
        fac_id = row['Fac_ID']
        if dept not in dept_faculties:
            dept_faculties[dept] = []
        dept_faculties[dept].append(fac_id)

    # Initialize all faculties with a load of 0
    fac_load = {row['Fac_ID']: 0 for _, row in faculties_df.iterrows()}

    # Calculate initial load from the existing course_instructor table
    assigned_courses = set(existing_assignments_df['Course_ID'].tolist())
    for _, row in existing_assignments_df.iterrows():
        fac_id = row['Fac_ID']
        if fac_id in fac_load:
            fac_load[fac_id] += 1
        else:
            # Failsafe if there's a faculty in course_instructor not mapped in the faculty table
            fac_load[fac_id] = 1 

    # ==========================================
    # 4. FILTER UNASSIGNED COURSES
    # ==========================================
    # Keep only courses that are NOT present in the existing assignments
    unassigned_courses = courses_df[~courses_df['Course_ID'].isin(assigned_courses)]
    print(f"Found {len(unassigned_courses)} courses needing instructor assignment.")

    # ==========================================
    # 5. DYNAMIC LOAD BALANCING ALGORITHM
    # ==========================================
    new_assignments = []
    unassignable = []

    for _, row in unassigned_courses.iterrows():
        c_id = row['Course_ID']
        dept = row['Department']

        # 1. Get available faculties for this specific department
        available_facs = dept_faculties.get(dept, [])

        if not available_facs:
            unassignable.append((c_id, dept))
            continue

        # 2. Find the faculty with the minimum current load
        min_fac = min(available_facs, key=lambda f: fac_load[f])
        
        # 3. Assign them to the course
        new_assignments.append((c_id, min_fac))
        
        # 4. Increment their load so they aren't overloaded on the next loop iteration
        fac_load[min_fac] += 1

    # ==========================================
    # 6. GENERATE SQL SCRIPT
    # ==========================================
    if not new_assignments:
        print("No new assignments needed. All relevant courses have instructors.")
        return

    output_filename = "assign_missing_instructors.sql"
    print(f"Writing {len(new_assignments)} new assignments to {output_filename}...")
    
    with open(output_filename, 'w') as f:
        f.write("USE IITP_Timetable;\n\n")
        f.write("BEGIN;\n\n")
        
        # Batch insert to handle large volumes cleanly
        batch_size = 100
        for i in range(0, len(new_assignments), batch_size):
            batch = new_assignments[i:i+batch_size]
            values = ",\n\t ".join([f"('{c}', '{fac}')" for c, fac in batch])
            f.write(f"INSERT IGNORE INTO course_instructor (Course_ID, Fac_ID) VALUES\n\t {values};\n\n")
            
        f.write("COMMIT;\n")

    print(f"Success! Generated {len(new_assignments)} new course-instructor assignments.")
    
    # Display unassignable courses warning (e.g., if a department has courses but 0 faculty listed)
    if unassignable:
        print("\n[WARNING] Could not assign faculty for the following courses (No faculty mapped to their department):")
        for c, d in unassignable:
            print(f"  - {c} (Dept: {d})")

if __name__ == "__main__":
    generate_missing_instructor_assignments()