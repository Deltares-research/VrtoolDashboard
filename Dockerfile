# To build this docker:
# `docker build -t vrtool_dash .`
# To run this docker:
# `docker run -p 8000:8080 vrtool_dash`

FROM python:3.12 as builder

RUN apt-get update

ARG SRC_ROOT="/vrtool_dash_src"

# Copy the directories with the local vrtool_dash
WORKDIR $SRC_ROOT

# Generate requirements files with:
COPY README.md LICENSE poetry.lock pyproject.toml $SRC_ROOT
COPY src $SRC_ROOT/src
copy externals $SRC_ROOT/externals

# Install the required packages
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev,test
# poetry export --without-hashes --format=requirements.txt > requirements.txt
# RUN pip install -r requirements.txt

# Define the endpoint
# CMD ["/bin/bash"]

CMD ["python", "-m", "src.index"]