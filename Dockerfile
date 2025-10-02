# 1. Start with a professional, slim Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
# This step is cached, so it only re-runs if requirements.txt changes, making builds faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the entire project code into the container
COPY . .

# 5. Expose the port the API will run on
EXPOSE 8000

# 6. The command to run the application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
