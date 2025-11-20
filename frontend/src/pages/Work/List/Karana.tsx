import styles from './Project.module.css'

function Karana() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Karana Dynamics Internship</h2>
            <a target="_blank" href="https://www.karanadyn.com/">
                <img className={styles['tech-icon']} title="Karana Dynamics" src="/icons/karana_logo.svg" alt="Karana Dynamics Link" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/work/karana_dynamics.png" alt="Karana Dynamics Internship Screenshot" />

            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>July 2025 - September 2025</p>
            <p className={styles['project-description']}>
                
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='kdFlex' className={styles['tech-icon']} src="/icons/karana_logo.svg" alt="kdFlex" />
                <img title='C++' className={styles['tech-icon']} src="/icons/cpp.svg" alt="C++" />
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
                <img title='LangChain' className={styles['tech-icon']} src="/icons/langchain.svg" alt="LangChain" />
                <img title='Gymnasium' className={styles['tech-icon']} src="/icons/gymnasium.svg" alt="Gymnasium" />
            </div>

            <h3 className={styles['project-section']}>Chatbot</h3>
            <p className={styles['project-description']}>

            </p>

            <h3 className={styles['project-section']}>Reinforcement Learning</h3>
            <p className={styles['project-description']}>
                
            </p>

            <h3 className={styles['project-section']}>Widgets</h3>
            <p className={styles['project-description']}>
            </p>
        </div>
    </div>
  )
}

export default Karana