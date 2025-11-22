// SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later

import { Link } from 'react-router'
import styles from './Profile.module.css'

function Profile() {

  return (
    <div className={styles['profile-container']}>
      <div className={styles['profile-content']}>
        <div className={styles['img-container']}>
          <img className={styles['profile-img']} src="/profile/profile.jpeg" alt="Profile" />
        </div>
        <div className={styles['profile-text']}>
          <h1 className={styles['title-text']}>Hey, I'm Kane</h1>
          <p className={styles['profile-description']}>I'm a motivated 4th year Computer Science Major at UC San Diego with a Minor in math.
            My expertise lies in web development, robotics, and simulators. Outside of academics,
            I enjoy playing Brawl Stars and Taiko drumming.
          </p>
          <div className={styles['icons-container']}>
            <a target='none' href='https://github.com/Li-Kane'>
              <img title='github' className={styles.icon} src="/icons/github.svg" alt="GitHub" />
            </a>
            <a target='none' href='https://www.linkedin.com/in/kane-li-b5153125b/'>
              <img title='LinkedIn' className={styles.icon} src="/icons/linkedin.svg" alt="LinkedIn" />
            </a>
            <a target='none' href='https://drive.google.com/file/d/1hpx4HIEDBf-lfs0S6q7CLm8HfJrwDm5M/view?usp=sharing'>
              <img title='resume' className={styles.icon} src="/icons/resume.svg" alt="Resume" />
            </a>
            <a target='none' href='mailto:kal036@ucsd.edu'>
              <img title='email' className={styles.icon} src="/icons/email.svg" alt="Email" />
            </a>
          </div>
        </div>
      </div>
      <div className={styles['read-more-container']}>
        <img className={styles.icon} src="/icons/down-arrow.svg" alt="Down Arrow" />
      </div>
      <div className={styles['technical-content']}>
        <h2 className={styles['section-title']}>Technical Skills</h2>
        <div className={styles['skills-boxes']}>
          <Link to="/work/web-development" className={styles['skill-box']}>
            <h3>Web Development</h3>
            <img className={styles['skill-img']} src="/profile/webdev.png" alt="Web Development" />
            <p className={styles['skill-description']}>
              Having built multiple websites and a mobile app, I have fullstack
              experience in both web and mobile applications.
            </p>
          </Link>
          <Link to="/work/robotics" className={styles['skill-box']}>
            <h3>Robotics</h3>
            <img className={styles['skill-img']} src="/profile/robotics.png" alt="Robotics" />
            <p className={styles['skill-description']}>
              As an executive in Triton Robotics, I wrote software
              for a real-world robot that can
              autonomously navigate and shoot targets.
            </p>
          </Link>
          <Link to="/work/simulators" className={styles['skill-box']}>
            <h3>Simulators</h3>
            <img className={styles['skill-img']} src="/profile/simulator.png" alt="Simulators" />
            <p className={styles['skill-description']}>
              Through work in a lab and startup I have implemented
              and tested scenarios for simulators such as
              Maniskill, kdFlex, and IsaacSim.
            </p>
          </Link>
        </div>
      </div>
      <div className={styles['personal-content']}>
        <h2 className={styles['section-title']}>Personal Interests</h2>
        <img className={styles['personal-img']} src="/profile/taiko.png" alt="Taiko" />
        <p className={styles['personal-description']}>
          For the past 4 years, I have been a member of the group Asayake Taiko,
          a Japanese drumming ensemble at UC San Diego. I have furthered my passion
          by becoming the current performance director of the club,
          leading the club and practices alongside the other directors.
        </p>
      </div>
    </div>
  )
}

export default Profile
