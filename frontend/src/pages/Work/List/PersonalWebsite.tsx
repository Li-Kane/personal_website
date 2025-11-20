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
            <p className={styles['project-description']}>
                A personal portfolio demonstrating my experience in robotics, simulators,
                and web development. On my AWS EC2 server, I run a <a target="_blank" href="https://www.karanadyn.com/">kdFlex</a> simulation
                where a Spot robot autonomously navigates to a target. It
                communicates with my React frontend through websockets to have Spot follow
                wherever the user's mouse is.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='kdFlex' className={styles['tech-icon']} src="/icons/karana_logo.svg" alt="kdFlex" />
                <img title='AWS' className={styles['tech-icon']} src="/icons/aws.svg" alt="AWS" />
                <img title='React' className={styles['tech-icon']} src="/icons/react.svg" alt="React" />
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
            </div>

            <h3 className={styles['project-section']}>Features</h3>

            <h3 className={styles['project-section']}>Challenges</h3>

            <h3 className={styles['project-section']}>Lessons Learned</h3>
        </div>
    </div>
  )
}

export default PersonalWebsite