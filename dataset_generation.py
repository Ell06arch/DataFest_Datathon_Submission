import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)

def generate_students(num_students, age_range, gender_ratio, grade_distribution, department_distribution, department_gender_distribution,study_hours_ratio):
    data = []
    departments = []
    
    # Create department distribution
    department_ids = {
        'Science': 1,
        'Arts': 2,
        'Commercial': 3
    }
    
    # Calculate the number of students for each department
    num_science = int(num_students * department_distribution['Science'])
    num_arts = int(num_students * department_distribution['Arts'])
    num_commerce = int(num_students * department_distribution['Commercial'])
    
    # Fill the department list based on gender distribution
    for _ in range(num_science):
        gender = 'Male' if random.random() < department_gender_distribution['Science']['male'] else 'Female'
        departments.append(department_ids['Science'])
    for _ in range(num_arts):
        gender = 'Male' if random.random() < department_gender_distribution['Arts']['male'] else 'Female'
        departments.append(department_ids['Arts'])
    for _ in range(num_commerce):
        gender = 'Male' if random.random() < department_gender_distribution['Commercial']['male'] else 'Female'
        departments.append(department_ids['Commercial'])
    
    random.shuffle(departments)  # Shuffle to mix department assignments


    for i in range(num_students):
        age = random.randint(age_range[0], age_range[1])
        gender = 'Male' if random.random() < gender_ratio else 'Female'
        grade_level = np.random.choice(list(grade_distribution.keys()), p=list(grade_distribution.values()))
        study_hours = np.random.choice(list(study_hours_ratio.keys()), p=list(study_hours_ratio.values()))
        data.append({
            'student_id': fake.unique.random_number(digits=5),
            'date_of_birth': fake.date_of_birth(minimum_age=age, maximum_age=age),
            'gender': gender,
            'grade_level': grade_level,
            'department_id': departments[i],
            'study_hours': study_hours  # Assign department ID
        })
    return pd.DataFrame(data)

# Define the pass rates
pass_rates = {
    'Science': {
        'WAEC': {'General': 0.65, 'Male': 0.68, 'Female': 0.32},
        'JAMB': {'General': 0.60, 'Male': 0.63, 'Female': 0.27}
    },
    'Commercial': {
        'WAEC': {'General': 0.60, 'Male': 0.62, 'Female': 0.38},
        'JAMB': {'General': 0.55, 'Male': 0.57, 'Female': 0.43}
    },
    'Arts': {
        'WAEC': {'General': 0.58, 'Male': 0.60, 'Female': 0.56},
        'JAMB': {'General': 0.53, 'Male': 0.55, 'Female': 0.51}
    }
}

def generate_academic_performance(students, classes, exams, subject_averages, departments):
    data = []
    for _, student in students.iterrows():
        # Get the student's department based on department_id
        if student['department_id'] != 0:
            department_row = departments[departments['department_id'] == student['department_id']]
            student_department = department_row.iloc[0]['department_name']  # Assuming this is the correct key for the department name
            student_subjects = ['Mathematics', 'English'] + department_row.iloc[0]['core_subjects']
        else:
            student_department = 'General'  # Default department if none selected
            student_subjects = ['Mathematics', 'English', 'Physics', 'Chemistry', 'Biology', 'Literature', 'Government', 'Economics', 'Commerce', 'Accounting', 'History']

        # Generate results for each exam and only the subjects related to the student
        for _, exam in exams.iterrows():
            for subject in student_subjects:
                class_id = classes[(classes['subject'] == subject) & (classes['grade_level'] == student['grade_level'])]['class_id'].values[0]
                score = np.clip(np.random.normal(subject_averages[subject], 10), 0, 100)

                # Determine pass rates based on department and exam type
                if student_department in pass_rates:
                    gender = 'Male' if student['gender'] == 'M' else 'Female'
                    pass_rate = pass_rates[student_department][exam['exam_type']][gender]
                    passed = random.random() < pass_rate
                else:
                    passed = random.random() < 0.5  # Default pass rate if department is not recognized

                data.append({
                    'student_id': student['student_id'],
                    'class_id': class_id,
                    'exam_id': exam['exam_id'],
                    'subject': subject,
                    'score': round(score, 2),
                    'exam_date': exam['exam_date'],
                    'passed': passed
                })
    return pd.DataFrame(data)


def generate_attendance(students, start_date, end_date, avg_attendance_rate, absence_reasons):
    data = []
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B' for business days
    for _, student in students.iterrows():
        for date in date_range:
            is_present = random.random() < avg_attendance_rate
            reason = np.random.choice(list(absence_reasons.keys()), p=list(absence_reasons.values())) if not is_present else None
            data.append({
                'student_id': student['student_id'],
                'date': date,
                'is_present': is_present,
                'absence_reason': reason
            })
    return pd.DataFrame(data)

def generate_socioeconomic_data(students, income_distribution, internet_access_rate, distance_distribution,parental_education_distribution):
    data = []
    for _, student in students.iterrows():
        income_bracket = np.random.choice(list(income_distribution.keys()), p=list(income_distribution.values()))
        parental_education = np.random.choice(list(parental_education_distribution.keys()), p=list(parental_education_distribution.values()))
        data.append({
            'student_id': student['student_id'],
            'family_income_bracket': income_bracket,
            'number_of_siblings': random.randint(0, 5),
            'distance_from_school': round(random.choice(distance_distribution), 2),
            'has_internet_at_home': random.random() < internet_access_rate,
            'has_personal_computer': random.random() < (internet_access_rate * 0.8),  # Assuming slightly lower than internet access
            'parental_education': parental_education
        })
    return pd.DataFrame(data)

def generate_teachers(num_teachers, subject_list, experience_distribution, qualification_distribution):
    data = []
    for _ in range(num_teachers):
        subjects = random.sample(subject_list, random.randint(1, 3))
        data.append({
            'teacher_id': fake.unique.random_number(digits=4),
            'qualification': np.random.choice(list(qualification_distribution.keys()), p=list(qualification_distribution.values())),
            'years_of_experience': np.random.choice(list(experience_distribution.keys()), p=list(experience_distribution.values())),
            'subjects_taught': ', '.join(subjects)
        })
    return pd.DataFrame(data)

def generate_classes(teachers, subjects, grade_levels, academic_year):
    data = []
    class_id = 1
    for subject in subjects:
        for grade in grade_levels:
            teacher = teachers[teachers['subjects_taught'].str.contains(subject)].sample(1)
            data.append({
                'class_id': class_id,
                'teacher_id': teacher['teacher_id'].values[0],
                'subject': subject,
                'grade_level': grade,
                'academic_year': academic_year
            })
            class_id += 1
    return pd.DataFrame(data)

def generate_resources(resource_list, quantity_distribution):
    data = []
    for resource, resource_type in resource_list:
        data.append({
            'resource_id': fake.unique.random_number(digits=3),
            'resource_name': resource,
            'resource_type': resource_type,
            'quantity_available': np.random.choice(list(quantity_distribution.keys()), p=list(quantity_distribution.values()))
        })
    return pd.DataFrame(data)

def generate_resource_utilization(students, resources, start_date, end_date, utilization_rate):
    data = []
    date_range = pd.date_range(start=start_date, end=end_date)
    for _, student in students.iterrows():
        for date in date_range:
            if random.random() < utilization_rate:
                resource = resources.sample(1).iloc[0]
                data.append({
                    'student_id': student['student_id'],
                    'resource_id': resource['resource_id'],
                    'usage_datetime': fake.date_time_between(start_date=date, end_date=date + timedelta(days=1)),
                    'duration_minutes': random.randint(15, 120)
                })
    return pd.DataFrame(data)

def generate_extracurricular(students, activities, participation_rate):
    data = []
    for _, student in students.iterrows():
        if random.random() < participation_rate:
            activity = random.choice(activities)
            data.append({
                'student_id': student['student_id'],
                'activity_name': activity,
                'role': random.choice(['Member', 'Leader']),
                'hours_per_week': random.randint(1, 10)
            })
    return pd.DataFrame(data)

def generate_behavioral_data(students, disciplinary_rate, award_rate):
    data = []
    for _, student in students.iterrows():
        data.append({
            'student_id': student['student_id'],
            'disciplinary_incidents': np.random.poisson(disciplinary_rate),
            'awards_received': np.random.poisson(award_rate),
        })
    return pd.DataFrame(data)

def generate_departments():
    departments = [
        {'department_id': 1, 'name': 'Science', 'core_subjects': ['Physics', 'Chemistry', 'Biology']},
        {'department_id': 2, 'name': 'Arts', 'core_subjects': ['Literature', 'Government', 'History']},
        {'department_id': 3, 'name': 'Commercial', 'core_subjects': ['Economics', 'Accounting', 'Commerce']}
    ]
    return pd.DataFrame(departments)


def generate_exams(exam_schedule):
    data = []
    for exam_name, exam_info in exam_schedule.items():
        data.append({
            'exam_id': fake.unique.random_number(digits=3),
            'exam_name': exam_name,
            'exam_type': exam_info['type'],
            'exam_date': exam_info['date']
        })
    return pd.DataFrame(data)

def generate_all_data(config):
    print('leggo!')
    students = generate_students(config['num_students'], config['age_range'], config['gender_ratio'], config['grade_distribution'],config['department_distribution'],config['department_gender_distribution'],config['study_hours_ratio'])
    students.to_csv('students.csv', index=False)
    

    teachers = generate_teachers(config['num_teachers'], config['subjects'], config['experience_distribution'], config['qualification_distribution'])
    teachers.to_csv('teachers.csv', index=False)

    classes = generate_classes(teachers, config['subjects'], config['grade_levels'], config['academic_year'])
    classes.to_csv('classes.csv', index=False)

    departments = generate_departments()
    departments.to_csv('departments.csv', index=False)

    exams = generate_exams(config['exam_schedule'])
    exams.to_csv('exams.csv', index=False)
    print('generated students,teachers,classes departments and exams')

    print('generating academic performace,attendace,socioeconomic data and recources')
    academic_performance = generate_academic_performance(students, classes, exams, config['subject_averages'], config['pass_rates'],departments=departments)
    academic_performance.to_csv('academic_performance.csv', index=False)

    attendance = generate_attendance(students, config['start_date'], config['end_date'], config['avg_attendance_rate'], config['absence_reasons'])
    attendance.to_csv('attendance.csv', index=False)

    socioeconomic_data = generate_socioeconomic_data(students, config['income_distribution'], config['internet_access_rate'], config['distance_distribution'],config['parental_education_distribution'])
    socioeconomic_data.to_csv('socioeconomic_data.csv', index=False)

    resources = generate_resources(config['resource_list'], config['quantity_distribution'])
    resources.to_csv('resources.csv', index=False)
    print('done genrating now genrating other stuff chill!')

    resource_utilization = generate_resource_utilization(students, resources, config['start_date'], config['end_date'], config['resource_utilization_rate'])
    resource_utilization.to_csv('resource_utilization.csv', index=False)

    extracurricular = generate_extracurricular(students, config['activities'], config['extracurricular_participation_rate'])
    extracurricular.to_csv('extracurricular.csv', index=False)

    behavioral_data = generate_behavioral_data(students, config['disciplinary_rate'], config['award_rate'])
    behavioral_data.to_csv('behavioral_data.csv', index=False)

    print("All data generated and saved to CSV files.")

# Example usage:
config = {
    'num_students': 1000,
    'age_range': (16, 18),
    'gender_ratio': 0.52,  # Proportion of males
    'grade_distribution': {'SS1': 0.15, 'SS2': 0.15, 'SS3': 0.7},
    'num_teachers': 50,
    'subjects': ['Mathematics', 'English', 'Physics', 'Chemistry', 'Biology', 'Literature', 'Government', 'Economics','Commerce', 'Accounting','History'],
    'experience_distribution': {1: 0.1, 5: 0.3, 10: 0.4, 15: 0.15, 20: 0.05},
    'qualification_distribution': {'B.Ed': 0.3, 'NCE': 0.45, 'PGDE': 0.15, 'HND': 0.1},
    'grade_levels': ['SS1', 'SS2', 'SS3'],
    'study_hours_ratio':{1: 0.3,2: 0.25,3: 0.2,4: 0.1,5: 0.05,6: 0.03,7: 0.03,8: 0.02,9: 0.01,10: 0.01},
    'academic_year': 2024,
    'department_distribution':{'Science': 0.4,'Arts': 0.3,'Commercial': 0.3},
    'department_gender_distribution':{'Science': {'male': 0.52, 'female': 0.48},'Arts': {'male': 0.50, 'female': 0.50},'Commercial': {'male': 0.60, 'female': 0.40}},
    'subject_averages': {'Mathematics': 65, 'English': 70, 'Physics': 60, 'Chemistry': 62, 'Biology': 68, 'Literature': 72, 'Government': 75, 'Economics': 70,'Commerce':73, 'Accounting':69,'History':67},
    'pass_rates': {'Mathematics': 0.7, 'English': 0.75, 'Physics': 0.65, 'Chemistry': 0.68, 'Biology': 0.72, 'Literature': 0.78, 'Government': 0.8, 'Economics': 0.75,'Commerce':.76, 'Accounting':.71,'History':.74},
    'start_date': '2023-09-01',
    'end_date': '2024-07-31',
    'avg_attendance_rate': 0.80,
    'absence_reasons': {'Illness': 0.5, 'Family emergency': 0.2, 'Transportation issues': 0.2, 'Other': 0.1},
    'income_distribution': {'Low': 0.5, 'Middle': 0.4, 'High': 0.1},
    'internet_access_rate': 0.30,
    'distance_distribution': [0.5, 1, 2, 3, 5, 10],  # in km
    'parental_education_distribution': {"secondary": .3,"Bachelor's": 0.15,"no formal": 0.3,"Primary":0.25},
    'resource_list': [('Textbook', 'Book'), ('Computer', 'Technology'), ('Microscope', 'Lab Equipment')],
    'quantity_distribution': {10: 0.1, 50: 0.3, 100: 0.4, 200: 0.2},
    'resource_utilization_rate': 0.3,
    'activities': ['Football', 'Debate Club', 'Science Club', 'Art Club', 'Music Band'],
    'extracurricular_participation_rate': 0.6,
    'disciplinary_rate': 0.5,
    'award_rate': 0.3,
    'exam_schedule': {
        'First Term Exam': {'type': 'Internal', 'date': '2023-12-15'},
        'Second Term Exam': {'type': 'Internal', 'date': '2024-03-25'},
        'Third Term Exam': {'type': 'Internal', 'date': '2024-07-10'},
        'JAMB Mock Exam': {'type': 'External', 'date': '2024-04-15'}
    }
}

generate_all_data(config)