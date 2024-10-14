FROM python:3.11-slim-buster
# Set the working directory in the container to /app
WORKDIR /app

# Add only the requirements file, so docker can create a layer with them
ADD requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/markr/

COPY ./src /app/src
ADD ./run_markr_server.sh /app/
ADD ./alembic.ini /app/

#note that this does not expose the port, it is just for documentation
EXPOSE 8082

CMD /app/run_markr_server.sh

