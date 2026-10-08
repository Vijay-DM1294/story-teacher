"""
StoryTeacher AI - Learn School Concepts Through Age-Adapted Stories
A production-grade EdTech web application built with Streamlit and Google Gemini API (google-genai SDK).
"""

import os
import json
import io
from typing import List, Dict, Any, Optional
import streamlit as st
from pydantic import BaseModel, Field

# Try loading dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing google-genai SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Try importing gTTS for optional offline/server MP3 generation
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


# ==============================================================================
# 1. DATA MODELS & STRUCTURED OUTPUT SCHEMAS
# ==============================================================================

class VocabularyItem(BaseModel):
    word: str = Field(description="The scientific or mathematical keyword")
    definition: str = Field(description="Kid-friendly 1-2 sentence definition adapted to the age level")
    in_story_usage: str = Field(description="Short sentence showing how it was used in the story")


class QuizQuestion(BaseModel):
    question: str = Field(description="Comprehension or concept transfer question")
    options: List[str] = Field(description="Exactly 4 distinct multiple-choice answer options")
    correct_index: int = Field(description="Zero-based index of the correct option (0, 1, 2, or 3)")
    explanation: str = Field(description="Kid-friendly explanation of why the correct answer is right")
    milestone: str = Field(description="Pedagogical category: 'Foundational Recall', 'In-Story Reasoning', or 'Real-World Transfer'")


class StoryTeacherResponse(BaseModel):
    title: str = Field(description="Exciting and catchy story title with a thematic emoji")
    mission_hook: str = Field(description="A high-stakes 2-3 sentence 'The Mission' challenge setting up the dilemma")
    story_content: str = Field(description="The main story narrative (300 to 400 words) using rich age-adapted prose with key terms in **bold**")
    science_takeaway: str = Field(description="The 'Secret Science/Math Takeaway' - 2-3 clear sentences explaining the core academic concept")
    vocabulary: List[VocabularyItem] = Field(description="3 to 4 core vocabulary terms with age-appropriate definitions")
    quiz: List[QuizQuestion] = Field(description="Exactly 3 multiple-choice comprehension questions")
    dinner_table_question: str = Field(description="A conversational, engaging prompt for parents or teachers to ask over dinner or in class")
    diagnostic_summary: str = Field(description="Pedagogical insight explaining how this story builds conceptual intuition")
    common_misconceptions: str = Field(description="Common pitfalls or misunderstandings children typically hold about this concept")


# ==============================================================================
# 2. CURATED DEMO ADVENTURES (INSTANT OFFLINE PREVIEW / DEMO MODE)
# ==============================================================================

CURATED_DEMOS: Dict[str, Dict[str, Any]] = {
    "Ages 5–7 (Early Explorers 🌱) - Photosynthesis": {
        "topic": "Photosynthesis",
        "age_bracket": "Ages 5–7 (Early Explorers 🌱)",
        "theme": "🧙‍♂️ Fantasy & Magic Quest",
        "protagonist": "Pip the Pixie",
        "data": {
            "title": "🍃 Pip and the Great Emerald Sun-Bakery",
            "mission_hook": "The enchanted Whispering Forest is losing its emerald sparkle! Pip the Pixie must unlock the ancient secret of the green leaf kitchen before the golden twilight fades forever.",
            "story_content": (
                "Deep inside the Whispering Forest lived **Pip the Pixie**, a cheerful sprite with sparkly wings. "
                "One sunny morning, Pip noticed the Great Oak tree looking sleepy and pale. 'Why aren't you eating your breakfast?' Pip chirped.\n\n"
                "The Great Oak rustled gently. 'Little Pip, trees don't eat crunchy berries like you do. We run a magical kitchen called **photosynthesis**!'\n\n"
                "Pip peeked closely under a glossy green leaf. Inside, billions of microscopic green chefs called **chlorophyll** were wearing tiny aprons! "
                "Chief Chef Fern waved a wooden spoon. 'Welcome to our leaf bakery! To bake delicious sweet sugars for our tree, we need three secret ingredients.'\n\n"
                "First, Chef Fern pointed down to the deep soil. 'Our roots sip cool **water** like a giant twisty straw!' Gurgle, gurgle went the sap.\n\n"
                "Next, tiny leaf windows called **stomata** opened with a quiet sigh. 'We catch invisible puffs of air called **carbon dioxide**,' whispered Fern.\n\n"
                "Finally, golden rays of **sunlight** streamed through the branches. The chlorophyll chefs caught the warm sunbeams like golden sprinkles! "
                "With a sizzling flash of green magic, the ingredients mixed together. 'Look!' cheered Pip. The bakery produced sweet **glucose sugar** to help the tree grow strong and tall.\n\n"
                "'And best of all,' laughed Chef Fern, opening the leaf windows wide, 'our kitchen breathes out fresh, clean **oxygen** for you, Pip, and all the forest creatures to breathe!'\n\n"
                "Pip danced a happy jig. Now the Whispering Forest sparkled brighter than ever, all powered by the quiet sunshine kitchen!"
            ),
            "science_takeaway": (
                "Plants make their own food through **photosynthesis**! By combining water from the soil, carbon dioxide from the air, "
                "and sunlight trapped by green **chlorophyll**, plants create nourishing sugars (glucose) and release the fresh oxygen we breathe."
            ),
            "vocabulary": [
                {
                    "word": "Photosynthesis",
                    "definition": "The amazing process green plants use to make their own food using sunlight, water, and air.",
                    "in_story_usage": "The Great Oak explained that its leaf kitchen runs on photosynthesis."
                },
                {
                    "word": "Chlorophyll",
                    "definition": "The special green pigment inside leaves that catches sunlight like a tiny solar panel.",
                    "in_story_usage": "Chief Chef Fern and the chlorophyll chefs trapped golden sunbeams."
                },
                {
                    "word": "Oxygen",
                    "definition": "The clean, invisible gas that plants give off, which humans and animals need to breathe.",
                    "in_story_usage": "The leaf bakery breathed out fresh oxygen for Pip and all forest friends."
                }
            ],
            "quiz": [
                {
                    "question": "What are the three main ingredients the leaf chefs need to make plant food?",
                    "options": [
                        "Sunlight, water, and carbon dioxide (air)",
                        "Milk, chocolate sprinkles, and butter",
                        "Moonlight, rocks, and raindrops",
                        "Soil pebbles, ice cubes, and honey"
                    ],
                    "correct_index": 0,
                    "explanation": "Plants require sunlight (energy), water from their roots, and carbon dioxide from the air to make glucose sugar!",
                    "milestone": "Foundational Recall"
                },
                {
                    "question": "What is the green helper inside leaves that catches the warm sunlight?",
                    "options": [
                        "Chlorophyll",
                        "Pinecone",
                        "Tree Bark",
                        "Glitter Dust"
                    ],
                    "correct_index": 0,
                    "explanation": "Chlorophyll is the special green pigment that absorbs light energy like a solar panel.",
                    "milestone": "In-Story Reasoning"
                },
                {
                    "question": "Why are green plants and trees so helpful to people and animals playing in the park?",
                    "options": [
                        "They release fresh oxygen for us to breathe while making their food",
                        "They hide secret toys underneath their roots",
                        "They turn the rain into soda pop",
                        "They make the clouds stay in one spot"
                    ],
                    "correct_index": 0,
                    "explanation": "When plants do photosynthesis, their wonderful 'leftover' gift to the world is oxygen, which we breathe every second!",
                    "milestone": "Real-World Transfer"
                }
            ],
            "dinner_table_question": "When you take a bite of an apple or a carrot at dinner tonight, can you guess where the stored sunshine went inside it?",
            "diagnostic_summary": "The child explored the foundational biological concept of autotrophic nutrition (photosynthesis). Focus is placed on energy transformation (light into chemical energy) and the mutualistic relationship between plant oxygen output and animal respiration.",
            "common_misconceptions": "Young children commonly believe plants 'eat dirt/soil' like animals eat food. Emphasize that soil provides water and minerals, but food (sugar) is actually baked from sunlight and air!"
        }
    },
    "Ages 8–10 (Adventurers 🔍) - Gravity": {
        "topic": "Gravity & Free Fall",
        "age_bracket": "Ages 8–10 (Adventurers 🔍)",
        "theme": "🕵️ Detective Mystery & Crime Lab",
        "protagonist": "Detective Maya Lin",
        "data": {
            "title": "🔍 Detective Maya and the Case of the Anti-Gravity Skateboard",
            "mission_hook": "At the annual Newton Middle School Science Expo, champion skater Leo's custom board suddenly began hovering six inches above the pavement! Maya Lin has 15 minutes before the finals to crack the mystery.",
            "story_content": (
                "Detective **Maya Lin** snapped her notebook shut as she skated into the bustling school courtyard. "
                "A crowd had gathered around Leo's neon-green skateboard, which was bobbing in mid-air like a cork in a bathtub.\n\n"
                "'It's defying **gravity**!' gasped Leo, pointing his wrench. 'Every time I let go, it floats! Am I disqualified?'\n\n"
                "Maya knelt down, pulling her magnifying glass and digital scale from her trench coat. "
                "'Nothing simply ignores **gravity**, Leo. Gravity is the invisible, mutual force of attraction that pulls objects with **mass** toward each other. "
                "Because Earth is enormous, it pulls everything—from skyscrapers to skateboards—straight toward its center at 9.8 meters per second squared.'\n\n"
                "Maya tested the air above the board. She dropped a heavy steel washer and a hollow plastic ping-pong ball simultaneously. "
                "Thud-click! Both struck the concrete at the exact same instant. 'See? In the absence of heavy air resistance, gravity accelerates all falling masses equally. "
                "So why is your board resisting Earth's pull?'\n\n"
                "Maya leaned beneath the wooden skate ramp. Her flashlight beam caught a strange silver glare. "
                "'Aha!' she shouted. Hidden under the plywood was a pair of industrial high-power electromagnets hooked up to a reversed battery pack! "
                "And embedded inside Leo's skateboard trucks were rare-earth neodymium magnets.\n\n"
                "'Your board isn't turning off gravity,' Maya grinned, switching the electromagnet power off. *Clack!* The skateboard dropped instantly to the concrete, anchored once again by Earth's steady gravitational grip. "
                "'The magnetic repulsion was simply pushing upward with a force greater than Earth's downward gravitational pull.'\n\n"
                "Leo beamed with relief. 'Mystery solved! Now that gravity is back in charge, watch me land this kickflip!'"
            ),
            "science_takeaway": (
                "**Gravity** is an invisible universal force of attraction between all objects that possess mass. "
                "Earth's massive size exerts a downward pull on everything near its surface. Objects only float when an equal or greater opposing force (like magnetism, lift, or buoyancy) pushes upward against gravity."
            ),
            "vocabulary": [
                {
                    "word": "Gravity",
                    "definition": "The fundamental attractive force pulling objects toward the center of any massive body, such as Earth.",
                    "in_story_usage": "Maya explained that gravity is the invisible force pulling everything with mass."
                },
                {
                    "word": "Mass",
                    "definition": "The amount of matter or 'stuff' that makes up an object, determining how strongly gravity acts upon it.",
                    "in_story_usage": "Maya noted that gravity pulls on all objects that possess mass."
                },
                {
                    "word": "Opposing Force",
                    "definition": "A counteracting push or pull acting in the reverse direction of another force.",
                    "in_story_usage": "The magnetic repulsion created an upward opposing force overcoming gravity."
                }
            ],
            "quiz": [
                {
                    "question": "What causes the Earth to pull skateboards, people, and buildings downward?",
                    "options": [
                        "Earth's immense mass creates a powerful gravitational pull toward its center",
                        "The atmosphere blows a giant downward wind",
                        "Earth is a giant freezer that freezes things to the ground",
                        "The spin of the Earth glues things onto the dirt"
                    ],
                    "correct_index": 0,
                    "explanation": "Any object with mass exerts gravity; because planet Earth has such a colossal mass, its gravitational pull anchors everything toward its center.",
                    "milestone": "Foundational Recall"
                },
                {
                    "question": "Why did Leo's skateboard hover off the ground in the courtyard?",
                    "options": [
                        "An upward magnetic force was pushing up with greater strength than gravity's downward pull",
                        "Earth temporarily turned off gravity in that specific 10-foot square",
                        "The skateboard had no mass inside its wooden deck",
                        "Maya Lin cast a wizard spell on the wheels"
                    ],
                    "correct_index": 0,
                    "explanation": "Gravity never turns off! The skateboard hovered because an upward magnetic force balanced and exceeded the downward pull of gravity.",
                    "milestone": "In-Story Reasoning"
                },
                {
                    "question": "When astronauts float inside the International Space Station, why do they appear weightless?",
                    "options": [
                        "They are in continuous free fall orbiting around Earth alongside the station",
                        "Gravity completely stops existing the moment you leave Earth's clouds",
                        "The space station is made of anti-gravity foam",
                        "The moon sucks all gravity away into outer space"
                    ],
                    "correct_index": 0,
                    "explanation": "Earth's gravity is actually still about 90% as strong at ISS orbit! The astronauts float because the station and astronauts are both falling around Earth at high forward speed (free fall).",
                    "milestone": "Real-World Transfer"
                }
            ],
            "dinner_table_question": "If you drop a flat piece of paper and a crumpled paper ball at the same time, which hits first, and why does gravity treat them differently?",
            "diagnostic_summary": "The student investigated gravitational acceleration, mass, and net forces. The mystery structure reinforces that apparent weightlessness or levitation is caused by opposing forces or free-fall dynamics, rather than the absence of gravity.",
            "common_misconceptions": "Children frequently believe heavier objects fall faster regardless of air resistance, or that space has 'zero gravity' everywhere. Reinforce that gravity operates across all distances and accelerates all masses identically in vacuum."
        }
    },
    "Ages 11–13 (Trailblazers 🚀) - Fractions & Ratios": {
        "topic": "Fractions & Proportional Ratios",
        "age_bracket": "Ages 11–13 (Trailblazers 🚀)",
        "theme": "🚀 Space & Sci-Fi Voyage",
        "protagonist": "Commander Alex Vance",
        "data": {
            "title": "🚀 Orbit Station Nexus: The Oxygen Ratio Emergency",
            "mission_hook": "Orbital Station Nexus has suffered a micrometeorite strike on Life-Support Sector 4! Commander Alex Vance has 12 minutes to balance the scrubber tanks before atmospheric toxicity crosses the critical threshold.",
            "story_content": (
                "The emergency klaxon wailed across Station Nexus as Commander **Alex Vance** propelled herself along the zero-G transit tunnel. "
                "On the heads-up display, the atmospheric telemetry flashed amber: **Oxygen (O₂)** was plummeting, while **Nitrogen (N₂)** and **Carbon Dioxide (CO₂)** levels skewed erratically.\n\n"
                "'Primary life-support computer offline,' crackled the flight engineer over comms. 'Manual scrubber synthesis required. "
                "Alex, our habitat mixture must maintain an exact **fractional proportion** of 1/5 oxygen to 4/5 nitrogen to keep the crew conscious.'\n\n"
                "Alex reached the manual mixing console. Three reserve tanks were available, each displaying different liquid volume fractions. "
                "Tank Alpha held 300 liters at 2/3 purity. Tank Beta held 600 liters at 1/2 purity. Tank Gamma was an emergency buffer containing 450 liters at 4/9 purity.\n\n"
                "'To purge toxicity, we need exactly 400 liters of pure, unadulterated O₂ into the main ventilation plenum,' Alex calculated, her stylus flying across the scratchpad. "
                "'Tank Alpha gives us: 300 liters multiplied by 2/3, which yields exactly 200 liters of pure O₂. "
                "Tank Beta gives us: 600 liters multiplied by 1/2, yielding 300 liters. "
                "If I open Alpha completely and tap exactly 2/3 of Beta's output (2/3 of 300 = 200 liters), we achieve 200 + 200 = 400 liters precisely!'\n\n"
                "Alex aligned the digital flow meters, setting Tank Alpha to 3/3 valve capacity and Tank Beta to 2/3 throttle. "
                "High-pressure vapor surged through the manifold pipes. On the environmental console, the overall chamber ratio calibrated with laser precision: "
                "21% O₂ to 78% N₂, matching the 1/5 to 4/5 habitable atmospheric **ratio**.\n\n"
                "The red warning lamps transitioned to a tranquil cyan. The automated voice chimed: *'Atmosphere stabilized. Oxygen-nitrogen equilibrium restored.'* "
                "Alex wiped the perspiration from her visor. Mathematical precision under pressure had just saved 120 souls on Orbit Station Nexus."
            ),
            "science_takeaway": (
                "**Fractions and ratios** describe proportional relationships between parts and wholes. "
                "When combining fractional mixtures or calculating required quantities, multiplying fractions by whole quantities ($300 \\times \\frac{2}{3} = 200$) "
                "allows exact chemical balancing and proportional control in engineering and daily life."
            ),
            "vocabulary": [
                {
                    "word": "Fractional Proportion",
                    "definition": "A mathematical relationship comparing a part of a quantity relative to the whole unit.",
                    "in_story_usage": "The habitat required an exact fractional proportion of 1/5 oxygen to 4/5 nitrogen."
                },
                {
                    "word": "Equilibrium Ratio",
                    "definition": "A balanced comparison between two or more quantities that maintains stability.",
                    "in_story_usage": "Alex calibrated the flow to restore the oxygen-nitrogen equilibrium ratio."
                },
                {
                    "word": "Common Denominator",
                    "definition": "A shared multiple of the denominators of several fractions, allowing direct addition or comparison.",
                    "in_story_usage": "Fractions with common denominators can be directly combined to solve mixing puzzles."
                }
            ],
            "quiz": [
                {
                    "question": "If Tank Alpha contains 300 liters of gas at 2/3 oxygen purity, how many liters of pure oxygen does it yield?",
                    "options": [
                        "200 liters (because 300 × 2/3 = 200)",
                        "150 liters (because 300 ÷ 2 = 150)",
                        "100 liters (because 300 × 1/3 = 100)",
                        "250 liters (because 300 - 50 = 250)"
                    ],
                    "correct_index": 0,
                    "explanation": "To find a fraction of a quantity, multiply: 300 × (2/3) = (300 ÷ 3) × 2 = 100 × 2 = 200 liters of pure oxygen.",
                    "milestone": "Foundational Recall"
                },
                {
                    "question": "Why did Commander Alex need to combine fractions precisely rather than just opening all valves to maximum?",
                    "options": [
                        "The human respiratory system requires a specific 1/5 O₂ to 4/5 N₂ ratio; too much pure oxygen is toxic and explosive",
                        "Opening all valves would drain the station's electrical batteries",
                        "The tanks would freeze solid if opened together",
                        "The station gravity would flip upside down"
                    ],
                    "correct_index": 0,
                    "explanation": "Chemical and atmospheric engineering relies on exact ratios. Over-concentrating oxygen is hazardous, while under-concentrating causes hypoxia.",
                    "milestone": "In-Story Reasoning"
                },
                {
                    "question": "If a baker wants to quadruple (4x) a recipe calling for 3/4 cup of sugar, how many total cups of sugar are needed?",
                    "options": [
                        "3 cups (because 4 × 3/4 = 12/4 = 3)",
                        "1.5 cups (because 4 × 1/4 = 1)",
                        "7 cups (because 4 + 3 = 7)",
                        "2.25 cups (because 3/4 + 1 = 1.75)"
                    ],
                    "correct_index": 0,
                    "explanation": "Multiplying 4 by 3/4 equals (4 × 3) / 4 = 12/4 = 3 whole cups of sugar! Proportional scaling works the same in baking as in spacecraft engineering.",
                    "milestone": "Real-World Transfer"
                }
            ],
            "dinner_table_question": "If our family pizza has 8 slices and we eat 6 slices, what fraction remains? How would you write that in lowest terms?",
            "diagnostic_summary": "The student applied fractional multiplication, part-to-whole proportions, and ratio preservation in an engineering context. Demonstrates mastery over fractional arithmetic as a practical tool for resource management.",
            "common_misconceptions": "Middle school students often mistakenly add denominators when combining fractions or struggle to conceptualize multiplying a whole number by a fraction less than 1 as finding a smaller part of the total."
        }
    }
}


# ==============================================================================
# 3. HELPER FUNCTIONS & GEMINI CLIENT ENGINE
# ==============================================================================

def get_api_key() -> Optional[str]:
    """Retrieve Gemini API Key from environment, st.secrets, or session state."""
    # 1. Check Streamlit Session State (sidebar input)
    if st.session_state.get("custom_api_key"):
        return st.session_state["custom_api_key"].strip()

    # 2. Check local environment (.env)
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 3. Check Streamlit secrets (Streamlit Cloud deployment)
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        pass

    return None


def clean_json_string(raw_text: str) -> str:
    """Strip markdown code block markers and leading/trailing whitespace."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def build_system_prompt(age_bracket: str) -> str:
    """Return tailored pedagogical directives for the chosen age bracket."""
    if "5–7" in age_bracket or "Early Explorers" in age_bracket:
        return (
            "PEDAGOGICAL PROFILE: Ages 5–7 (Early Explorers 🌱)\n"
            "- Reading Level: Lexile 200L-400L (Kindergarten to Grade 2).\n"
            "- Vocabulary: Sensory, tactile, concrete words (glowing, sweet, bouncing, breezy). NO unexplained jargon.\n"
            "- Sentence Length: Very short, rhythmic sentences (6 to 11 words per sentence).\n"
            "- Metaphors: Friendly kitchen baking, magic gardens, cheerful animal friends, cozy stakes.\n"
            "- Narrative Arc: Clear 3-act story: 1) Gentle puzzle, 2) Discovering nature's secret trick, 3) Happy celebration.\n"
            "- Key Concept Terms: Must highlight core terms in **bold**.\n"
        )
    elif "8–10" in age_bracket or "Adventurers" in age_bracket:
        return (
            "PEDAGOGICAL PROFILE: Ages 8–10 (Adventurers 🔍)\n"
            "- Reading Level: Lexile 500L-750L (Grade 3 to Grade 5).\n"
            "- Vocabulary: Dynamic verbs, detective puzzles, secret codes, playful gadgets, schoolyard science.\n"
            "- Sentence Length: Balanced sentences (10 to 18 words) with energetic dialogue.\n"
            "- Metaphors: Detective mysteries, superhero power-ups, sports strategies, contraptions.\n"
            "- Narrative Arc: High curiosity: 1) Baffling mystery/heist, 2) Using the scientific principle to crack the clue, 3) Triumph.\n"
            "- Key Concept Terms: Must highlight core terms in **bold**.\n"
        )
    else:  # Ages 11–13 (Trailblazers)
        return (
            "PEDAGOGICAL PROFILE: Ages 11–13 (Trailblazers 🚀)\n"
            "- Reading Level: Lexile 800L-1050L (Grade 6 to Grade 8).\n"
            "- Vocabulary: Accurate technical terminology, mathematical relationships, cause-and-effect physical laws.\n"
            "- Sentence Length: Engaging, sophisticated prose (14 to 25 words).\n"
            "- Metaphors: Sci-fi telemetry, deep-space survival, cyberpunk coding, environmental engineering, planetary expeditions.\n"
            "- Narrative Arc: High stakes: 1) Critical crisis/emergency, 2) Applying rigorous mathematical/scientific law, 3) Equilibrium restored.\n"
            "- Key Concept Terms: Must highlight core technical terms in **bold**.\n"
        )


def generate_story_with_gemini(
    topic: str,
    age_bracket: str,
    theme: str,
    protagonist: str,
    api_key: str,
    model_name: str = "gemini-3.8-flash",
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Call Google Gemini API using google-genai SDK with structured output validation."""
    if not GENAI_AVAILABLE:
        raise RuntimeError("The 'google-genai' SDK is not installed. Please run: pip install google-genai")

    client = genai.Client(api_key=api_key)
    pedagogy_guide = build_system_prompt(age_bracket)

    user_prompt = f"""
You are StoryTeacher AI, an elite EdTech specialist, award-winning children's author, and master science teacher.
Your mission is to teach the school concept '{topic}' through a thrilling, age-adapted story, followed by an interactive 3-question comprehension quiz and a parent/educator diagnostic report.

MISSION PARAMETERS:
- Topic: {topic}
- Target Audience: {age_bracket}
- Story Theme: {theme}
- Protagonist Name: {protagonist}

{pedagogy_guide}

CRITICAL CONTENT SPECIFICATIONS:
1. Title: Catchy, engaging title with an emoji matching the theme.
2. The Mission Hook: 2-3 sentences setting up the high-stakes dilemma or mystery.
3. Story Content: Exactly 300 to 400 words. Vibrant narrative. Key scientific or mathematical terms MUST be formatted in **bold**.
4. Secret Science/Math Takeaway: 2-3 clear sentences summarizing the real-world principle in plain language.
5. Vocabulary: Exactly 3 to 4 core vocabulary terms with age-adapted definitions and short in-story usage examples.
6. Quiz: Exactly 3 multiple-choice questions:
   - Question 1 (Foundational Recall): Tests identifying the core definition or concept.
   - Question 2 (In-Story Reasoning): Tests understanding how the hero applied the concept in the plot.
   - Question 3 (Real-World Transfer): Tests applying the concept to an everyday real-world situation outside the story.
   Each question MUST have exactly 4 plausible choices, a 0-based correct_index (0, 1, 2, or 3), and a warm, encouraging explanation.
7. Dinner-Table Discussion Question: A delightful, conversational question parents or teachers can ask casually at dinner or in morning circle time to spark curious family dialogue.
8. Diagnostic Summary & Common Misconceptions: Analytical insights for educators and parents explaining what concept was taught and typical pitfalls children encounter with this topic.
"""

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=StoryTeacherResponse,
        temperature=temperature,
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=config,
        )
    except Exception as e:
        # Fallback to gemini-3.8-flash if model name is unrecognized
        if model_name != "gemini-3.8-flash":
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_prompt,
                config=config,
            )
        else:
            raise e

    # Parse structured output safely
    if hasattr(response, "parsed") and response.parsed is not None:
        if isinstance(response.parsed, BaseModel):
            return response.parsed.model_dump()
        elif isinstance(response.parsed, dict):
            return response.parsed

    # Secondary parse from text if needed
    cleaned_json = clean_json_string(response.text)
    data = json.loads(cleaned_json)
    validated = StoryTeacherResponse(**data)
    return validated.model_dump()


def generate_audio_gtts(text: str) -> Optional[bytes]:
    """Generate speech audio bytes using gTTS if available."""
    if not GTTS_AVAILABLE:
        return None
    try:
        clean_text = text.replace("**", "").replace("*", "").replace("#", "")
        # Truncate to reasonable length for quick generation
        tts = gTTS(text=clean_text[:1200], lang="en", slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return None


# ==============================================================================
# 4. STREAMLIT APPLICATION & UI STYLING
# ==============================================================================

def setup_page_config():
    """Configure Streamlit page layout and custom CSS styling."""
    st.set_page_config(
        page_title="StoryTeacher AI | Learn Any Concept Through Stories",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
    /* Google-inspired modern EdTech styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #4338CA 0%, #6366F1 50%, #8B5CF6 100%);
        padding: 2.2rem 2.4rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.25);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        color: #FFFFFF !important;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        max-width: 850px;
        line-height: 1.5;
        margin: 0;
        color: #F1F5F9 !important;
    }

    /* Step Navigation Badges */
    .step-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.9rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.88rem;
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
    }

    .step-pill-active {
        background: #EEF2FF;
        color: #4338CA;
        border-color: #C7D2FE;
    }

    /* Story Card Elements */
    .mission-card {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 1.2rem 0;
    }

    .mission-tag {
        font-weight: 800;
        color: #B45309;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }

    .story-body-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2rem;
        font-size: 1.08rem;
        line-height: 1.85;
        color: #1E293B;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .story-body-card strong {
        color: #4F46E5;
        background: #EEF2FF;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }

    .science-takeaway-card {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 5px solid #10B981;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 1.4rem 0;
    }

    .vocab-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s;
    }

    .vocab-term {
        font-weight: 700;
        color: #4338CA;
        font-size: 1.05rem;
    }

    /* Quiz Styling */
    .quiz-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }

    .quiz-q-num {
        font-weight: 800;
        color: #6366F1;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-correct {
        background: #D1FAE5;
        color: #065F46;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }

    .badge-wrong {
        background: #FEE2E2;
        color: #991B1B;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }

    /* Diagnostic Report Card */
    .diagnostic-hero {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }

    .dinner-table-card {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        border: 2px dashed #F97316;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }

    .dinner-title {
        color: #C2410C;
        font-weight: 800;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize persistent Streamlit session state."""
    if "current_step" not in st.session_state:
        st.session_state["current_step"] = 1
    if "story_data" not in st.session_state:
        st.session_state["story_data"] = None
    if "active_topic" not in st.session_state:
        st.session_state["active_topic"] = "Photosynthesis"
    if "active_age" not in st.session_state:
        st.session_state["active_age"] = "Ages 5–7 (Early Explorers 🌱)"
    if "active_theme" not in st.session_state:
        st.session_state["active_theme"] = "🧙‍♂️ Fantasy & Magic Quest"
    if "active_protagonist" not in st.session_state:
        st.session_state["active_protagonist"] = "Pip"
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = 0
    if "audio_bytes" not in st.session_state:
        st.session_state["audio_bytes"] = None
    if "custom_api_key" not in st.session_state:
        st.session_state["custom_api_key"] = ""


# ==============================================================================
# 5. SIDEBAR & API KEY MANAGEMENT
# ==============================================================================

def render_sidebar():
    """Render application controls, API key safety checker, and settings in sidebar."""
    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")

        api_key = get_api_key()
        if api_key:
            st.success("🟢 **Gemini API Connected**", icon="✅")
        else:
            st.warning("🟡 **No API Key Detected**", icon="🔑")

        with st.expander("🔑 Configure API Key", expanded=not bool(api_key)):
            st.markdown(
                "Enter your **Google Gemini API Key** below or save it in `.env` as `GEMINI_API_KEY`."
            )
            key_input = st.text_input(
                "Gemini API Key",
                value=st.session_state.get("custom_api_key", ""),
                type="password",
                help="Get a free API key at https://aistudio.google.com/app/apikey",
                key="sidebar_key_field"
            )
            if key_input:
                st.session_state["custom_api_key"] = key_input
            
            st.markdown(
                "[👉 Get a free Gemini API Key](https://aistudio.google.com/app/apikey)"
            )

        st.markdown("---")
        st.markdown("#### 🤖 Model Parameters")
        model_choice = st.selectbox(
            "Gemini Model",
            options=["gemini-3.8-flash", "gemini-3.8-flash"],
            index=0,
            help="Gemini 2.5 Flash provides optimal speed and high storytelling fidelity."
        )
        st.session_state["model_choice"] = model_choice

        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.2,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="0.7 balances lively storytelling with scientific accuracy."
        )
        st.session_state["temperature"] = temperature

        st.markdown("---")
        st.markdown("#### ⚡ 1-Click Interactive Demos")
        st.caption("Test the full 4-step experience without entering an API key:")
        
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            if st.button("🌱 Ages 5-7\n(Photosynthesis)", use_container_width=True):
                load_demo("Ages 5–7 (Early Explorers 🌱) - Photosynthesis")
        with col_demo2:
            if st.button("🔍 Ages 8-10\n(Gravity)", use_container_width=True):
                load_demo("Ages 8–10 (Adventurers 🔍) - Gravity")

        if st.button("🚀 Ages 11-13\n(Fractions & Ratios)", use_container_width=True):
            load_demo("Ages 11–13 (Trailblazers 🚀) - Fractions & Ratios")

        st.markdown("---")
        if st.button("🔄 Reset Adventure", use_container_width=True):
            st.session_state["story_data"] = None
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_score"] = 0
            st.session_state["audio_bytes"] = None
            st.session_state["current_step"] = 1
            for k in list(st.session_state.keys()):
                if k.startswith("quiz_choice_"):
                    del st.session_state[k]
            st.rerun()


def load_demo(demo_key: str):
    """Load pre-compiled rich interactive demo data."""
    demo = CURATED_DEMOS[demo_key]
    st.session_state["active_topic"] = demo["topic"]
    st.session_state["active_age"] = demo["age_bracket"]
    st.session_state["active_theme"] = demo["theme"]
    st.session_state["active_protagonist"] = demo["protagonist"]
    st.session_state["story_data"] = demo["data"]
    st.session_state["quiz_submitted"] = False
    st.session_state["quiz_score"] = 0
    st.session_state["audio_bytes"] = None
    st.session_state["current_step"] = 2
    for k in list(st.session_state.keys()):
        if k.startswith("quiz_choice_"):
            del st.session_state[k]
    st.rerun()


# ==============================================================================
# 6. STEP 1: TOPIC INPUT & ADVENTURE CONFIGURATION
# ==============================================================================

def render_step_1():
    """Render Step 1: Topic selection, age adaptation tier, and theme picker."""
    st.markdown("### 🎯 Step 1: Craft Your Learning Adventure")
    st.markdown("Choose any school concept or pick a popular topic below:")

    # Quick selection pills
    quick_topics = [
        ("🌿 Photosynthesis", "Photosynthesis"),
        ("🍎 Gravity", "Gravity & Free Fall"),
        ("🍕 Fractions", "Fractions & Proportions"),
        ("🕳️ Black Holes", "Black Holes & Gravity"),
        ("💧 Water Cycle", "The Water Cycle"),
        ("⚡ Circuits", "Electric Circuits & Current"),
        ("🏔️ Plate Tectonics", "Plate Tectonics & Earthquakes"),
        ("🧬 DNA & Genetics", "DNA & Inheritance"),
        ("➖ Negative Numbers", "Negative Numbers & Number Line"),
    ]

    st.markdown("**Quick Pick Samples:**")
    pill_cols = st.columns(len(quick_topics))
    for i, (label, val) in enumerate(quick_topics):
        with pill_cols[i]:
            if st.button(label, key=f"quick_topic_{i}", use_container_width=True):
                st.session_state["input_topic"] = val
                st.session_state["active_topic"] = val

    col_input1, col_input2 = st.columns([3, 2])
    with col_input1:
        topic_input = st.text_input(
            "School Science / Math Concept:",
            value=st.session_state.get("input_topic", st.session_state.get("active_topic", "Photosynthesis")),
            placeholder="e.g., Photosynthesis, The Pythagorean Theorem, Newton's Third Law, Mitosis...",
            help="Type ANY academic concept you want to teach through a story!"
        )
        st.session_state["active_topic"] = topic_input

    with col_input2:
        protagonist_input = st.text_input(
            "Hero / Protagonist Name:",
            value=st.session_state.get("active_protagonist", "Alex"),
            placeholder="e.g., Alex, Maya, Leo, Zara...",
            help="Personalize the story with your child or student's favorite name!"
        )
        st.session_state["active_protagonist"] = protagonist_input

    st.markdown("---")
    st.markdown("#### 🧠 Age-Adapted Story Engine & World Theme")

    col_age, col_theme = st.columns(2)
    with col_age:
        age_options = [
            "Ages 5–7 (Early Explorers 🌱)",
            "Ages 8–10 (Adventurers 🔍)",
            "Ages 11–13 (Trailblazers 🚀)"
        ]
        # Match current index safely
        current_age = st.session_state.get("active_age", age_options[0])
        age_idx = age_options.index(current_age) if current_age in age_options else 0
        
        selected_age = st.radio(
            "Select Target Age Group:",
            options=age_options,
            index=age_idx,
            help="Dynamically alters vocabulary complexity, sentence length, and metaphor design."
        )
        st.session_state["active_age"] = selected_age

        # Display pedagogical explanation card
        if "5–7" in selected_age:
            st.info("🌱 **Ages 5–7 Engine:** Simple words, sensory metaphors (leaf bakeries, sunshine cookies), short rhythmic sentences, gentle stakes.")
        elif "8–10" in selected_age:
            st.info("🔍 **Ages 8–10 Engine:** Detective mysteries, comic quests, gadgets, schoolyard science puzzles, dynamic verbs, witty dialogue.")
        else:
            st.info("🚀 **Ages 11–13 Engine:** Deep-space sci-fi, survival missions, accurate formulas and technical terms, high narrative stakes.")

    with col_theme:
        theme_options = [
            "🧙‍♂️ Fantasy & Magic Quest",
            "🚀 Space & Sci-Fi Voyage",
            "🕵️ Detective Mystery & Crime Lab",
            "🦸 Superhero & Comic Quest",
            "🌿 Jungle Safari & Wildlife Adventure",
            "💻 Cyber Matrix & Tech Lab",
            "⏳ Time Travel Chrono-Missions"
        ]
        current_theme = st.session_state.get("active_theme", theme_options[0])
        theme_idx = theme_options.index(current_theme) if current_theme in theme_options else 0
        
        selected_theme = st.selectbox(
            "Select Story World Theme:",
            options=theme_options,
            index=theme_idx,
            help="Sets the setting, aesthetic, and imaginative backdrop of the quest."
        )
        st.session_state["active_theme"] = selected_theme

    st.markdown("---")
    col_btn, col_msg = st.columns([1, 2])
    with col_btn:
        generate_clicked = st.button("✨ Generate Story Adventure", type="primary", use_container_width=True)

    with col_msg:
        api_key = get_api_key()
        if not api_key:
            st.caption("⚠️ No API key set. You can click any **1-Click Interactive Demo** in the sidebar or enter your API key to generate live!")

    if generate_clicked:
        if not topic_input.strip():
            st.error("Please enter a concept topic to generate a story!")
            return

        api_key = get_api_key()
        if not api_key:
            st.error("🔑 Please provide a Gemini API Key in the sidebar or environment to generate a custom story. Alternatively, test with our 1-Click Interactive Demos in the sidebar!")
            return

        with st.spinner(f"🧙‍♂️ StoryTeacher AI is crafting your {selected_age.split()[1]} adventure on '{topic_input}' with Gemini..."):
            try:
                story_response = generate_story_with_gemini(
                    topic=topic_input,
                    age_bracket=selected_age,
                    theme=selected_theme,
                    protagonist=protagonist_input,
                    api_key=api_key,
                    model_name=st.session_state.get("model_choice", "gemini-3.8-flash"),
                    temperature=st.session_state.get("temperature", 0.7)
                )
                st.session_state["story_data"] = story_response
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_score"] = 0
                st.session_state["audio_bytes"] = None
                st.session_state["current_step"] = 2
                for k in list(st.session_state.keys()):
                    if k.startswith("quiz_choice_"):
                        del st.session_state[k]
                st.success("🎉 Adventure generated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Generation error: {str(e)}")
                st.info("Tip: Double-check your Gemini API key or try selecting 'gemini-3.8-flash' in the sidebar.")


# ==============================================================================
# 7. STEP 2: STORY GENERATION & AUDIO NARRATION
# ==============================================================================

def render_step_2():
    """Render Step 2: The story adventure, hook, read-aloud controls, takeaway, and vocab chest."""
    story_data = st.session_state.get("story_data")
    if not story_data:
        st.warning("No story loaded yet. Please complete Step 1 or load an Interactive Demo from the sidebar!")
        if st.button("⬅️ Back to Step 1: Craft Adventure"):
            st.session_state["current_step"] = 1
            st.rerun()
        return

    # Header tags
    topic = st.session_state.get("active_topic", "Science Concept")
    age = st.session_state.get("active_age", "All Ages")
    theme = st.session_state.get("active_theme", "Adventure")

    col_meta1, col_meta2, col_meta3 = st.columns([2, 1, 1])
    with col_meta1:
        st.markdown(f"## {story_data.get('title', 'The Learning Quest')}")
    with col_meta2:
        st.caption(f"**Target Age:** {age.split('(')[0]}")
    with col_meta3:
        st.caption(f"**Theme:** {theme.split('&')[0]}")

    # The Mission Hook
    st.markdown(f"""
    <div class="mission-card">
        <div class="mission-tag">🎯 THE MISSION HOOK</div>
        <div style="font-size: 1.05rem; font-weight: 500; color: #78350F; line-height: 1.6;">
            {story_data.get('mission_hook', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Audio Read-Aloud Controls
    render_audio_controls(story_data.get('story_content', ''))

    # The Main Story Body
    st.markdown("### 📖 The Adventure Story")
    story_paragraphs = story_data.get('story_content', '').split('\n\n')
    formatted_story = "".join(f"<p>{p}</p>" for p in story_paragraphs if p.strip())
    
    st.markdown(f"""
    <div class="story-body-card">
        {formatted_story}
    </div>
    """, unsafe_allow_html=True)

    # Secret Science Takeaway
    st.markdown(f"""
    <div class="science-takeaway-card">
        <div style="font-weight: 800; color: #065F46; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
            💡 THE SECRET SCIENCE / MATH TAKEAWAY
        </div>
        <div style="font-size: 1.05rem; color: #064E3B; line-height: 1.6;">
            {story_data.get('science_takeaway', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Vocabulary Chest
    vocab_list = story_data.get('vocabulary', [])
    if vocab_list:
        st.markdown("### 📚 Key Concept Vocabulary Chest")
        vcols = st.columns(len(vocab_list))
        for i, item in enumerate(vocab_list):
            with vcols[i]:
                st.markdown(f"""
                <div class="vocab-card">
                    <div class="vocab-term">{item.get('word', '')}</div>
                    <div style="font-size: 0.9rem; color: #475569; margin-top: 0.3rem;">
                        <strong>Meaning:</strong> {item.get('definition', '')}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-top: 0.4rem; font-style: italic;">
                        "{item.get('in_story_usage', '')}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("⬅️ Edit Adventure Parameters (Step 1)", use_container_width=True):
            st.session_state["current_step"] = 1
            st.rerun()
    with col_nav2:
        if st.button("Proceed to Comprehension Quest (Step 3) ➔", type="primary", use_container_width=True):
            st.session_state["current_step"] = 3
            st.rerun()


def render_audio_controls(story_text: str):
    """Render browser-based Web Speech API narration and optional gTTS audio."""
    with st.expander("🔊 Audio Narration (Read Aloud)", expanded=False):
        clean_text = story_text.replace("**", "").replace("*", "").replace("\n", " ")
        safe_js_text = json.dumps(clean_text)

        # Web Speech API in-browser synthesis
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
            <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.5rem;">🎙️ In-Browser Interactive Narrator</div>
            <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.8rem;">
                Listen to the story read aloud instantly using your device's natural voice engine:
            </p>
            <div style="display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap;">
                <button onclick="speakStory()" style="background: #4F46E5; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    ▶️ Read Aloud
                </button>
                <button onclick="pauseSpeech()" style="background: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    ⏸️ Pause
                </button>
                <button onclick="stopSpeech()" style="background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    ⏹️ Stop
                </button>
            </div>
        </div>

        <script>
        const storyStoryText = {safe_js_text};
        let synth = window.speechSynthesis;
        let utterance = null;

        function speakStory() {{
            if (!synth) return;
            synth.cancel();
            utterance = new SpeechSynthesisUtterance(storyStoryText);
            utterance.rate = 0.95;
            utterance.pitch = 1.05;
            synth.speak(utterance);
        }}

        function pauseSpeech() {{
            if (synth.speaking && !synth.paused) {{
                synth.pause();
            }} else if (synth.paused) {{
                synth.resume();
            }}
        }}

        function stopSpeech() {{
            if (synth) {{
                synth.cancel();
            }}
        }}
        </script>
        """, unsafe_allow_html=True)

        if GTTS_AVAILABLE:
            if st.button("Generate Server MP3 Audio"):
                with st.spinner("Synthesizing audio narration..."):
                    audio = generate_audio_gtts(story_text)
                    if audio:
                        st.session_state["audio_bytes"] = audio
                        st.audio(audio, format="audio/mp3")
                    else:
                        st.warning("Could not generate audio. Please use the browser narrator above.")
        else:
            st.caption("ℹ️ Web Speech API is ready. (Install `gTTS` to generate standalone MP3 audio files).")


# ==============================================================================
# 8. STEP 3: INTERACTIVE COMPREHENSION QUIZ (STATE-PERSISTENT)
# ==============================================================================

def render_step_3():
    """Render Step 3: Interactive Comprehension Quiz with persistent session state."""
    story_data = st.session_state.get("story_data")
    if not story_data:
        st.warning("No active adventure. Please generate a story first!")
        if st.button("⬅️ Back to Step 1"):
            st.session_state["current_step"] = 1
            st.rerun()
        return

    quiz_questions = story_data.get("quiz", [])
    if not quiz_questions:
        st.error("No quiz questions found in this adventure.")
        return

    st.markdown("### 🧩 Step 3: Interactive Comprehension Quest")
    st.markdown(
        f"Test your mastery of **{st.session_state.get('active_topic', 'the concept')}**! Answer the 3 questions below to check your understanding."
    )

    submitted = st.session_state.get("quiz_submitted", False)

    for i, q in enumerate(quiz_questions):
        st.markdown(f"""
        <div class="quiz-card">
            <div class="quiz-q-num">QUESTION {i+1} of 3 • {q.get('milestone', 'Comprehension')}</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #1E293B; margin: 0.5rem 0 1rem 0;">
                {q.get('question', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        options = q.get("options", [])
        # Session state key for radio choice
        radio_key = f"quiz_choice_{i}"
        
        # When rendered as radio, selections are preserved across Streamlit reruns
        selected_option = st.radio(
            f"Select your answer for Question {i+1}:",
            options=options,
            key=radio_key,
            label_visibility="collapsed",
            disabled=submitted  # Lock choices after submission
        )

        # Show feedback if quiz has been submitted
        if submitted:
            correct_idx = q.get("correct_index", 0)
            user_idx = options.index(selected_option) if selected_option in options else -1
            is_correct = (user_idx == correct_idx)

            if is_correct:
                st.markdown(f"""
                <div class="badge-correct">
                    ✅ <strong>Spot on! You got it right!</strong>
                </div>
                <div style="font-size: 0.95rem; color: #065F46; margin-top: 0.3rem;">
                    {q.get('explanation', '')}
                </div>
                """, unsafe_allow_html=True)
            else:
                correct_text = options[correct_idx] if 0 <= correct_idx < len(options) else "N/A"
                st.markdown(f"""
                <div class="badge-wrong">
                    💡 <strong>Nice try! Correct answer:</strong> {correct_text}
                </div>
                <div style="font-size: 0.95rem; color: #991B1B; margin-top: 0.3rem;">
                    {q.get('explanation', '')}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    
    col_action1, col_action2, col_action3 = st.columns([1, 1, 1])

    with col_action1:
        if not submitted:
            if st.button("🎯 Submit My Answers", type="primary", use_container_width=True):
                # Calculate score
                score = 0
                for i, q in enumerate(quiz_questions):
                    opts = q.get("options", [])
                    user_val = st.session_state.get(f"quiz_choice_{i}")
                    user_idx = opts.index(user_val) if user_val in opts else -1
                    if user_idx == q.get("correct_index", 0):
                        score += 1
                
                st.session_state["quiz_score"] = score
                st.session_state["quiz_submitted"] = True
                
                if score == len(quiz_questions):
                    st.balloons()
                st.rerun()
        else:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_score"] = 0
                st.rerun()

    with col_action2:
        if st.button("📖 Read Story Again (Step 2)", use_container_width=True):
            st.session_state["current_step"] = 2
            st.rerun()

    with col_action3:
        if submitted:
            if st.button("📊 View Diagnostic Report (Step 4) ➔", type="primary", use_container_width=True):
                st.session_state["current_step"] = 4
                st.rerun()
        else:
            st.caption("Submit answers above to view parent/teacher diagnostic report.")


# ==============================================================================
# 9. STEP 4: PARENT & TEACHER DIAGNOSTIC REPORT
# ==============================================================================

def render_step_4():
    """Render Step 4: Concept Mastery Score, Learning Milestones, and Discussion Question."""
    story_data = st.session_state.get("story_data")
    if not story_data:
        st.warning("No active session. Please start with Step 1!")
        if st.button("⬅️ Start Adventure"):
            st.session_state["current_step"] = 1
            st.rerun()
        return

    score = st.session_state.get("quiz_score", 0)
    total_q = len(story_data.get("quiz", []))
    total_q = total_q if total_q > 0 else 3
    mastery_pct = int((score / total_q) * 100)

    # Determine badge tier
    if mastery_pct == 100:
        badge = "🏆 Concept Champion"
        badge_desc = "Flawless conceptual retention and real-world application reasoning!"
    elif mastery_pct >= 66:
        badge = "🌟 Skilled Explorer"
        badge_desc = "Solid foundational grasp; minor review recommended for transfer tasks."
    elif mastery_pct >= 33:
        badge = "💡 Apprentice Thinker"
        badge_desc = "Developing intuition; needs reinforced narrative metaphors."
    else:
        badge = "🌱 Budding Inquirer"
        badge_desc = "Initial exposure gained; guided re-reading recommended."

    st.markdown("### 📊 Step 4: Parent & Educator Diagnostic Lab")
    st.markdown("Diagnostic assessment of student comprehension, milestone progression, and actionable conversation prompts.")

    # Diagnostic Hero
    st.markdown(f"""
    <div class="diagnostic-hero">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.8;">STUDENT CONCEPT MASTERY</span>
                <h1 style="margin: 0.2rem 0; font-size: 2.5rem; color: #FFFFFF;">{mastery_pct}% Mastery</h1>
                <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">Score: <strong>{score} / {total_q}</strong> Questions Correct</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 1rem 1.4rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.25);">
                <div style="font-size: 1.3rem; font-weight: 800;">{badge}</div>
                <div style="font-size: 0.85rem; opacity: 0.9; max-width: 250px;">{badge_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Learning Milestones Met Breakdown
    st.markdown("#### 🎯 Learning Milestones Met")
    milestone_cols = st.columns(3)
    
    milestone_names = [
        ("Foundational Recall", "Identifies the core scientific or mathematical definition from memory."),
        ("In-Story Reasoning", "Understands how the concept was applied to solve the narrative problem."),
        ("Real-World Transfer", "Applies the concept to novel everyday scenarios outside the story.")
    ]

    quiz_questions = story_data.get("quiz", [])
    for i, (m_title, m_desc) in enumerate(milestone_names):
        with milestone_cols[i]:
            # Determine if question i was answered correctly
            is_met = False
            if i < len(quiz_questions):
                correct_idx = quiz_questions[i].get("correct_index", 0)
                opts = quiz_questions[i].get("options", [])
                user_choice = st.session_state.get(f"quiz_choice_{i}")
                user_idx = opts.index(user_choice) if user_choice in opts else -1
                is_met = (user_idx == correct_idx)

            status_icon = "✅ MET" if is_met else "⏳ REVIEW NEEDED"
            border_color = "#10B981" if is_met else "#F59E0B"
            bg_color = "#F0FDF4" if is_met else "#FFFBEB"

            st.markdown(f"""
            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.2rem; min-height: 180px;">
                <div style="font-weight: 800; color: #1E293B; font-size: 0.95rem;">{m_title}</div>
                <div style="font-weight: 700; color: {border_color}; font-size: 0.85rem; margin: 0.3rem 0;">{status_icon}</div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.5; margin-top: 0.4rem;">{m_desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Pedagogical Insights & Misconception Alert
    st.markdown("<br>", unsafe_allow_html=True)
    col_diag1, col_diag2 = st.columns(2)

    with col_diag1:
        st.markdown("#### 🔬 Diagnostic Summary")
        st.info(story_data.get("diagnostic_summary", "The student successfully engaged with the primary learning objectives."))

    with col_diag2:
        st.markdown("#### ⚠️ Common Misconceptions Alert")
        st.warning(story_data.get("common_misconceptions", "Children often confuse superficial appearances with underlying mechanisms."))

    # Dinner Table Discussion Question Card
    dinner_q = story_data.get("dinner_table_question", "What did you discover about this concept today?")
    st.markdown(f"""
    <div class="dinner-table-card">
        <div class="dinner-title">🍽️ DINNER-TABLE DISCUSSION QUESTION</div>
        <p style="font-size: 0.9rem; color: #7C2D12; margin: 0.4rem 0 0.8rem 0;">
            Ask your child or student this question casually over dinner or during circle time to reinforce everyday learning:
        </p>
        <div style="font-size: 1.2rem; font-weight: 700; color: #9A3412; font-style: italic; line-height: 1.5;">
            "{dinner_q}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Export Report Button
    st.markdown("---")
    report_text = generate_markdown_report(story_data, score, total_q, mastery_pct, badge)
    
    col_rep1, col_rep2, col_rep3 = st.columns([1, 1, 1])
    with col_rep1:
        st.download_button(
            label="📥 Download Diagnostic Report (.md)",
            data=report_text,
            file_name=f"StoryTeacher_Report_{st.session_state.get('active_topic', 'Concept').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_rep2:
        if st.button("⬅️ Retake Quiz (Step 3)", use_container_width=True):
            st.session_state["current_step"] = 3
            st.rerun()
    with col_rep3:
        if st.button("🚀 Start New Adventure (Step 1)", type="primary", use_container_width=True):
            st.session_state["current_step"] = 1
            st.session_state["story_data"] = None
            st.rerun()


def generate_markdown_report(
    story_data: Dict[str, Any],
    score: int,
    total: int,
    pct: int,
    badge: str,
    topic: Optional[str] = None,
    age: Optional[str] = None,
    protagonist: Optional[str] = None
) -> str:
    """Format an exportable diagnostic report for parents and educators."""
    topic = topic or st.session_state.get("active_topic", "Science Concept")
    age = age or st.session_state.get("active_age", "General")
    protagonist = protagonist or st.session_state.get("active_protagonist", "Student")

    return f"""# StoryTeacher AI - Learning Diagnostic Report
**Student / Hero:** {protagonist}  
**Topic:** {topic}  
**Target Age:** {age}  
**Concept Mastery Score:** {pct}% ({score}/{total} Questions Correct)  
**Achievement Badge:** {badge}  

---

## 1. Story Adventure Summary
- **Title:** {story_data.get('title', '')}
- **The Mission:** {story_data.get('mission_hook', '')}
- **Secret Academic Takeaway:** {story_data.get('science_takeaway', '')}

---

## 2. Comprehension Quiz Breakdown
{chr(10).join(f"- **Q{i+1}:** {q.get('question')} ({q.get('milestone')})" for i, q in enumerate(story_data.get('quiz', [])))}

---

## 3. Pedagogical Observations
- **Diagnostic Summary:** {story_data.get('diagnostic_summary', '')}
- **Common Misconceptions Alert:** {story_data.get('common_misconceptions', '')}

---

## 4. Family Dinner-Table Discussion Prompt
> "{story_data.get('dinner_table_question', '')}"

*Report generated automatically by StoryTeacher AI powered by Google Gemini.*
"""


# ==============================================================================
# 10. MAIN APP CONTROLLER & NAVIGATION
# ==============================================================================

def main():
    """Main application loop."""
    setup_page_config()
    init_session_state()
    render_sidebar()

    # Top Hero Banner
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">✨ EDTECH COGNITIVE NARRATIVE ENGINE</div>
        <h1 class="hero-title">StoryTeacher AI</h1>
        <p class="hero-subtitle">
            Kids find science and maths boring but never get tired of stories. Teach any school concept through an age-adapted story, dynamically test comprehension, and generate a parent/teacher diagnostic report.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Step Tracker / Tab Navigation
    current_step = st.session_state.get("current_step", 1)
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        s1_active = "step-pill-active" if current_step == 1 else "step-pill"
        if st.button("1️⃣ Craft Adventure", use_container_width=True):
            st.session_state["current_step"] = 1
            st.rerun()
    with col_t2:
        s2_active = "step-pill-active" if current_step == 2 else "step-pill"
        if st.button("2️⃣ Read Story", use_container_width=True):
            st.session_state["current_step"] = 2
            st.rerun()
    with col_t3:
        s3_active = "step-pill-active" if current_step == 3 else "step-pill"
        if st.button("3️⃣ Comprehension Quest", use_container_width=True):
            st.session_state["current_step"] = 3
            st.rerun()
    with col_t4:
        s4_active = "step-pill-active" if current_step == 4 else "step-pill"
        if st.button("4️⃣ Diagnostic Report", use_container_width=True):
            st.session_state["current_step"] = 4
            st.rerun()

    st.markdown("<hr style='margin: 0.8rem 0 1.5rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Render Active Step
    if current_step == 1:
        render_step_1()
    elif current_step == 2:
        render_step_2()
    elif current_step == 3:
        render_step_3()
    elif current_step == 4:
        render_step_4()


if __name__ == "__main__":
    main()
