import styles from './Project.module.css'

function Dougu() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Dougu</h2>
            <a target="_blank" href="https://github.com/Asayake-Taiko/Dougu">
                <img className={styles['tech-icon']} title="github" src="/icons/github.svg" alt="GitHub Link" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/work/dougu.png" alt="Dougu Screenshot" />
            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>March 2024 - Present</p>
            <p className={styles['project-description']}>
                Dougu is a mobile app born out of a need to more quickly and reliably organize equipment within Asayake Taiko (Japanese Drumming Organization).
                To do so, it seeks to utilize a drag and drop functionality with offline caching to minimize ease of equipment transfer, compared to the old manual
                system of typing assignments into a google sheet. While it has been put on hold for the time being, I plan to continue development this winter,
                cleaning up the codebase and deploying it before summer 2026.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='AWS' className={styles['tech-icon']} src="/icons/aws.svg" alt="AWS" />
                <img title='React' className={styles['tech-icon']} src="/icons/react.svg" alt="React" />
                <img title='Amplify' className={styles['tech-icon']} src="/icons/amplify.svg" alt="Amplify" />
                <img title='TypeScript' className={styles['tech-icon']} src="/icons/typescript.svg" alt="TypeScript" />
            </div>
        </div>
    </div>
  )
}

export default Dougu