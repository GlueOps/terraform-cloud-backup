# Use an official Python runtime as the parent image
FROM python:3.11.9-alpine@sha256:eb8afe385f10ccc9da8378e8712fea8b26f4ed009648f8afea4518836d8b3ed3

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
