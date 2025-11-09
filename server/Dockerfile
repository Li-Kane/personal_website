FROM osrf/ros:kilted-desktop

# Install kdFlex
COPY libs/kdflex-*-Linux.deb /tmp/
COPY libs/evaluation.license /opt/kdflex/evaluation.license
RUN apt update && \
    apt install -y /tmp/kdflex-*-Linux.deb && \
    # Remove conflicting Debian Python packages that pip needs to upgrade
    apt remove -y \
        python3-typing-extensions \
        python3-scipy \
        python3-more-itertools \
        python3-lark \
    && \
    pip install --upgrade-strategy only-if-needed --break-system-packages -r /usr/share/Karana/requirements.txt && \
    # Reinstall ROS2 packages that were removed as dependencies
    apt install -y --no-install-recommends \
        ros-kilted-ament-cmake \
        ros-kilted-ament-cmake-python \
        ros-kilted-rosidl-default-generators \
        ros-kilted-rclpy \
        ros-kilted-launch \
        ros-kilted-rosidl-parser \
        ros-kilted-ament-lint-auto \
        ros-kilted-ament-lint-common \
        ros-kilted-ros2cli \
        ros-kilted-ros2cli-common-extensions \
    && \
    rm -rf /tmp/*.deb

# Set up kdFlex license environment variable
ENV KARANA_LICENSE_FILE=/opt/kdflex/evaluation.license

# Source ROS2 environment automatically
RUN echo "source /opt/ros/kilted/setup.bash" >> ~/.bashrc

WORKDIR /server

VOLUME [ "/server" ]

EXPOSE 3247
EXPOSE 8080
CMD ["/bin/bash", "-c", "cd /server && colcon build && source ./install/setup.bash && cd launch && ros2 launch server_sim_launch.yaml && exec /bin/bash"]
# CMD ["/bin/bash", "-c", "exec /bin/bash"]