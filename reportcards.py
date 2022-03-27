import sys
import pandas
from json import dump


# Check for the proper number and file type of arguments
if len(sys.argv) != 6 or sys.argv[1][-4:] != '.csv' or sys.argv[2][-4:] != '.csv' \
        or sys.argv[3][-4:] != '.csv' or sys.argv[4][-4:] != '.csv' or sys.argv[5][-5:] != '.json':
    # Check if an output file was supplied
    for arg in sys.argv[1:]:
        if arg[-5:] == '.json':
            error_json = {'error': 'Invalid arguments'}
            with open(arg, 'w') as out:
                dump(error_json, out)
    # No output file was found so just halt the program
    sys.exit('error: Invalid arguments')


# Writes an error message to the output file and halts the program
def write_error(message, file=sys.argv[5]):
    error_json = {'error': message}
    with open(file, 'w') as out:
        dump(error_json, out)
    sys.exit(f'error: {message}')


# Read all the csv files into dataframes, and make sure they have the proper columns
# Note that since I'm using dataframes and dictionaries, order doesn't matter, also that
# typing (specifically, castability to float) only matters for the test weights and marks
try:    # course CSV
    courses_df = pandas.read_csv(sys.argv[1], index_col='id')
    # Check if any of the required columns are missing, ID column checked on reading
    # Note that additional columns do not break any functionality
    if 'name' not in courses_df or 'teacher' not in courses_df:
        write_error(f'Missing columns in file {sys.argv[1]}')
except FileNotFoundError:
    write_error(f'Failed to find file {sys.argv[1]}')
except ValueError:  # this is to check for the ID column
    write_error(f'Missing columns in file {sys.argv[1]}')
try:    # student CSV
    students_df = pandas.read_csv(sys.argv[2], index_col='id')
    # Check if any of the required columns are missing, ID column checked on reading
    # Note that additional columns do not break any functionality
    if 'name' not in students_df:
        write_error(f'Missing columns in file {sys.argv[2]}')
except FileNotFoundError:
    write_error(f'Failed to find file {sys.argv[2]}')
except ValueError:  # this is to check for the ID column
    write_error(f'Missing columns in file {sys.argv[2]}')
try:    # test CSV
    tests_df = pandas.read_csv(sys.argv[3], index_col='id')
    # Check if any of the required columns are missing, ID column checked on reading
    # Note that additional columns do not break any functionality
    if 'course_id' not in tests_df or 'weight' not in tests_df:
        write_error(f'Missing columns in file {sys.argv[3]}')
except FileNotFoundError:
    write_error(f'Failed to find file {sys.argv[3]}')
except ValueError:  # this is to check for the ID column
    write_error(f'Missing columns in file {sys.argv[3]}')
try:    # mark CSV
    marks_df = pandas.read_csv(sys.argv[4])
    # Check if any of the required columns are missing
    # Note that additional columns do not break any functionality
    if 'test_id' not in marks_df or 'student_id' not in marks_df or 'mark' not in marks_df:
        write_error(f'Missing columns in file {sys.argv[4]}')
except FileNotFoundError:
    write_error(f'Failed to find file {sys.argv[4]}')

# print(courses_df)
# print(students_df)
# print(tests_df)
# print(marks_df)

# Make sure the test weightings for each course add up
course_dict = {}
for id in courses_df.index:
    # Check for NaN
    if id != id:
        write_error(f'Missing value in {sys.argv[1]}')
    course_dict[id] = 0
for weight, course_id in zip(tests_df['weight'], tests_df['course_id']):
    # Check for NaN
    if course_id != course_id or weight != weight:
        write_error(f'Missing value in {sys.argv[3]}')
    # Check test weightings are numbers and non-negative
    try:
        tmp = float(weight)
    except ValueError:
        write_error('Invalid test weights, non-number')
    if weight < 0:
        write_error('Invalid test weights, negative value')
    # Check that the course_id is valid, and if so add the weight
    if course_id in course_dict:
        course_dict[course_id] += weight
    else:
        write_error(f'Invalid course ID in {sys.argv[1]}')
# Check the weightings of each course
for course in course_dict:
    if course_dict[course] != 100:
        write_error('Invalid course weights')

# Populate dictionary structs for courses, students, and tests
# This will make it easier to access ___-specific information and for inserting into the json structure
for id, name, teacher in zip(courses_df.index, courses_df['name'], courses_df['teacher']):
    # Check for NaN, already checked ID
    if name != name or teacher != teacher:
        write_error(f'Missing value in {sys.argv[1]}')
    course_dict[id] = {'id': id, 'name': name, 'teacher': teacher, 'courseAverage': 0.0}
student_dict = {}
for id, name in zip(students_df.index, students_df['name']):
    # Check for NaN
    if id != id or name != name:
        write_error(f'Missing value in {sys.argv[2]}')
    student_dict[id] = {'id': id, 'name': name, 'totalAverage': 0.0, 'courses': []}
test_dict = {}
for id, course_id, weight in zip(tests_df.index, tests_df['course_id'], tests_df['weight']):
    # Check for NaN, already checked course ID and weight
    if id != id:
        write_error(f'Missing value in {sys.argv[3]}')
    test_dict[id] = [course_id, weight]

# print(course_dict)
# print(student_dict)
# print(test_dict)

# For each mark, add it to the appropriate student object
for test_id, student_id, mark in zip(marks_df['test_id'], marks_df['student_id'], marks_df['mark']):
    # Check for NaN
    if test_id != test_id or student_id != student_id or mark != mark:
        write_error(f'Missing value in {sys.argv[4]}')
    # Check that marks are numbers and non-negative
    try:
        tmp = float(mark)
    except ValueError:
        write_error('Invalid marks, non-number')
    if mark < 0:
        write_error('Invalid marks, negative value')
    # Check student_id is a valid student
    if student_id not in student_dict:
        write_error(f'Invalid student ID in {sys.argv[4]}')
    # Check test_id is a valid test
    if test_id not in test_dict:
        write_error(f'Invalid test ID in {sys.argv[4]}')
    # If the mark is for a course already in the student object, add the weight
    # -adjusted mark to the course average, if not, add the course to the course list
    # for that student and then add the weight-adjusted mark
    new_course = True
    for course in student_dict[student_id]['courses']:
        if course['id'] == test_dict[test_id][0]:
            new_course = False
            grade = mark * test_dict[test_id][1] / 100
            course['courseAverage'] += grade
    if new_course:
        # Make a copy of the course object instead of using a reference
        course = dict(course_dict[test_dict[test_id][0]])
        student_dict[student_id]['courses'].append(course)
        grade = mark * test_dict[test_id][1] / 100
        student_dict[student_id]['courses'][-1]['courseAverage'] = grade

# Initialize report card struct
reportcard_json = {'students': []}

# for each student object, add it to the list of students in the report card
for student in student_dict:
    if len(student_dict[student]['courses']) > 0:
        # add and round the course averages to get the total average
        avg = 0.0
        for course in student_dict[student]['courses']:
            course['courseAverage'] = min(course['courseAverage'], 100.0)
            avg += course['courseAverage']
            course['courseAverage'] = round(course['courseAverage'], 2)
        student_dict[student]['totalAverage'] = round(avg / len(student_dict[student]['courses']), 2)
    reportcard_json['students'].append(student_dict[student])

# write the report card data to the output file
with open(sys.argv[5], 'w') as outfile:
    dump(reportcard_json, outfile)

print(f'Report cards have been written to {sys.argv[5]}.')
