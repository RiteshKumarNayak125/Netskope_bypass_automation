# Use the official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file (even if it's empty/commented for documentation)
COPY requirements.txt .
# Run pip install ONLY if requirements.txt actually lists dependencies (we removed them for this final version)
# RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files into the container
COPY automation_script.py .
COPY mock_jira_webhook.json .
COPY mock_user_history.json .

# Create the mock database file with initial content
RUN echo "# This file simulates the Netskope group 'Netskope-Bypass-Temp'" > mock_netskope_db.txt

# Command to run the application
CMD ["python", "automation_script.py"]
