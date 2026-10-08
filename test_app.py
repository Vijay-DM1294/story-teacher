import unittest
from app import (
    StoryTeacherResponse,
    clean_json_string,
    build_system_prompt,
    generate_markdown_report,
    CURATED_DEMOS
)

class TestStoryTeacher(unittest.TestCase):
    def test_curated_demos_validation(self):
        """Ensure all curated demos strictly conform to StoryTeacherResponse schema."""
        for key, demo in CURATED_DEMOS.items():
            data = demo["data"]
            validated = StoryTeacherResponse(**data)
            self.assertIsNotNone(validated.title)
            self.assertIsNotNone(validated.mission_hook)
            self.assertGreater(len(validated.story_content), 100)
            self.assertEqual(len(validated.quiz), 3)
            for q in validated.quiz:
                self.assertEqual(len(q.options), 4)
                self.assertIn(q.correct_index, [0, 1, 2, 3])

    def test_clean_json_string(self):
        raw = '```json\n{"hello": "world"}\n```'
        cleaned = clean_json_string(raw)
        self.assertEqual(cleaned, '{"hello": "world"}')

    def test_build_system_prompt(self):
        p_5_7 = build_system_prompt("Ages 5–7 (Early Explorers 🌱)")
        self.assertIn("Early Explorers", p_5_7)
        self.assertIn("Lexile 200L-400L", p_5_7)

        p_8_10 = build_system_prompt("Ages 8–10 (Adventurers 🔍)")
        self.assertIn("Adventurers", p_8_10)

        p_11_13 = build_system_prompt("Ages 11–13 (Trailblazers 🚀)")
        self.assertIn("Trailblazers", p_11_13)

    def test_markdown_report(self):
        demo = CURATED_DEMOS["Ages 5–7 (Early Explorers 🌱) - Photosynthesis"]["data"]
        report = generate_markdown_report(
            demo, 3, 3, 100, "Concept Champion",
            topic="Photosynthesis", age="Ages 5-7", protagonist="Pip"
        )
        self.assertIn("Concept Mastery Score", report)
        self.assertIn("Photosynthesis", report)
        self.assertIn("Dinner-Table Discussion", report)

if __name__ == "__main__":
    unittest.main()
