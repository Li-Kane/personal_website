import styles from './Project.module.css'

function PersonalWebsite() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Personal Website</h2>
            <a target="_blank" href="https://github.com/Li-Kane/personal_website">
                <img className={styles['tech-icon']} title="github" src="/icons/github.svg" alt="GitHub Link" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/work/personal_website.png" alt="Personal Website Screenshot" />

            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>September 2025 - Nov 2025</p>
            <p className={styles['project-description']}>
                A personal portfolio demonstrating my experience in robotics, simulators,
                and web development. On my AWS EC2 server, I run a <a target="_blank" href="https://www.karanadyn.com/">kdFlex</a> simulation
                in a docker container where a Spot robot autonomously navigates to a target. It
                communicates with my React frontend through websockets and an nginx proxy to have Spot follow
                wherever the user's mouse is.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='kdFlex' className={styles['tech-icon']} src="/icons/karana_logo.svg" alt="kdFlex" />
                <img title='AWS' className={styles['tech-icon']} src="/icons/aws.svg" alt="AWS" />
                <img title='React' className={styles['tech-icon']} src="/icons/react.svg" alt="React" />
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
                <img title='Docker' className={styles['tech-icon']} src="/icons/docker.svg" alt="Docker" />
                <img title='Nginx' className={styles['tech-icon']} src="/icons/nginx.svg" alt="Nginx" />
                <img title='TypeScript' className={styles['tech-icon']} src="/icons/typescript.svg" alt="TypeScript" />
            </div>

            <h3 className={styles['project-section']}>The Simulation</h3>
            <p className={styles['project-description']}>
                To run the simulation, I am using a Spot URDF model from <a href="https://github.com/bdaiinstitute/spot_description">this repository</a>.
                At the top level, I have a simple proportional planner that takes in target coordinates as well as the Spot coordinates and computes the desired forward 
                and angular velocities. Then, I feed these desired velocities into a tuned <a href="https://isaac-sim.github.io/IsaacLab/main/source/overview/environments.html">IsaacLab policy</a>
                which outputs the necessary joint qpos to achieve these velocities. Finally, I apply a PD controller on the joints to have Spot move.
            </p>
            <p className={styles['project-description']}>
                One major challenge I faced was optimizing the simulation performance, since to cut costs I limited myself to a AWS t3 small instance with only 2 vCPUs and 2GB of RAM.
                After extensive profiling, I addressed this by using a euler integrator with a larger time step, lowering the contact fidelity, decreasing the 
                render resolution and frame rate, decreasing collision mesh complexity, using visual meshes for the body, and offloading as much computation as possible from
                the main simulation thread. In the end, on the simulation thread less than 2% of the runtime was spent on tasks other than stepping the simulation.
            </p>
            <p className={styles['project-description']}>
                Average step: 18.157ms (100%)
                Policy Inference: 0.101ms (0.6%)
                Simulation step: 17.909ms (98.6%)
                Python Operations: 0.146ms (0.8%)
            </p>

            <h3 className={styles['project-section']}>The Frontend</h3>
            <p className={styles['project-description']}>
                The frontend is built using React and communicates with the backend simulation through websockets.
                Every mouse movement is captured and send to the backend, which projects them onto the ground plane.
                Aside from that, the frontend itself is statically hosted on Github pages with the custom domain
                kaneliportfolio.com.
            </p>

            <h3 className={styles['project-section']}>AWS and Networking</h3>
            <p className={styles['project-description']}>
                To run the simulation 24/7, I set up an AWS EC2 t3 small instance running Ubuntu. This required also 
                setting up a virtual private cloud (VPC), security groups, and security policies. Because kdFlex came
                built-in with a rendering websocket server that could only be hosted locally, I setup an nginx reverse proxy
                to forward public traffic to the appropriate internal ports, also allowing SSL certification. Finally, the
                server itself uses a ROS2 docker container, allowing the server to be easily deployed and scaled 
                (though I keep it to a single instance for cost reasons). 
            </p>
        </div>
    </div>
  )
}

export default PersonalWebsite