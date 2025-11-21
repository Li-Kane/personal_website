import styles from './Project.module.css'

function Tutor() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Tutoring</h2>
        </div>

        <div className={styles['project-content']}>
            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>March 2024 - December 2024</p>
            <p className={styles['project-description']}>
                Over the course of 3 quarters at UCSD, I tutored 3 classes in the computer science
                department. They were all theory/algorithm based, consisting of CSE 21 (Mathematics for Algorithms and Systems)
                and CSE 101 (Design and Analysis of Algorithms). As a tutor, I never missed a grading deadline, and 
                had a 100% recommendation rate from over 6 students. 
            </p>
        </div>
    </div>
  )
}

export default Tutor