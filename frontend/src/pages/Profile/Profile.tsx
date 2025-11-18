import './Profile.css'

function Profile() {

  return (
    <div className='profile-container'>
      <div className='profile-content'>
        <div className='img-container'>
          <img className='profile-img' src="/profile/profile.jpeg" alt="Profile" />
        </div>
        <div className='profile-text'>
          <h1 className='title-text'>Hey, I'm Kane</h1>
          <p className='profile-description'>I'm a motivated 4th year Computer Science Major at UC San Diego with a Minor in math. 
            My expertise lies in web development, robotics, and simulators. Outside of academics,
            I enjoy playing Brawl Stars and Taiko drumming.
          </p>
          <div className='icons-container'>
            <a target='none' href='https://github.com/Li-Kane'>
              <img title='github' className='icon' src="/profile/github.svg" alt="GitHub" />
            </a>
            <a target='none' href='https://www.linkedin.com/in/kane-li-b5153125b/'>
              <img title='LinkedIn' className='icon' src="/profile/linkedin.svg" alt="LinkedIn" />
            </a>
            <a target='none' href='https://drive.google.com/file/d/1hpx4HIEDBf-lfs0S6q7CLm8HfJrwDm5M/view?usp=sharing'>
              <img title='resume' className='icon' src="/profile/resume.svg" alt="Resume" />
            </a>
            <a target='none' href='mailto:kal036@ucsd.edu'>
              <img title='email' className='icon' src="/profile/email.svg" alt="Email" />
            </a>
          </div>
        </div>
      </div>
      <div className='read-more-container'>
        <img className='icon' src="/profile/down-arrow.svg" alt="Down Arrow" />
      </div>
      <div className='technical-content'>
        <h2 className='section-title'>Technical Skills</h2>
        <div className='skills-boxes'>
          <div className='skill-box'>
            <h3>Web Development</h3>
            <img className='skill-img' src="/profile/webdev.png" alt="Web Development" />
            <p className='skill-description'>
              Having built multiple websites and a mobile app, I have fullstack
              experience in both web and mobile applications.
            </p>
          </div>
          <div className='skill-box'>
            <h3>Robotics</h3>
            <img className='skill-img' src="/profile/robotics.png" alt="Robotics" />
            <p className='skill-description'>
              As an executive in Triton Robotics, I wrote software
              for a real-world robot that can
              autonomously navigate and shoot targets.
            </p>
          </div>
          <div className='skill-box'>
            <h3>Simulators</h3>
            <img className='skill-img' src="/profile/simulator.png" alt="Simulators" />
            <p className='skill-description'>
              Through work in a lab and startup I have implemented
              and tested scenarios for simulators such as
              Maniskill, kdFlex, and IsaacSim.
            </p>
          </div>
        </div>
      </div>
      <div className='personal-content'>
        <h2 className='section-title'>Personal Interests</h2>
        <img className='personal-img' src="/profile/taiko.png" alt="Taiko" />
        <p className='personal-description'>
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
