# To build this docker run:
# `docker build -t vrtool_dashboard`

FROM python:3.12

RUN apt-get update

# Copy the directories with the local vrtool_dashboard.
WORKDIR /vrtool_dash_src
COPY README.md LICENSE pyproject.toml poetry.lock /vrtool_dash_src/
COPY src /vrtool_dash_src/src

# Install the required packages
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev,test
RUN apt-get clean autoclean

# Define the endpoint
CMD ["python3", "-m", "src.index"]