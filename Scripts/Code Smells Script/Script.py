from github import Github, RateLimitExceededException, UnknownObjectException
import calendar, time, csv,requests

with open("final_sample.txt") as file, open("code_smell.csv", "a", encoding = "utf8", newline='') as out:
    writer = csv.writer(out)
    writer.writerow(["Name","URL of sub-project","Contributors", "# of test files","# of test units",
                     "# of test units with mocks","Total # of more than one class mocked per test","Mocks of other mocks"])
    
    setup_words = ("@Before", "setup()", "setUp()", "setUpTest()")
    
    for url in file:
        # main project name
        name = url[url.index(".com/")+5:url.index("/tree")]
        # subproject path
        path = url[url.index("master/")+7:-1]
        num_test_file = num_test_units = num_test_units_with_mocks = bad_smell = mock_of_other_mock = 0
        
        try:
            g = Github("Access Token HERE")
            repo = g.get_repo(name)
            contributors = repo.get_contributors().totalCount        
            response = requests.get(url.strip("\n") + "src/test")

            if response.status_code < 400:
                link = response.url            
                branch = repo.get_branch(link[link.index("tree/")+5:].split("/")[0])
                contents = repo.get_contents(path + "src/test")
                while contents:
                    # case where get_contents returns nonetype due to empty directories
                    try:            
                        content = contents.pop(0)
                        # ignore data and resources directories
                        if content.type == "dir" and not (content.path.endswith("resources") or content.path.endswith("data")):
                            contents.extend(repo.get_contents(content.path))

                        # if there is a test file
                        if (content.path.lower().endswith("test.java")) or (content.path.lower().endswith("tests.java")):
                            num_test_file += 1
                            file_content = content.decoded_content.decode().split("\n")
                            setup = test = mock_annot = False
                            mock_count = 0
                            mocked_classes = [] #stores instances mocked in setup
                            temp = [] # stores instances mocked in unit test
                            setup_mocks = []  # for checking the number of setup mocked classes used in each unit test                

                            for line in file_content:

                                if any(s in line for s in setup_words):
                                    setup = True
                                    mock_annot = False

                                elif "@Test" in line:
                                    test = True
                                    num_test_units += 1
                                    mock_annot = setup = False

                                elif "@Mock" in line:
                                    # consider case such as @MockService

                                    if "@Mock(" in line or len(line.split()) == 1:
                                        mock_annot = True
                                        setup = False
                                elif "@Spy" in line:
                                    mock_annot = True
                                    setup = False

                                if setup:
                                    # account for different initialisation formats
                                    # Item item = mock(Item.class)
                                    # vs Already created and item = mock(Item.class)
                                    if "mock(" in line and ".class" in line:
                                        if len(line.split()) == 4:         
                                            mocked_classes.append(line.split()[1])
                                        elif len(line.split()) == 3:         
                                            mocked_classes.append(line.split()[0])

                                elif test:
                                    if "mock(" in line and ".class" in line:
                                        class_name = line[line.index("mock(")+5: line.index(".class")]
                                        ''' allows to not count different instances of the same class
                                        e.g. if class under test is Item, we can have Item a, Item b all being mocked.'''
                                        if class_name not in temp:
                                            temp.append(class_name)                                              
                                            mock_count += 1

                                        # for case such as Context context = mock(Context.class)
                                        # then in separate test -> Mail mail = context.mock(Mail.class)                                                                            
                                        if any(c + "." in line for c in mocked_classes):
                                            mock_of_other_mock += 1

                                    elif "spy(" in line:
                                        mock_count += 1

                                    # case where test relies on classes mocked in setup test
                                    # need to check how many classes it relies upon
                                    elif any(c + "." in line for c in mocked_classes):
                                        class_instance = [c for c in mocked_classes if c in line][0] 
                                        if class_instance not in setup_mocks:
                                            setup_mocks.append(class_instance)

                                elif mock_annot:
                                    if "@Mock" not in line and "@Spy" not in line:
                                        # case where another annotation is on next line
                                        if ";" in line:
                                            mocked_classes.append(line[:line.index(";")].split()[-1])
                                            mock_annot = False

                                if test and "}" in line:                            
                                    test = False
                                    temp = [] 

                                    if mock_count > 1 or len(setup_mocks) > 1:
                                        bad_smell += 1

                                    if mock_count >= 1 or len(setup_mocks) >= 1:
                                        num_test_units_with_mocks += 1

                                    mock_count = 0
                                    setup_mocks = []

                    except StopIteration:
                        break
                    except RateLimitExceededException:
                        core_rate_limit = g.get_rate_limit().core
                        print(core_rate_limit)
                        reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
                        print("Running after " + str(round((sleep_time/60),2)) + " min ")
                        time.sleep(sleep_time)
                        continue

                writer.writerow([name, url,str(contributors), str(num_test_file),str(num_test_units), str(num_test_units_with_mocks),
                                 str(bad_smell), str(mock_of_other_mock)])
        except UnknownObjectException:
            continue
        except TypeError:
            continue
        except RateLimitExceededException:
                    core_rate_limit = g.get_rate_limit().core
                    print(core_rate_limit)
                    reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                    sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 5
                    print("Running after " + str(round((sleep_time/60),2)) + " min ")
                    time.sleep(sleep_time)
                    continue
