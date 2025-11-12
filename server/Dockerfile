FROM ros:jazzy-ros-base

# Install kdFlex in a separate layer
COPY docker_libs/evaluation.license /opt/kdflex/evaluation.license
COPY docker_libs/KaranaConfig.cmake /tmp/KaranaConfig.cmake
COPY docker_libs/kdflex-*-Linux.deb /tmp/
RUN apt update && \
    apt install -y /tmp/kdflex-*-Linux.deb && \
    mv /tmp/KaranaConfig.cmake /usr/share/Karana/cmake/KaranaConfig.cmake && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*.deb

# Install Python dependencies in a separate layer
COPY docker_libs/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade-strategy only-if-needed --break-system-packages -r /tmp/requirements.txt && \
    rm -rf /tmp/*.txt \
        /root/.cache \
        /root/.local/share/pip \
        /usr/share/doc \
        /usr/share/man

# Set up kdFlex license environment variable
ENV KARANA_LICENSE_FILE=/opt/kdflex/evaluation.license
EXPOSE 3247 8080

# source ROS2 and the workspace
WORKDIR /server
VOLUME [ "/server" ]
CMD ["/bin/bash", "-c", "cd /server && exec /bin/bash"]