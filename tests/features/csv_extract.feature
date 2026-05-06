Feature: CSV Extract and Pair Building

  Scenario: Series1Pair builds correct XYPair
    Given a row with x123 "10.0" and y1 "8.04"
    When we build a pair using Series1Pair
    Then the pair should have x "10.0" and y "8.04"

  Scenario: Series1Pair handles missing values
    Given a row with missing x123 and y1
    When we build a pair using Series1Pair
    Then the pair should have x "" and y ""

  Scenario: Extract builds pairs from valid CSV
    Given a valid CSV file at "data/test_valid.csv"
    When we extract pairs using Series1Pair
    Then we should get a list of pairs

  Scenario: Extract fails when file does not exist
    Given a non-existent CSV path "data/missing.csv"
    When we try to extract pairs
    Then an error should occur

  Scenario: Extract fails on missing headers
    Given a CSV file with missing headers at "data/test_bad_headers.csv"
    When we try to extract pairs
    Then a header error should occur