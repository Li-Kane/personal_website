// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

import styles from './Project.module.css'

function Cmnist() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Cmnist</h2>
            <a target="_blank" href="https://github.com/Li-Kane/cmnist-website">
                <img className={styles['tech-icon']} title="github" src="/icons/github.svg" alt="GitHub Link" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/profile/webdev.png" alt="Cmnist Screenshot" />
            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>July 2023 - October 2023</p>
            <p className={styles['project-description']}>
                Cmnist is my first web development project that also displayed my interest in machine learning.
                Having taken a kaggle computer vision course, I sought to create a website that could classify 
                handwritten chinese numerals from the CMNIST dataset. After training the model in a notebook, the
                weights are exported and loaded into TensorflowJS, allowing the entire svelte website to be hosted 
                statically on vercel.
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='Svelte' className={styles['tech-icon']} src="/icons/svelte.svg" alt="Svelte" />
                <img title='Tensorflow' className={styles['tech-icon']} src="/icons/tensorflow.svg" alt="Tensorflow" />
                <img title='Vercel' className={styles['tech-icon']} src="/icons/vercel.svg" alt="Vercel" />
            </div>
        </div>
    </div>
  )
}

export default Cmnist