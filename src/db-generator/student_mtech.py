import random
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# 1. Configuration: Intake per year (Sum = 816 students per batch)
# 816 students / 24 groups = exactly 34 students per group for 1st years.
intake_per_year = {
    'CSE': 27,
    'AI': 60,
    'MNC': 21,
    'MSE': 20,
    'CM': 21,
    'PC': 12,
    'VL': 14,
    'EV': 12,
    'RK': 12,
    'TS': 12,
    'ST': 17,
    'GT': 17,
    'TF': 17,
    'MD': 17,
    'AM': 17,
    'MT': 21,
    'CBE': 17
}

# 2. Metadata Mapping: Maps Branch to its Department and 2-letter Roll Code
branch_metadata = {
    'CSE': {'dept': 'CSE', 'code': 'CS'},
    'AI':  {'dept': 'CSE',  'code': 'AI'},
    'MNC': {'dept': 'MATH',  'code': 'MC'},
    'MSE': {'dept': 'MME', 'code': 'MS'},
    'CM': {'dept': 'EE', 'code': 'CM'},
    'PC': {'dept': 'EE', 'code': 'PC'},
    'VL': {'dept': 'EE', 'code': 'VL'},
    'EV': {'dept': 'CEE', 'code': 'EV'},
    'RK': {'dept': 'CEE', 'code': 'RK'},
    'TS': {'dept': 'CEE', 'code': 'TS'},
    'ST': {'dept': 'CEE', 'code': 'ST'},
    'GT': {'dept': 'CEE', 'code': 'GT'},
    'TF': {'dept': 'ME', 'code': 'TF'},
    'MD': {'dept': 'ME', 'code': 'MD'},
    'AM': {'dept': 'ME', 'code': 'AM'},
    'MT': {'dept': 'ME', 'code': 'MT'},
    'CBE': {'dept': 'CBE', 'code': 'CB'}
}

# 3. Level to Year Mapping
levels_years = {
    'MT1': '25',
    'MT2': '24',
}

def generate_students_sql(filename="student_mtech.sql"):
    with open(filename, 'w') as f:
        f.write("USE IITP_Timetable;\n")
        f.write("BEGIN;\n\n") 
        
        mt1_counter = 0 # Global counter to evenly distribute 1st years into 24 groups
        
        for branch, intake in intake_per_year.items():
            dept = branch_metadata[branch]['dept']
            br_code = branch_metadata[branch]['code']
            
            # Generate students for all 2 years for this branch
            for year_level in range(1, 3):
                year = levels_years[f'MT{year_level}']
                
                for i in range(1, intake + 1):
                    # Construct format: YR-D-P-BR-AB (e.g., 25-0-01-CS-01)
                    roll_no = f"{year}11{br_code}{i:02d}"
                    name = fake.name().replace("'", "''") 
                    
                    level_str = f"MT{year_level}"
                        
                    sql = f"INSERT INTO student (Roll_no, Name, Branch, Department, Level) VALUES ('{roll_no}', '{name}', '{branch}', '{dept}', '{level_str}');\n"
                    f.write(sql)
                
        f.write("\nCOMMIT;\n")
        
    total_generated = sum(intake_per_year.values()) * 2
    print(f"Successfully generated {total_generated} student records in '{filename}'.")

if __name__ == "__main__":
    generate_students_sql()