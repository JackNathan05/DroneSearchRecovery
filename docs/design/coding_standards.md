## Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use meaningful variable and function names
- Use docstrings for all classes and functions

## Documentation

- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Include type hints for function parameters and return values
- Document complex algorithms with comments explaining the approach

## File Organization

- Group related functionality in modules
- Keep modules focused on a single responsibility
- Limit file size to 500 lines when possible; split larger files

## Error Handling

- Use explicit exception handling with specific exception types
- Log all exceptions with appropriate context
- Provide user-friendly error messages in the UI

## Testing

- Write unit tests for all non-UI modules
- Aim for at least 80% code coverage
- Tests should be independent and repeatable

## Version Control

- Write clear, descriptive commit messages
- Use feature branches for new development
- Perform code reviews before merging to main branch

## Naming Conventions

- Classes: CamelCase (e.g., `MissionPlanner`)
- Functions/Methods: snake_case (e.g., `calculate_path`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_ALTITUDE`)
- Private attributes/methods: prefix with underscore (e.g., `_internal_method`)

## UI Development

- Separate UI design from business logic
- Use Qt Designer for complex UI components
- Follow the application color scheme defined in config.py