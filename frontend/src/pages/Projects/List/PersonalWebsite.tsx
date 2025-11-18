import './Project.css'

function PersonalWebsite() {
  return (
    <div className="project">
        <div className="title-container">
            <h2 className="project-title">Personal Website</h2>
            <a target="_blank" href="https://github.com/Li-Kane/personal_website">
                <img className="icon" title="github" src="/profile/github.svg" alt="GitHub Link" />
            </a>
        </div>
        <div className="project-content">
            <p className="project-description">
                A personal portfolio demonstrating my experience in robotics, simulators,
                and web development. On my AWS EC2 server, I run a <a target="_blank" href="https://www.karanadyn.com/">kdFlex</a> simulation
                where a Spot robot autonomously navigates to a target. It 
                communicates with my React frontend through websockets to have Spot follow 
                wherever the user's mouse is.
            </p>
            
            <div className="project-details">
                <h3>Technologies Used</h3>
                <div className="tech-list">
                    <span>kdFlex</span>
                    <span>AWS</span>
                    <span>React</span>
                    <span>Python</span>
                </div>

                <h3>Features</h3>

                <h3>Challenges</h3>

                <h3>Lessons Learned</h3>
            </div>
        </div>
    </div>
  )
}

export default PersonalWebsite