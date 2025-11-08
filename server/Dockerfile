FROM osrf/ros:kilted-desktop

# Install kdFlex
COPY libs/ /tmp/libs/
RUN apt update && \
    apt install -y /tmp/libs/kdflex-*-Linux.deb python3-venv && \
    python3 -m venv --system-site-packages /opt/kdflex_venv && \
    /opt/kdflex_venv/bin/pip install --upgrade -r /usr/share/Karana/requirements.txt && \
    cp /tmp/libs/evaluation.license /opt/kdflex_venv/ && \
    rm -rf /tmp/libs

# Set up kdFlex license environment variable
ENV KARANA_LICENSE_FILE=/opt/kdflex_venv/evaluation.license

WORKDIR /src

VOLUME [ "/src" ]

EXPOSE 3247

CMD ["/bin/bash", "-c", "source /opt/kdflex_venv/bin/activate && exec /bin/bash"]