# Use an official Python runtime as the parent image
FROM python:3.11.10-alpine@sha256:f089154eb2546de825151b9340a60d39e2ba986ab17aaffca14301b0b961a11c

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
