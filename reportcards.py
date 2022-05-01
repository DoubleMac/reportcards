import sys
import pandas
from json import dump


# Check for the proper number and file type of arguments
if (
    len(sys.argv) != 6
    or sys.argv[1][-4:] != ".csv"
    or sys.argv[2][-4:] != ".csv"
    or sys.argv[3][-4:] != ".csv"
    or sys.argv[4][-4:] != ".csv"
    or sys.argv[5][-5:] != ".json"
):
    # Check if an output file was supplied
    for arg in sys.argv[1:]:
        if arg[-5:] == ".json":
            error_content = {"error": "Invalid arguments"}
            with open(arg, "w") as out:
                dump(error_content, out)
    sys.exit("error: Invalid arguments")


# Writes an error message to the output file and halts the program
def write_error(message, file=sys.argv[5]):
    error_json = {"error": message}
    with open(file, "w") as out:
        dump(error_json, out)
    sys.exit(f"error: {message}")


# Reads the CSV file and checks if it is correctly formatted
# Note that additional columns do not break any functionality
def try_read_csv(file, columns=[], id_col=""):
    try:
        if id_col == "":
            df = pandas.read_csv(file)
        else:
            df = pandas.read_csv(file, index_col=id_col)
            for id in df.index:
                if id != id:
                    write_error(f"Missing value in {file}")
        for col in columns:
            if col not in df:
                write_error(f"Missing columns in file {file}")
            for item in df[col]:
                if item != item:
                    write_error(f"Missing value in {file}")
        return df
    except FileNotFoundError:
        write_error(f"Failed to find file {file}")
    except ValueError:  # this is to check for the ID column
        write_error(f"Missing columns in file {file}")


# Checks if input is a number and non-negative
def valid_number(num, name):
    try:
        float(num)
    except ValueError:
        write_error(f"Invalid {name}, non-number")
    if weight < 0:
        write_error(f"Invalid {name}, negative value")


# Read all the csv files into dataframes
# Note that since I'm using dataframes and dictionaries, column order doesn't matter, also that
# typing (specifically, castability to float) only matters for the test weights and marks
courses_df = try_read_csv(sys.argv[1], ["name", "teacher"], "id")
students_df = try_read_csv(sys.argv[2], ["name"], "id")
tests_df = try_read_csv(sys.argv[3], ["course_id", "weight"], "id")
marks_df = try_read_csv(sys.argv[4], ["test_id", "student_id", "mark"])

# Make sure the test weightings for each course add up
course_dict = {}
for id in courses_df.index:
    course_dict[id] = 0
for weight, course_id in zip(tests_df["weight"], tests_df["course_id"]):
    valid_number(weight, "weights")
    if course_id in course_dict:
        course_dict[course_id] += weight
    else:
        write_error(f"Invalid course ID in {sys.argv[1]}")
for course in course_dict:
    if course_dict[course] != 100:
        write_error("Invalid course weights")

# Populate dictionary structs for courses, students, and tests
# This will make it easier to access ___-specific information and for inserting into the json structure
for id, name, teacher in zip(
    courses_df.index, courses_df["name"], courses_df["teacher"]
):
    course_dict[id] = {"id": id, "name": name, "teacher": teacher, "courseAverage": 0.0}
student_dict = {}
for id, name in zip(students_df.index, students_df["name"]):
    student_dict[id] = {"id": id, "name": name, "totalAverage": 0.0, "courses": []}
test_dict = {}
for id, course_id, weight in zip(
    tests_df.index, tests_df["course_id"], tests_df["weight"]
):
    test_dict[id] = [course_id, weight]

# For each mark, add it to the appropriate student object
for test_id, student_id, mark in zip(
    marks_df["test_id"], marks_df["student_id"], marks_df["mark"]
):
    valid_number(mark, "marks")
    if student_id not in student_dict:
        write_error(f"Invalid student ID in {sys.argv[4]}")
    if test_id not in test_dict:
        write_error(f"Invalid test ID in {sys.argv[4]}")

    # If the mark is for a course already in the student object, add the weight
    # -adjusted mark to the course average, if not, add the course to the course list
    # for that student and then add the weight-adjusted mark
    new_course = True
    for course in student_dict[student_id]["courses"]:
        if course["id"] == test_dict[test_id][0]:
            new_course = False
            grade = mark * test_dict[test_id][1] / 100
            course["courseAverage"] += grade
    if new_course:
        course = dict(course_dict[test_dict[test_id][0]])
        student_dict[student_id]["courses"].append(course)
        grade = mark * test_dict[test_id][1] / 100
        student_dict[student_id]["courses"][-1]["courseAverage"] = grade

# Initialize report card struct
reportcard_json = {"students": []}

# for each student object, add it to the list of students in the report card
for student in student_dict:
    if len(student_dict[student]["courses"]) > 0:
        # add and round the course averages to get the total average
        avg = 0.0
        for course in student_dict[student]["courses"]:
            course["courseAverage"] = min(course["courseAverage"], 100.0)
            avg += course["courseAverage"]
            course["courseAverage"] = round(course["courseAverage"], 2)
        student_dict[student]["totalAverage"] = round(
            avg / len(student_dict[student]["courses"]), 2
        )
    reportcard_json["students"].append(student_dict[student])

# write the report card data to the output file
with open(sys.argv[5], "w") as outfile:
    dump(reportcard_json, outfile)

print(f"Report cards have been written to {sys.argv[5]}.")
