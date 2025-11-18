import './Profile.css'

function Profile() {

  return (
    <div className='profile-container'>
      <div className='navbar-spacer'></div>
      <div className='profile-content'>
        <div className='img-container'>
          <img className='profile-img' src="/profile.jpeg" alt="Profile" />
        </div>
        <div className='profile-text'>
          <h1 className='title-text'>Hey, I'm Kane</h1>
          <p className='profile-description'>I'm a motivated 4th year Computer Science Major with a Minor in math. 
            My expertise lies in web development, robotics algorithms, and simulators.
          </p>
          <div className='icons-container'>
            <a target='none' href='https://github.com/Li-Kane'>
              <img title='github' className='icon' src="/github.svg" alt="GitHub" />
            </a>
            <a target='none' href='https://www.linkedin.com/in/kane-li-b5153125b/'>
              <img title='LinkedIn' className='icon' src="/linkedin.svg" alt="LinkedIn" />
            </a>
            <a target='none' href='https://drive.google.com/file/d/1hpx4HIEDBf-lfs0S6q7CLm8HfJrwDm5M/view?usp=sharing'>
              <img title='resume' className='icon' src="/resume.svg" alt="Resume" />
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
