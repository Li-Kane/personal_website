import './Home.css'

function Home() {
  return (
    <div>
      <div className="overlay-text">
        <div className="title-container">
          <h1 className="title-text">Kane's Website</h1>
          <p className="subtitle-text">Aspiring Roboticist and Software Engineer</p>
        </div>
      </div>
      <a className="logo" href='https://karanadyn.com' target='_blank'>
        <img src="/karana_logo.svg" alt="Logo" />
      </a>
    </div>
  )
}

export default Home
