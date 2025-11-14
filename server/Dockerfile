FROM ubuntu:24.04

# Install kdFlex
COPY docker_files/kdflex-*-Linux.deb /tmp/
COPY docker_files/evaluation.license /opt/kdflex/evaluation.license
COPY docker_files/requirements.txt /tmp/requirements.txt
RUN apt update && \
    apt install -y /tmp/kdflex-*-Linux.deb && \
    pip install --no-cache-dir --upgrade-strategy only-if-needed --break-system-packages -r /tmp/requirements.txt && \
    # Clean up everything
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
        /tmp/*.deb \
        /tmp/*.txt \
        /root/.cache \
        /root/.local/share/pip \
        /usr/share/doc \
        /usr/share/man

# Set up kdFlex license environment variable
ENV KARANA_LICENSE_FILE=/opt/kdflex/evaluation.license
EXPOSE 3247 8080

# source ROS2 and the workspace
WORKDIR /server
COPY src/ /server/src/
COPY assets/ /server/assets/ 
CMD ["/bin/bash", "-c", "python3 src/server.py"]