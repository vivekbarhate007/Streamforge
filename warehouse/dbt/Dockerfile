FROM python:3.11-slim

WORKDIR /dbt

# Install dbt and dependencies
RUN pip install --no-cache-dir \
    dbt-postgres==1.7.0 \
    great-expectations==0.18.8 \
    psycopg2-binary==2.9.9

COPY . /dbt

CMD ["tail", "-f", "/dev/null"]

