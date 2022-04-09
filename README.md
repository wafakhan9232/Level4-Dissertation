# Is doubling/mocking hiding bad code smells?
A PROJECT BY UNIVERSITY OF GLASGOW
Derek Somerville
Wafa Khan Tareen

The project investigates bad code smells associated with mocking. 

The script takes an input file, extracts the link to a project , and navigates to this link to get test files of the project and analyses them to find code smells.

We regard a mock to be a smell if:
* A unit test mocks more than one class
* A unit test has a mock which is mocking another mock

If a unit test contains these smells, we only count them once, regardless of how many classes are mocked or how many mocks of mocks are there.


