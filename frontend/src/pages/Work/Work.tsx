import { useState, useEffect, useRef } from 'react'
import styles from './Work.module.css'

// list of work components
import PersonalWebsite from './List/PersonalWebsite'
import Karana from './List/Karana'
import TritonRobotics from './List/TR'
import ARC from './List/ARC'
import Dougu from './List/Dougu'
import Tutor from './List/Tutor'
import Cmnist from './List/Cmnist'

// Define work categories
export type Category = 'web-development' | 'robotics' | 'simulations' | 'other'

// Define work data structure
export interface Work {
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

// Add your work here with their categories
const work: Work[] = [
  {
    id: 'personal-website',
    name: 'Personal Website',
    component: PersonalWebsite,
    categories: ['web-development', 'robotics', 'simulations']
  },
  {
    id: 'karana-internship',
    name: 'Karana Dynamics Internship',
    component: Karana,
    categories: ['simulations', 'web-development']
  },
  {
    id: 'triton-robotics',
    name: 'Triton Robotics',
    component: TritonRobotics,
    categories: ['robotics', 'simulations']
  },
  {
    id: 'arc-lab',
    name: 'Advanced Robotics and Controls Lab',
    component: ARC,
    categories: ['simulations', 'robotics']
  },
  {
    id: 'dougu',
    name: 'Dougu',
    component: Dougu,
    categories: ['web-development', 'other']
  }, 
  {
    id: 'tutoring',
    name: 'Tutoring',
    component: Tutor,
    categories: ['other']
  },
  {
    id: 'cmnist',
    name: 'Cmnist',
    component: Cmnist,
    categories: ['web-development', 'other']
  }
]

function Work() {
  const [selectedCategory, setSelectedCategory] = useState<Category | 'all'>('all')
  const [selectedWork, setSelectedWork] = useState<string | null>(null)
  const [activeWorkId, setActiveWorkId] = useState<string | null>(null)
  const [tocExpanded, setTocExpanded] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  // Filter work based on category and specific work selection
  const filteredByCategory = selectedCategory === 'all'
    ? work
    : work.filter(p => p.categories.includes(selectedCategory))

  const displayedWork = selectedWork
    ? filteredByCategory.filter(p => p.id === selectedWork)
    : filteredByCategory

  // Get work for the selected category
  const categoryWork = selectedCategory === 'all'
    ? work
    : work.filter(p => p.categories.includes(selectedCategory))

  const handleCategoryClick = (categoryId: Category | 'all') => {
    setSelectedCategory(categoryId)
    setSelectedWork(null) // Reset work selection when changing category
  }

  const handleWorkClick = (workId: string) => {
    setSelectedWork(selectedWork === workId ? null : workId)
  }

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveWorkId(entry.target.id)
          }
        })
      },
      {
        root: contentRef.current,
        rootMargin: '-10% 0px -80% 0px',
        threshold: 0
      }
    )

    const workItems = contentRef.current?.querySelectorAll(`.${styles['work-item']}`)
    workItems?.forEach((item) => observer.observe(item))

    return () => observer.disconnect()
  }, [displayedWork, selectedCategory])

  return (
    <div className={styles['work-container']}>
      <button
        className={styles['toc-toggle']}
        onClick={() => setTocExpanded(!tocExpanded)}
      >
        Work {tocExpanded ? '▲' : '▼'}
      </button>
      <div className={`${styles['table-of-contents']} ${tocExpanded ? styles['toc-expanded'] : styles['toc-collapsed']}`}>
        <h2 className={styles['toc-desktop-title']}>Work</h2>

        {categoryList.map(category => (
          <div key={category.id} className={styles['category-section']}>
            <button
              className={`${styles['category-header']} ${selectedCategory === category.id ? styles.active : ''}`}
              onClick={() => handleCategoryClick(category.id)}
              aria-pressed={selectedCategory === category.id}
            >
              {category.name}
            </button>

            {selectedCategory === category.id && (
              <div className={styles['work-list']} role="group" aria-label={`${category.name} work`}>
                {categoryWork.map(workItem => (
                  <button
                    key={workItem.id}
                    className={`${styles['work-item-button']} ${(selectedWork === workItem.id || (!selectedWork && activeWorkId === workItem.id)) ? styles.active : ''}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleWorkClick(workItem.id)
                    }}
                    aria-pressed={selectedWork === workItem.id}
                  >
                    {workItem.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className={styles['work-content']} ref={contentRef}>
        {displayedWork.map(workItem => {
          const Component = workItem.component
          return (
            <div key={workItem.id} id={workItem.id} className={styles['work-item']}>
              <Component />
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Work
