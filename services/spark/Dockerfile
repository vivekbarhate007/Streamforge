FROM python:3.11-slim

# Install Java 17 (required for Spark 3.4.1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    && wget -qO- https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-aarch64_bin.tar.gz | tar -xz -C /opt \
    && mv /opt/jdk-17.0.2 /opt/java17 \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/opt/java17
ENV PATH=$PATH:$JAVA_HOME/bin

# Install Spark and Python dependencies
RUN pip install --no-cache-dir \
    pyspark==3.4.1 \
    kafka-python==2.0.2 \
    psycopg2-binary==2.9.9

# Set Spark environment
ENV SPARK_HOME=/usr/local/lib/python3.11/site-packages/pyspark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV PYTHONPATH=$SPARK_HOME/python:$PYTHONPATH

# Create directories
RUN mkdir -p /app/jobs /tmp/spark-checkpoints

WORKDIR /app

COPY jobs/ /app/jobs/

