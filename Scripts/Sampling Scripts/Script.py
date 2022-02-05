from github import Github, RateLimitExceededException
import calendar, time,csv, requests
from pathlib import Path


path = Path(__file__).parent
with open(path /"data/repos_with_mocks.csv",encoding = "utf8") as file, open(path /"data/final_sample.txt", "a", encoding = "utf8") as out:
    csvreader = csv.reader(file)
    g = Github("Access Token HERE")

    for row in csvreader:  
        repo = g.get_repo(row[0])
        contents = repo.get_contents("")
        temp = []
        paths = []

        while contents:
            try:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))

                # if path is repo/src or repo/../src
                if file_content.path.endswith("src"):
                    #if src is in the top level dir
                    if len(file_content.path) == 3:
                        response = requests.get("https://github.com/" + row[0] + "/tree/master/src/main/test")
                        if response.status_code < 400:
                            paths.append(row[0] + "/tree/master/" +  file_content.path)
                    #if path ends with src and is already in temp, add to paths
                    elif file_content.path[:-3] in temp:
                        paths.append(row[0] + "/tree/master/"  + file_content.path[:-3])
                    else:
                        temp.append(file_content.path[:-3])

                elif file_content.path.endswith("core"):

                    if len(file_content.path) == 4:
                        response = requests.get("https://github.com/" + row[0] + "/tree/master/core/main/test")
                        if response.status_code < 400:
                            paths.append(row[0] + "/tree/master/" +  file_content.path)

                    elif file_content.path[:-4] in temp:
                        paths.append(row[0] + "/tree/master/" +  file_content.path[:-4])
                    else:
                        temp.append(file_content.path[:-4])

                # if path endswith pom.xml
                elif file_content.path.endswith("pom.xml"):
                    if len(file_content.path) == 7:
                        continue
                    elif file_content.path[:-7] in temp:
                        paths.append(row[0] + "/tree/master/" + file_content.path[:-7])
                    else:
                        temp.append(file_content.path[:-7])
            except StopIteration:
                break
            except RateLimitExceededException:
                core_rate_limit = g.get_rate_limit().core
                print(core_rate_limit)
                reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
                print("Running after " + str(sleep_time/3600) + " hr ")
                time.sleep(sleep_time)
                continue
                
        for path in paths:
            response = requests.get("https://github.com/" + path + "/pom.xml")
            count = 0
            if response.status_code < 400:
                content = response.text
                count = content.count("mockito") + content.count("powermock")
                if count != 0:
                    out.write("https://github.com/" + path +  "\n")
