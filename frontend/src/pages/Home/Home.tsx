import styles from './Home.module.css'

function Home() {
  return (
    <div>
      <div className={styles['overlay-text']}>
        <h1 className={styles['title-text']}>Kane's Website</h1>
        <p className={styles['subtitle-text']}>Aspiring Roboticist and Software Engineer</p>
      </div>
      <a className={styles.logo} href='https://karanadyn.com' target='_blank'>
        <img src="/icons/karana_logo.svg" alt="Logo" />
      </a>
    </div>
  )
}

export default Home
