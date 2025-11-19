from hello import main

def test_main_prints():
    # this is a trivial test: calling main should not error
    main()
    assert True