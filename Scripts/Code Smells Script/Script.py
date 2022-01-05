
#Working code against a sample test file.
with open("testFile.java") as f:
    setup_words = ("@Before", "setup()", "setUp()", "setUpTest()")
    setup = False
    test = False
    setup_mock = 0
    mock_count = 0
    
    for line in f:
        if any(s in line for s in setup_words):
            setup = True
        elif "@Test" in line:
            test = True
            setup = False
            
        if setup:
            if "mock(" in line:
                setup_mock += 1
        elif test:
            if "mock(" in line and ".class" in line:
                mock_count += 1
                
        if test and "}" in line:
            test = False
            if (mock_count + setup_mock) > 1:
                print("Bad Smell")
            mock_count = 0
                        
