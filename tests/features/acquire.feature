Feature: Data Acquisition CLI

  Scenario: Successfully extracts all four series
    Given the "data/Anscombe_quartet_data.csv" source file exists
    And the "output/test_quartet" directory exists
    When we run command "python src/acquire.py --force -o output/test_quartet data/Anscombe_quartet_data.csv"
    Then the "output/test_quartet/series_1.json" file exists
    And the "output/test_quartet/series_2.json" file exists
    And the "output/test_quartet/series_3.json" file exists
    And the "output/test_quartet/series_4.json" file exists
    And the "output/test_quartet/series_1.json" file starts with '{"x": "10.0", "y": "8.04"}'
    And the log contains "All series files written successfully."


  Scenario: Output directory does not exist
    Given the "data/Anscombe_quartet_data.csv" source file exists
    And the "output/test_quartet" directory does not exist
    When we run command "python src/acquire.py --force -o output/test_quartet data/Anscombe_quartet_data.csv"
    Then the exit code is not 0
    And the log contains "Output directory does not exist:"

  Scenario: Unknown command-line option
    Given the "data/Anscombe_quartet_data.csv" source file exists
    And the "output/test_quartet" directory exists
    When we run command "python acquire.py --unknown ../data/Anscombe_quartet_data.csv"
    Then the exit code is not 0

  Scenario: CSV path is not a file
    Given the "data/test_dir.csv" source path is a directory, not a file
    And the "output/test_quartet" directory exists
    When we run command "python src/acquire.py --force -o output/test_quartet data/test_dir.csv"
    Then the exit code is not 0
    And the log contains "CSV path is not a file:"