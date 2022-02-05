import csv, requests
from pathlib import Path


#Script that checks our sampled projects to see how many of them have multiple sub-projects inside them
path = Path(__file__).parent

with open(path /"data/repos_with_mocks.csv",encoding = "utf8") as file, open(path /"data/repos_without_subprojects.csv", "a", encoding = "utf8") as out:
    csvreader = csv.reader(file)
    writer = csv.writer(out)

    for row in csvreader:
        response = requests.get("https://github.com/" + row[0] + "/blob/master/test")
        if response.status_code < 400:
            writer.writerow(row)