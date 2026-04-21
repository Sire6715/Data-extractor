Feature: The Cheerful Greeting CLI interface provides a greeting to a specific name.

Scenario: When requested, the application writes the greeting message.
     When we run command "python src/hello_world.py"
     Then output has "Hello, World!"