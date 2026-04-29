import random
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# 1. Configuration: Intake per year (Sum = 816 students per batch)
# 816 students / 24 groups = exactly 34 students per group for 1st years.
intake_per_year = {
    'CSE': 86,
    'AI':  50,
    'ECE': 50,
    'EEE': 50,
    'ME':  86,
    'CEE': 70,
    'CBE': 70,
    'MME': 46,
    'MNC': 50,
    'EP':  40,
    'CST': 40,
    'ECO': 30
}

# 2. Metadata Mapping: Maps Branch to its Department and 2-letter Roll Code
branch_metadata = {
    'CSE': {'dept': 'CSE',  'code': 'CS'},
    'AI':  {'dept': 'CSE',  'code': 'AI'},
    'ECE': {'dept': 'EE',   'code': 'EC'},
    'EEE': {'dept': 'EE',   'code': 'EE'},
    'ME':  {'dept': 'ME',   'code': 'ME'},
    'CEE': {'dept': 'CEE',  'code': 'CE'},
    'CBE': {'dept': 'CBE',  'code': 'CB'},
    'MME': {'dept': 'MME',  'code': 'MM'},
    'MNC': {'dept': 'MATH', 'code': 'MC'},
    'EP':  {'dept': 'PHY',  'code': 'EP'},
    'CST': {'dept': 'CHM',  'code': 'CH'},
    'ECO': {'dept': 'HSS',  'code': 'ES'}
}

# 3. Level to Year Mapping
levels_years = {
    'UG1': '25',
    'UG2': '24',
    'UG3': '23',
    'UG4': '22'
}

def generate_students_sql(filename="student_ug.sql"):
    with open(filename, 'w') as f:
        f.write("USE IITP_Timetable;\n")
        f.write("BEGIN;\n\n") 
        
        ug1_counter = 0 # Global counter to evenly distribute 1st years into 24 groups
        
        for branch, intake in intake_per_year.items():
            dept = branch_metadata[branch]['dept']
            br_code = branch_metadata[branch]['code']
            
            # Generate students for all 4 years for this branch
            for year_level in range(1, 5):
                year = levels_years[f'UG{year_level}']
                
                for i in range(1, intake + 1):
                    # Construct format: YR-D-P-BR-AB (e.g., 25-0-01-CS-01)
                    roll_no = f"{year}01{br_code}{i:02d}"
                    name = fake.name().replace("'", "''") 
                    
                    # --- THE 1ST YEAR MODIFICATION ---
                    if year_level == 1:
                        # Distributes into 1-24 evenly
                        group_num = (ug1_counter % 24) + 1 
                        level_str = f"UG1_G{group_num}"
                        ug1_counter += 1
                    else:
                        level_str = f"UG{year_level}"
                        
                    sql = f"INSERT INTO student (Roll_no, Name, Branch, Department, Level) VALUES ('{roll_no}', '{name}', '{branch}', '{dept}', '{level_str}');\n"
                    f.write(sql)
                
        f.write("\nCOMMIT;\n")
        
    total_generated = sum(intake_per_year.values()) * 4
    print(f"Successfully generated {total_generated} student records in '{filename}'.")
    print(f"1st Year (UG1) Students generated: {ug1_counter} (Perfectly divided into 24 groups).")

if __name__ == "__main__":
    generate_students_sql()