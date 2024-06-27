# Use an official Python runtime as the parent image
FROM python:3.11.9-alpine@sha256:5745fa2b8591a756160721b8305adba3972fb26a9132789ed60160f21e55f5dc

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
