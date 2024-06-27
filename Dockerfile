# Use an official Python runtime as the parent image
FROM python:3.12.4-alpine@sha256:ff870bf7c2bb546419aaea570f0a1c28c8103b78743a2b8030e9e97391ddf81b

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
