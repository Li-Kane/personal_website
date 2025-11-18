import './Project.css'

function PersonalWebsite() {
  return (
    <div className="project">
      <h2 className="project-title">Personal Website</h2>
      <div className="project-content">
        <p className="project-description">
          A modern personal portfolio website built with React and TypeScript.
        </p>
        
        <div className="project-details">
          <h3>Technologies Used</h3>
          <ul>
            <li>React</li>
            <li>TypeScript</li>
            <li>Vite</li>
            <li>CSS</li>
          </ul>
          
          <h3>Key Features</h3>
          <ul>
            <li>Responsive design</li>
            <li>Project showcase</li>
            <li>Dynamic routing</li>
          </ul>
        </div>

        <div className="project-links">
          <a href="https://github.com/Li-Kane/personal_website" target="_blank" rel="noopener noreferrer">GitHub</a>
        </div>
      </div>
    </div>
  )
}

export default PersonalWebsite