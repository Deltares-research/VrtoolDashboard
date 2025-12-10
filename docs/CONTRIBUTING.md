# Run coverage #

    ```bash
    pixi run -e test pytest --cov=src
    pixi run -e test pytest --cov=src --cov-report html:coverage-reports/html
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


# Solve bug with miniforge and poetry #
Commands like `poetry build` or `poetry install` might raise an error like this:

    ```bash
    Command C:\Users\hauth\miniforge3\envs\vrtool_dash\python.exe -I -W ignore - errored with the following return code 1, and output:
    The system cannot find the path specified.
    C:\Users\hauth\miniforge3\envs\vrtool_dash
    input was : import sys

    if hasattr(sys, "real_prefix"):
        print(sys.real_prefix)
    elif hasattr(sys, "base_prefix"):
        print(sys.base_prefix)
    else:
        print(sys.prefix)
    ```
A solution is to force poetry to reinstall

        ```bash
        conda remove poetry
        conda install poetry
        poetry --version
        poetry env use C:/Users/hauth/miniforge3/envs/vrtool_dash/python.exe
        ```
Then try again to build the wheel with `poetry build` again.


# install with pip #
poetry export -f requirements.txt > requirements.txt 
pip install -r requirements.txt
