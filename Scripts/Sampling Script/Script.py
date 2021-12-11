import csv, requests
from pathlib import Path
repos = []

path = Path(__file__).parent / "results.csv"
with open(path,encoding = "utf8") as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        if row[0] != "Name":
            response = requests.get("https://github.com/" + row[0] + "/tree/master/test")
            if response.status_code < 400:
                repos.append(row[0])

print(repos)