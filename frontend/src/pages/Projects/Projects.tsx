import { useState } from 'react'
import './Projects.css'

// list of project components
import PersonalWebsite from './List/PersonalWebsite'

// Define project categories
export type Category = 'web-development' | 'robotics' | 'simulations' | 'other'

// Define project data structure
export interface Project {
  id: string
  name: string
  component: React.ComponentType
  categories: Category[]
}

// Category metadata
interface CategoryInfo {
  id: Category | 'all'
  name: string
}

const categoryList: CategoryInfo[] = [
  { id: 'all', name: 'All' },
  { id: 'web-development', name: 'Web Development' },
  { id: 'robotics', name: 'Robotics' },
  { id: 'simulations', name: 'Simulations' },
  { id: 'other', name: 'Other' },
]

// Add your projects here with their categories
const projects: Project[] = [
  { 
    id: 'personal-website', 
    name: 'Personal Website', 
    component: PersonalWebsite,
    categories: ['web-development', 'robotics', 'simulations']
  },
]

function Projects() {
  const [selectedCategory, setSelectedCategory] = useState<Category | 'all'>('all')
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [tocExpanded, setTocExpanded] = useState(false)

  // Filter projects based on category and specific project selection
  const filteredByCategory = selectedCategory === 'all'
    ? projects
    : projects.filter(p => p.categories.includes(selectedCategory))

  const displayedProjects = selectedProject
    ? filteredByCategory.filter(p => p.id === selectedProject)
    : filteredByCategory

  // Get projects for the selected category
  const categoryProjects = selectedCategory === 'all'
    ? projects
    : projects.filter(p => p.categories.includes(selectedCategory))

  const handleCategoryClick = (categoryId: Category | 'all') => {
    setSelectedCategory(categoryId)
    setSelectedProject(null) // Reset project selection when changing category
  }

  const handleProjectClick = (projectId: string) => {
    setSelectedProject(selectedProject === projectId ? null : projectId)
  }

  return (
    <div className="projects-container">
      <button 
        className="toc-toggle"
        onClick={() => setTocExpanded(!tocExpanded)}
      >
        Projects {tocExpanded ? '▲' : '▼'}
      </button>
      <div className={`table-of-contents ${tocExpanded ? 'toc-expanded' : 'toc-collapsed'}`}>
        <h2 className="toc-desktop-title">Projects</h2>
        
        {categoryList.map(category => (
          <div key={category.id} className="category-section">
            <div
              className={`category-header ${selectedCategory === category.id ? 'active' : ''}`}
              onClick={() => handleCategoryClick(category.id)}
            >
              {category.name}
            </div>
            
            {selectedCategory === category.id && category.id !== 'all' && (
              <ul className="project-list">
                {categoryProjects.map(project => (
                  <li
                    key={project.id}
                    className={selectedProject === project.id ? 'active' : ''}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleProjectClick(project.id)
                    }}
                  >
                    {project.name}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
      <div className="projects-list">
        {displayedProjects.map(project => {
          const Component = project.component
          return (
            <div key={project.id} className="project-item">
              <Component />
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Projects
