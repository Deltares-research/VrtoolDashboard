# Run coverage #

    ```bash
    poetry run pytest --cov=src
    poetry run pytest --cov=src --cov-report html:coverage-reports/html
    ```


# Add git tag #

Please, don't forget to first update the changelog when creating a new tag.

    ```bash
    git tag -a v0.0.0 -m "v0.0.0"
    git push origin v0.0.0
    ```

# Publish #

1. Update the changelog 
2. Update the version in `pyproject.toml`
3. Change the vrtool version to vrtool = "0.1.3" in the `pyproject.toml` file
vrtool = {path = "externals/vrtool/vrtool-0.1.3.tar.gz"} is for development only.
4. Create a git tag and push it
5. build the wheel: `poetry build`
