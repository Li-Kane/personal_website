FROM ros:jazzy-ros-base

# Install kdFlex
COPY libs/kdflex-*-Linux.deb /tmp/
COPY libs/evaluation.license /opt/kdflex/evaluation.license
COPY libs/requirements.txt /tmp/requirements.txt
RUN apt update && \
    apt install -y /tmp/kdflex-*-Linux.deb && \
    # Remove conflicting Debian Python packages that pip needs to upgrade
    apt remove -y \
        python3-typing-extensions \
        python3-scipy \
        python3-more-itertools \
        python3-lark \
    && \
    pip install --no-cache-dir --upgrade-strategy only-if-needed --break-system-packages -r /tmp/requirements.txt && \
    # Reinstall ROS2 packages that were removed as dependencies
    apt install -y --no-install-recommends \
        ros-jazzy-ament-cmake \
        ros-jazzy-ament-cmake-python \
        ros-jazzy-rosidl-default-generators \
        ros-jazzy-rclpy \
        ros-jazzy-launch \
        ros-jazzy-rosidl-parser \
        ros-jazzy-ament-lint-auto \
        ros-jazzy-ament-lint-common \
        ros-jazzy-ros2cli \
        ros-jazzy-ros2cli-common-extensions \
    && \
    # Clean up EVERYTHING in same layer
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
EXPOSE 3247
EXPOSE 8080

# copy the install files
COPY ./install /server/install
COPY ./launch /server/launch

# source ROS2 and the workspace
WORKDIR /server
CMD ["/bin/bash", "-c", "source /opt/ros/jazzy/setup.bash && source ./install/setup.bash && cd launch && ros2 launch server_sim_launch.yaml"]