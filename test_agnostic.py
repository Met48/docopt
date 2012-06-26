from language_agnostic_test.language_agnostic_tester import generate_cases, check_case


def test_agnostic():
    for _, argv, doc, expect in generate_cases():
        yield check_case, 'testee.py', argv, doc, expect
