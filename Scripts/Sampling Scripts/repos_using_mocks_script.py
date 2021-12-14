import csv, requests
from pathlib import Path

# Script to shortlist repositories using test mocks.
path = Path(__file__).parent
with open(path /"data/repos_with_test.csv",encoding = "utf8") as file, open(path /"data/repos_with_mocks.csv", "a", encoding = "utf8", newline='') as out:
    csvreader = csv.reader(file)
    writer = csv.writer(out)

    for row in csvreader:
        if row[0] != "Name":
            response = requests.get("https://github.com/" + row[0] + "/blob/master/pom.xml")
            # reset count for every project
            count = 0
            if response.status_code < 400:
                # if a pom.xml file exists for a project, get its content
                content = response.text
                # check if it uses mocking
                count = content.count("mock")
                if count != 0:
                    writer.writerow(row)
                  
