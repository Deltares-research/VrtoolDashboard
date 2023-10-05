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

