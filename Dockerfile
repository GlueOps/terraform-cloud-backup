# Use an official Python runtime as the parent image
FROM python:3.11.9-alpine@sha256:700b4aa84090748aafb348fc042b5970abb0a73c8f1b4fcfe0f4e3c2a4a9fcca

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
