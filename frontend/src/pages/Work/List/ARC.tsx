// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

import styles from './Project.module.css'

function ARC() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Advanced Robotics and Controls Lab</h2>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/profile/simulator.png" alt="Advanced Robotics and Controls Lab Screenshot" />

            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>December 2024 - July 2025</p>
            <p className={styles['project-description']}>
                As a research assistant, I worked under Yuheng Zhi, a PhD student to help test his differential
                collision detection library <a href="https://github.com/ucsdarclab/diffco.git">DiffCo</a>. By 
                replacing the default collision detection module in various libraries such as Maniskill with DiffCo,
                we were able to evaluate the performance increases that the library provided.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
                <img title='Maniskill' className={styles['tech-icon']} src="/icons/maniskill.svg" alt="Maniskill" />
            </div>
        </div>
    </div>
  )
}

export default ARC