import styles from './Project.module.css'

function TritonRobotics() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Triton Robotics</h2>
            <a target="_blank" href="https://tritonrobotics.org/">
                <img className={styles['tech-icon']} title="Triton Robotics" src="/icons/TR.svg" alt="Triton Robotics Logo" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/work/triton_robotics.png" alt="Triton Robotics Screenshot" />

            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>September 2023 - Present</p>
            <p className={styles['project-description']}>
                From my second year of university, I have been a member of Triton Robotics, a robotics club at UCSD that 
                competes in Robomaster North America. First, I was a member and then a lead of the Autonomy subteam,
                where I was responsible for writing software to make a fully autonomous robot that could navigate the arena
                and shoot enemy targets. Currently, I am the head of software, helping ensure all code is clean and organized
                for Embedded and Autonomy.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='ROS' className={styles['tech-icon']} src="/icons/ROS.svg" alt="ROS" />
                <img title='C++' className={styles['tech-icon']} src="/icons/cpp.svg" alt="C++" />
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
                <img title='OpenCV' className={styles['tech-icon']} src="/icons/opencv.svg" alt="OpenCV" />
            </div>

            <h3 className={styles['project-section']}>UART Comms</h3>
            <p className={styles['project-description']}>
                One my first tasks was to setup a reliable UART communication protocol between the Orin Jetson Nano that runs
                autonomy code and the STM32 microcontroller that manages embedded code. Using Linux's termios library, I was able
                to establish a 115200 baud connection that could reliably send and receive packets. 
            </p>

            <h3 className={styles['project-section']}>Aim and Shoot</h3>
            <img className={styles['project-image']} title="Aim and Shoot Screenshot" src="/work/aimshoot.gif" alt="Aim and Shoot Screenshot" />
            <p className={styles['project-description']}>
                As a relatively new team, my goal as lead was to implement a computer vision pipeline that could detect enemy
                targets, aim the turret at them, and shoot. First we used CUDA and YOLOv5 to detect armor panels, and then OpenCV 
                to determine the color, type, distance, and angle of the target. After that the information was processed using a simple
                Aiming controller that would compute the necessary turret angles to hit the target. An outside state manager would determine 
                when to shoot. There were many challenges along the way, such as inference latency, communication delay, UART packet loss, and 
                mechanical inaccuracies. But in the end, we were able to get a working system by competition time!
            </p>
        </div>
    </div>
  )
}

export default TritonRobotics