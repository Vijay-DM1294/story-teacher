# 📚 StoryTeacher AI

> **"Kids find science and maths boring but never get tired of stories."**  
> StoryTeacher AI bridges the engagement gap by teaching any school concept through an age-adapted interactive story quest, dynamically verifying comprehension with stateful quizzes, and generating actionable parent/teacher diagnostic reports.

---

## 🌟 Overview & Pedagogical Philosophy

Traditional STEM education often relies on abstract formulas and rote definitions that fail to engage young minds. **StoryTeacher AI** applies **Cognitive Narrative Scaffolding** and **Bloom's Revised Taxonomy** to transform abstract curricula into vivid, character-driven adventures:

```
[Academic Concept] ➔ [Age-Adapted Narrative Engine] ➔ [3-Act Story Quest] ➔ [Formative Comprehension Quiz] ➔ [Diagnostic Analytics]
```

---

## 🧠 1. Architecture & Age-Adaptation Engine

The core generative engine dynamically adjusts vocabulary, sentence cadence, metaphor complexity, and stakes based on the learner's developmental stage:

| Age Bracket | Developmental Tier | Reading Level | Narrative Archetypes | Metaphor & Language Style |
| :--- | :--- | :--- | :--- | :--- |
| **Ages 5–7** | **Early Explorers 🌱** | Lexile 200L–400L (Grades K–2) | Whimsical magical kitchens, enchanted gardens, playful animal sidekicks | Sensory and concrete imagery, short rhythmic sentences (6–11 words), cozy stakes, gentle personification (e.g. *chlorophyll chefs baking sweet sun-cookies*). |
| **Ages 8–10** | **Adventurers 🔍** | Lexile 500L–750L (Grades 3–5) | Detective mysteries, comic capers, schoolyard invention fairs | Action verbs, dynamic dialogue (10–18 words), gadgets, puzzles, and secret codes (e.g. *opposing magnetic repulsion balancing Earth's gravitational pull*). |
| **Ages 11–13** | **Trailblazers 🚀** | Lexile 800L–1050L (Grades 6–8) | Deep-space telemetry, survival expeditions, cyber research labs | Accurate technical terminology, mathematical relationships, cause-and-effect physical laws, high-stakes crises (e.g. *fractional proportions and oxygen ratios in spacecraft scrubbers*). |

---

## 🚀 2. Core Features & User Journey

### Step 1: Craft Adventure (Topic & World Setup)
- **Topic Input:** Free-text input for any curriculum topic (*e.g., Photosynthesis, Negative Numbers, Newton's Third Law, Mitosis, Black Holes*).
- **One-Click Quick Pills:** Instant selection of standard curriculum staples (*🌿 Photosynthesis, 🍎 Gravity, 🍕 Fractions, 🕳️ Black Holes, 💧 Water Cycle, ⚡ Circuits, 🏔️ Plate Tectonics, 🧬 DNA*).
- **Age Selector:** Dynamic 3-tier selector with contextual pedagogical cues.
- **Story Theme Selector:** 7 immersive story worlds (*Fantasy & Magic Quest, Space & Sci-Fi Voyage, Detective Mystery, Superhero League, Jungle Safari, Cyber Matrix, Time Travel*).
- **Protagonist Customization:** Add the child's name for deeply personalized immersion.

### Step 2: Story Adventure & Interactive Narration
- **Thematic Header & Mission Hook:** High-stakes 2–3 sentence dilemma explaining why the hero needs the concept to solve the problem.
- **The Main Story:** 300–400 words crafted to adhere to the Lexile tier, with core scientific keywords highlighted in **bold**.
- **Interactive Audio Narration:**
  - **In-Browser Web Speech Synthesizer:** Real-time client-side read-aloud engine with Play, Pause, and Stop controls (zero server lag, zero external cost).
  - **Server-Side MP3 Generation:** Optional `gTTS` audio synthesis with inline player.
- **The Secret Science/Math Takeaway:** A dedicated spotlight card distilling the fundamental academic rule.
- **Concept Vocabulary Chest:** 3–4 interactive cards showing key terms, child-friendly definitions, and their exact contextual in-story usage.

### Step 3: Interactive Comprehension Quest
- **3 Dynamic Multiple-Choice Questions:**
  1. *Foundational Recall:* Core definition and conceptual recognition.
  2. *In-Story Reasoning:* How the character applied the concept to resolve the crisis.
  3. *Real-World Transfer:* Applying the concept to an unfamiliar real-world scenario outside the story.
- **State-Persistent Radio Architecture:** Utilizes Streamlit's `st.session_state` keys (`quiz_choice_0`, etc.) ensuring radio clicks and navigation never reset the story or clear user answers.
- **Instant Visual Feedback:**
  - Correct answers are highlighted with green celebratory badges and pedagogical reinforcement.
  - Incorrect answers provide gentle encouragement, reveal the correct answer, and explain the underlying reasoning.
  - 100% scores trigger animated celebration effects.
- **Retake & Navigate:** Option to retake without regenerating the story.

### Step 4: Parent & Educator Diagnostic Lab
- **Concept Mastery Score & Achievement Badges:**
  - 🏆 **100% — Concept Champion:** Flawless conceptual retention and real-world transfer.
  - 🌟 **67% — Skilled Explorer:** Solid foundation; minor review recommended for transfer tasks.
  - 💡 **33% — Apprentice Thinker:** Developing intuition; benefit from reinforced metaphors.
  - 🌱 **0% — Budding Inquirer:** Initial exposure gained; guided re-reading recommended.
- **Learning Milestones Met Breakdown:**
  - Milestone 1: Foundational Recall & Recognition (`✅ MET` or `⏳ REVIEW NEEDED`).
  - Milestone 2: Contextual Application & In-Story Logic (`✅ MET` or `⏳ REVIEW NEEDED`).
  - Milestone 3: Real-World Concept Transfer (`✅ MET` or `⏳ REVIEW NEEDED`).
- **Pedagogical Diagnostic Summary:** Detailed analysis of student performance and cognitive absorption.
- **Common Misconceptions Alert:** Highlights classic pitfalls children make for this specific topic (*e.g., confusing plant respiration with animal digestion*).
- **The Dinner-Table Discussion Question:** A conversation prompt parents or educators can ask casually over dinner or during circle time to bridge school concepts to everyday conversation.
- **Exportable Diagnostic Report:** 1-click download of a formatted Markdown report (`.md`).

---

## 🔒 3. Security & Production Quality

### Multi-Tier API Key Resolution
The application secures API credentials through a 3-tier fallback strategy:
1. **Local `.env`:** Loaded automatically via `python-dotenv` (`GEMINI_API_KEY`).
2. **Streamlit Secrets:** Detected automatically on Streamlit Cloud via `st.secrets["GEMINI_API_KEY"]` with graceful exception handling.
3. **Sidebar UI Key Entry:** Secure password field allowing end-users to enter their own API key without touching code.
4. **1-Click Pre-Built Interactive Demos:** Curated rich demos across all 3 age groups allowing instant evaluation without requiring an API key.

### Zero-Crash Structured Outputs
- Powered by the official `google-genai` SDK (`google.genai`).
- Enforces strict Pydantic schema validation using `response_schema=StoryTeacherResponse` and `response_mime_type="application/json"`.
- Clean JSON stripping fallback handles markdown code fences (` ```json `) to guarantee zero JSON parsing crashes.

---

## 🛠️ 4. Quick Start & Installation

### Prerequisites
- Python 3.10+ installed
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation Steps

1. **Clone or Navigate to the Repository:**
```bash
cd storyteacher-ai
```

2. **Create and Activate a Virtual Environment:**
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables:**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Alternatively, enter your API key directly in the web app sidebar).*

5. **Run the Application:**
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🧪 5. Running Automated Unit Tests

A comprehensive unit test suite is included in `test_app.py` to verify:
- Pydantic schema validation across all curated demo sets.
- JSON sanitizer and markdown code fence cleaning.
- Age-adapted pedagogical prompt generation.
- Exportable diagnostic report formatting.

Run the test suite with:
```bash
python test_app.py
```

---

## 📦 6. Project Structure

```
storyteacher-ai/
├── .streamlit/
│   └── config.toml          # Custom theme and server settings
├── app.py                   # Production-grade Streamlit web application
├── test_app.py              # Automated unit and integration test suite
├── requirements.txt         # Pinned application dependencies
├── .env.example             # Template for API credentials
└── README.md                # Comprehensive documentation and architecture guide
```

---

## 📄 License
StoryTeacher AI is open source under the MIT License.
