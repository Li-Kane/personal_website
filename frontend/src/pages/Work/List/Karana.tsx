import styles from './Project.module.css'

function Karana() {
  return (
    <div className={styles.project}>
        <div className={styles['title-container']}>
            <h2 className={styles['project-title']}>Karana Dynamics Internship</h2>
            <a target="_blank" href="https://www.karanadyn.com/">
                <img className={styles['tech-icon']} title="Karana Dynamics" src="/icons/karana_logo.svg" alt="Karana Dynamics Link" />
            </a>
        </div>

        <div className={styles['project-content']}>
            <img className={styles['project-image']} src="/work/karana_dynamics.png" alt="Karana Dynamics Internship Screenshot" />

            <h3 className={styles['project-section']}>Overview</h3>
            <p className={styles['project-date']}>July 2025 - September 2025</p>
            <p className={styles['project-description']}>
                
            </p>

            <h3 className={styles['project-section']}>Technologies Used</h3>
            <div className={styles['tech-list']}>
                <img title='kdFlex' className={styles['tech-icon']} src="/icons/karana_logo.svg" alt="kdFlex" />
                <img title='C++' className={styles['tech-icon']} src="/icons/cpp.svg" alt="C++" />
                <img title='Python' className={styles['tech-icon']} src="/icons/python.svg" alt="Python" />
                <img title='LangChain' className={styles['tech-icon']} src="/icons/langchain.svg" alt="LangChain" />
                <img title='Gymnasium' className={styles['tech-icon']} src="/icons/gymnasium.svg" alt="Gymnasium" />
            </div>

            <h3 className={styles['project-section']}>Chatbot</h3>
            <img className={styles['project-image']} title="Chatbot Screenshot" src="/work/karana_chatbot.png" alt="Chatbot Screenshot" />
            <p className={styles['project-description']}>
                After the team found NotebookLM to be a helpful tool for querying documentation internally,
                I was tasked to build a similar chatbot for Karana's public documentation. I did this by 
                implementing a retrieval-augmented generation (RAG) pipeline using LangChain. First, I processed the doxygen
                generated PDF files, stored them into text chunks, and embedded them into a local chroma database. Then, I set
                up a LangChain graph that would take in user queries, retrieve relevant document chunks, and generate the final 
                answer. After that, I setup a simple FastAPI server to host the chatbot and wrote a minimal frontend using 
                vanilla HTML/CSS/JS. I also setup a human-labelled responses dataset to evaluate the chatbot, here are some 
                of the stats (using a strict correctness criteria):
                <br />
                Correctness: 0.583
                Groundedness: 0.947
                Latency: 15.75s
                Cost-per-query: $0.0149
            </p>

            <h3 className={styles['project-section']}>Stress Testing</h3>
            <img className={styles['project-image']} title="Stress Testing Screenshot" src="/work/atrv.png" alt="Stress Testing Screenshot" />
            <p className={styles['project-description']}>
                Another task I worked on was stress testing kdFlex's simulator values by implementing a variety of 
                scenarios and validating values such as  acceleration, friction, contact forces, and energy consumption.
                The image above shows one scenario I implemented of creating a gymnasium environment where an ATRV-Jr robot
                drives towards a target. 
            </p>

            <h3 className={styles['project-section']}>Widgets</h3>
            <p className={styles['project-description']}>
                Lastly, I designed the framework for an efficient C++ browser-based widget library. While there are a
                variety of python and C++ libraries already out there, it was imperative for kdFlex to create a minimal
                and efficient system that was compatible with the current rendering library. Using websockets and custom
                DOM based event listeners, I developed an easily extendable widget and message template for future use. </p>
        </div>
    </div>
  )
}

export default Karana