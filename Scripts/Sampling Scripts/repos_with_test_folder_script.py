import csv, requests
from pathlib import Path

# Script to shortlist repositories containing a test folder.
path = Path(__file__).parent
with open(path /"data/results.csv",encoding = "utf8") as file, open(path /"data/repos_with_test.csv", "a", encoding = "utf8") as out:
    csvreader = csv.reader(file)
    writer = csv.writer(out)

    for row in csvreader:
        if row[0] != "Name":
            response = requests.get("https://github.com/" + row[0] + "/tree/master/test")
            if response.status_code < 400:
                writer.writerow(row)
