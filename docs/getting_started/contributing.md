# Contributing

Follow these steps to submit a PR to Heimdall and ensure a smooth review process:

## Step 1: Fork the Repository

1. **Fork**: Visit the Heimdall repository and fork it by clicking on the "Fork" button.
2. **Clone**: Clone your forked repository to your local machine.

   ```bash
   git clone https://github.com/your-user-name/heimdall.git
   ```

## Step 2: Create a New Branch

Always create a new branch for your changes.

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names like `feature/update-docstrings` or `fix/issue-123`.

## Step 3: Make Your Changes

Follow these guidelines when implementing changes:

- **Follow Code Style**: Ensure code is formatted with type hints, and docstrings follow the NumPy style.
- **Add Tests**: If your PR changes functionality or fixes a bug, include tests.
- **Document**: Update the README or other relevant documentation to reflect changes.
- **Run Tests**: Confirm all tests pass before submitting your PR.

## Step 4: Commit Changes

Use clear, concise commit messages in the format:

```
ADD/FIX/UPDATE: file_name
```

Example:

```bash
git add .
git commit -m "FIX: symbols_jar"
```

## Step 5: Push Changes

Push your branch to your forked repository.

```bash
git push origin feature/your-feature-name
```

## Step 6: Submit a PR

1. **Navigate**: Go to the original Heimdall repository and click on "New Pull Request."
2. **Select Branch**: Select the branch from your fork with your changes.
3. **Provide a Description**: Describe your changes in the PR description. Reference any related issues (e.g.,
   `Closes #123`).
4. **Request Review**: Tag reviewers if specific team members should review your PR.

---

## Example Python Function Documentation

When documenting code, follow the format below:

```python
def example_function(param1: int, param2: str) -> bool:
    """
    Example function to demonstrate documentation style.

    Parameters
    ----------
    param1 : int
        Description of the first parameter.
    param2 : str
        Description of the second parameter.

    Returns
    -------
    bool
        Description of the return value.
    """
    # Function implementation here
    return True
```

### Pull Request Template

Include the following template in your PR description:

```markdown
### Summary

Provide a concise summary of your changes and the reason for them.

### Related Issues

Closes #<issue-number> (if applicable)

### Changes Made

- Describe each change in bullet points.
- Explain why these changes are necessary.

### Tests Performed

- Detail any new or existing tests that were run and their results.

### Checklist

- [ ] Code follows project style guidelines
- [ ] Documentation updated where necessary
- [ ] All tests pass
- [ ] Linked relevant issues or user stories
```

Following this guide will help ensure that your PR is reviewed quickly and thoroughly. Thank you for contributing to
Heimdall!