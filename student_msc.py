import random
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# 1. Configuration: Intake per year (Sum = 816 students per batch)
# 816 students / 24 groups = exactly 34 students per group for 1st years.
intake_per_year = {
    'PHY': 30,
    'CHM': 30,
    'MATH': 30
}

# 2. Metadata Mapping: Maps Branch to its Department and 2-letter Roll Code
branch_metadata = {
    'MATH': {'dept': 'MATH', 'code': 'MA'},
    'PHY':  {'dept': 'PHY',  'code': 'PH'},
    'CHM': {'dept': 'CHM',  'code': 'CH'}
}

# 3. Level to Year Mapping
levels_years = {
    'MS1': '25',
    'MS2': '24',
}

def generate_students_sql(filename="student_msc.sql"):
    with open(filename, 'w') as f:
        f.write("USE IITP_Timetable;\n")
        f.write("BEGIN;\n\n") 
        
        ms1_counter = 0 # Global counter to evenly distribute 1st years into 24 groups
        
        for branch, intake in intake_per_year.items():
            dept = branch_metadata[branch]['dept']
            br_code = branch_metadata[branch]['code']
            
            # Generate students for all 2 years for this branch
            for year_level in range(1, 3):
                year = levels_years[f'MS{year_level}']
                
                for i in range(1, intake + 1):
                    # Construct format: YR-D-P-BR-AB (e.g., 25-0-01-CS-01)
                    roll_no = f"{year}12{br_code}{i:02d}"
                    name = fake.name().replace("'", "''") 
                    
                    level_str = f"MS{year_level}"
                        
                    sql = f"INSERT INTO student (Roll_no, Name, Branch, Department, Level) VALUES ('{roll_no}', '{name}', '{branch}', '{dept}', '{level_str}');\n"
                    f.write(sql)
                
        f.write("\nCOMMIT;\n")
        
    total_generated = sum(intake_per_year.values()) * 2
    print(f"Successfully generated {total_generated} student records in '{filename}'.")

if __name__ == "__main__":
    generate_students_sql()