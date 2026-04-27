from flask import Flask, request, jsonify, render_template
import mysql.connector
import re

import csv
import ast
import os

app = Flask(__name__)

def load_enrollments():
    enrollments = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, '..', 'Database', 'student_course_enrollment_202604091338.sql')
    try:
        if os.path.exists(sql_file_path):
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract all ('Roll_No', 'Course_ID') pairs
                matches = re.findall(r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", content)
                for roll, course in matches:
                    roll_upper = roll.upper()
                    if roll_upper not in enrollments:
                        enrollments[roll_upper] = set()
                    enrollments[roll_upper].add(course)
            print(f"Loaded enrollments for {len(enrollments)} students.")
        else:
            print("Enrollment SQL file not found.")
    except Exception as e:
        print(f"Error loading enrollments: {e}")
    return enrollments

ENROLLMENTS = load_enrollments()

def parse_timetable_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(base_dir, '..', 'final_really_last_final.csv')
    events = []
    if not os.path.exists(csv_file_path):
        return events
        
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            events.append({
                'Event_ID': row.get('Event_ID', ''),
                'Course_ID': row.get('Course_ID', ''),
                'Type': row.get('Type', ''),
                'Groups': row.get('Groups', ''),
                'Room_name': row.get('Room_name', ''),
                'Start_Slot': int(row.get('Start_Slot', 0)),
                'Duration': int(row.get('Duration', 0)),
                'Fac_ID': row.get('Fac_ID', '')
            })
    return events

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule', methods=['POST'])
def get_schedule():
    data = request.json
    role = data.get('role')
    user_id = data.get('id', '')
    group_id_str = data.get('group', '')
    specialization = data.get('specialization', '')

    if not role:
        return jsonify({'error': 'Missing role'}), 400

    try:
        all_events = parse_timetable_csv()
        
        if not all_events:
            return jsonify({'error': 'Could not read schedule data from file.'}), 500

        if role == 'faculty':
            if not user_id:
                return jsonify({'error': 'Missing Faculty ID'}), 400
            user_id_upper = user_id.upper()
            schedule = []
            for e in all_events:
                if e.get('Fac_ID', '').upper() == user_id_upper:
                    e_copy = e.copy()
                    e_copy['Room_name'] = ''
                    schedule.append(e_copy)
            return jsonify({'schedule': schedule})

        elif role == 'student':
            user_id_upper = user_id.upper()
            my_schedule = []
            
            if not user_id_upper:
                return jsonify({'error': 'Missing Roll Number'}), 400
                
            if user_id_upper.startswith('25'):
                if not group_id_str:
                    return jsonify({'error': 'Missing Group Number'}), 400
                student_grp = int(group_id_str)
                group_search_str = f"'G{student_grp}'"
                
                for event in all_events:
                    if group_search_str in event.get('Groups', ''):
                        my_schedule.append(event)
                        
                name = f"Roll No: {user_id_upper}"
                level = f"Year 1, Group {student_grp}"
            else:
                enrolled_courses = ENROLLMENTS.get(user_id_upper, set())
                
                if not enrolled_courses:
                    return jsonify({'student': {'name': f"Roll No: {user_id_upper}", 'level': "No Enrollments Found"}, 'schedule': []})
                    
                for event in all_events:
                    if event.get('Course_ID') in enrolled_courses:
                        event_copy = event.copy()
                        event_copy['Room_name'] = ''
                        my_schedule.append(event_copy)
                
                name = f"Roll No: {user_id_upper}"
                level = f"Enrolled in {len(enrolled_courses)} Courses"

            return jsonify({'student': {'name': name, 'level': level}, 'schedule': my_schedule})
        else:
            return jsonify({'error': 'Invalid role'}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
