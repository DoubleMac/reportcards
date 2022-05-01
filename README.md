# hatchways-mosaic
software assessment - report cards

## Complexity
Let c be the number of courses, s be the number of students, t be the number of tests, and m be the number of marks. 

First assume that for one of the CSV files, there are a number of extra columns that dominate any of the previous values, call it n. Then both time and space complexity are dominated when reading the CSV files. i.e. both are O(max(c,s,t,m)\*n). *(it may end up being a bit smaller than this if the file with the extra columns has few entries but this is the upper limit.)*

However, that is a fringe case so now assume that each of the files has an insignificant number of columns as is expected. For space, there are a constant number of structures used in the program, with most correlating linearly to one of the above values. The one exception is the report card struct which has size O(s\*c). Of course, this could be dominated by the size of the test dataframe/dict if there are enough tests (O(t)), and that could be dominated by the mark structs as m is of the order O(s\*t). Hence space complexity is O(max(c,t)\*s). For time it's a little more straightforward. The largest loop nesting is a course loop within a mark loop and all the commands within the loop(s) are constant time. Thus time complexity is O(c\*m) ~ O(c\*s\*t).

## Unit tests
Each of the following command line inputs is a demonstration of either functionality or error handling. All of the files used in these tests have been included in this repository. Please note that these commands are for a Windows environment, if you are using a Linux or Mac system please make the necessary adjustments.

Base case - This uses the example files provided in the instruction PDF, and should match the accompanying JSON file

```python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\marks.csv outputs\output.json```

Wrong number of arguments - If not exactly 5 arguments are provided, the program will look for an output file among them and error out

```python reportcards.py``` or ```python reportcards.py outputs\wrongnumberofargs.json```

Invalid type of arguments - If an argument is of the incorrect file type according to its position, the program  will look for an output file among them and error out

```python reportcards.py courses\courses.csv students\students.csv tests\tests.csv outputs\wrongfiletype.json marks\marks.csv```

Non-existent file - If one of the CSV arguments is a file that doesn't exist, the attempted reading of it will throw an exception and the program will error out

```python reportcards.py courses\courses.csv students\404.csv tests\tests.csv marks\marks.csv outputs\filenotfound.json```

Missing CSV columns - If one of the CSV arguments is missing one of its required columns (or is named incorrectly), the program should detect this and error out

```
python reportcards.py courses\noID.csv students\students.csv tests\tests.csv marks\marks.csv outputs\noid.json
python reportcards.py courses\courses.csv students\thestudentsthathathnoname.csv tests\tests.csv marks\marks.csv outputs\noname.json
```
Missing values - If one of the CSV files is missing a value, the program will error out

```python reportcards.py courses\missingvalue.csv students\students.csv tests\tests.csv marks\marks.csv outputs\missingvalue.json```

Non-numeric values - If the weights in the test CSV or the marks in the mark CSV cannot be interpreted as numbers, the program will error out

```
python reportcards.py courses\courses.csv students\students.csv tests\practicetests.csv marks\marks.csv outputs\nonnumericweights.json
python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\lettergrades.csv outputs\nonnumericmarks.json
```

Negative values - If the weights in the test CSV or the marks in the mark CSV are negative, the program will error out

```
python reportcards.py courses\courses.csv students\students.csv tests\failingonpurpose.csv marks\marks.csv outputs\negativeweights.json
python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\superfail.csv outputs\negativemarks.json
```

Invalid weightings - If the weights for a course's tests don't total 100 the program will error out

```python reportcards.py courses\courses.csv students\students.csv tests\mathishard.csv marks\marks.csv outputs\invalidweights.json```

Test for non-existent course - If the test CSV contains an invalid course ID the program will error out

```python reportcards.py courses\courses.csv students\students.csv tests\extracurriculars.csv marks\marks.csv outputs\invalidcourseid.json```

Mark for non-existent student - If the mark CSV contains an invalid student ID the program will error out

```python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\youwouldntknowhershegoestoadifferentschool.csv outputs\invalidstudentid.json```

Mark for non-existent test - If the mark CSV contains an invalid test ID the program will error out

```python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\youmeanitookthisfornothing.csv outputs\invalidtestid.json```

Float values - Test and mark CSVs will contain float values for weights/marks, report cards should be generated as expected

```python reportcards.py courses\courses.csv students\students.csv tests\floats.csv marks\floats.csv outputs\floatvalues.json```

Empty files - If every CSV file has no entries, an empty report card will be generated

```python reportcards.py courses\empty.csv students\empty.csv tests\empty.csv marks\empty.csv outputs\empty.json```

Bonus marks - If a student has a higher than 100% average in a course, the course average will be capped at 100% (same with total average)

```python reportcards.py courses\courses.csv students\students.csv tests\tests.csv marks\overachiever.csv outputs\betterthanperfect.json```
