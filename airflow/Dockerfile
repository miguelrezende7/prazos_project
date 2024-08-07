FROM apache/airflow:2.5.1-python3.8

# Base image
# FROM apache/airflow:2.8.1

# Switch to the airflow user
USER airflow

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip install -r requirements.txt