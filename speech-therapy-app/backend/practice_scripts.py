"""
Practice scripts for speech therapy sessions
Organized by difficulty level and focus area
"""

PRACTICE_SCRIPTS = {
    "beginner": {
        "clarity": [
            "Hello, my name is speaking clearly today.",
            "The quick brown fox jumps over the lazy dog.",
            "Peter Piper picked a peck of pickled peppers.",
            "She sells seashells by the seashore.",
            "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
        ],
        "pace": [
            "I am practicing speaking at a steady pace, not too fast and not too slow.",
            "Taking time to breathe between sentences helps me speak more clearly.",
            "Slow and steady wins the race when it comes to clear communication.",
            "I will pause naturally between thoughts to give listeners time to process.",
            "Speaking at the right speed makes it easier for others to understand me.",
        ],
        "volume": [
            "I am projecting my voice with confidence and clarity.",
            "Speaking loudly enough ensures that everyone can hear my message.",
            "Good volume control is essential for effective communication.",
            "I will speak up so that my voice reaches across the room.",
            "Clear, confident volume makes a strong impression on listeners.",
        ],
    },
    "intermediate": {
        "articulation": [
            "The sixth sick sheik's sixth sheep's sick. This tongue twister helps with articulation.",
            "Red lorry, yellow lorry. Red lorry, yellow lorry. Repeating this improves pronunciation.",
            "Unique New York, you need New York, you know you need unique New York.",
            "Irish wristwatch, Swiss wristwatch. These challenging words test my clarity.",
            "Three free throws. Fred threw three free throws. Practicing difficult sounds helps.",
        ],
        "professional": [
            "Good morning everyone, I'd like to present our quarterly results and discuss our future strategy.",
            "Thank you for taking the time to meet with me today. I appreciate your consideration.",
            "I am confident in my ability to communicate effectively in professional settings.",
            "Our team has worked diligently to deliver exceptional results for our clients.",
            "I look forward to collaborating with you on this exciting new project.",
        ],
        "storytelling": [
            "Once upon a time, there was a young person who decided to improve their speaking skills. They practiced every day and saw remarkable progress.",
            "The key to effective communication is not just what you say, but how you say it. Clarity, confidence, and connection matter most.",
            "I remember the first time I gave a presentation. My hands were shaking and my voice was quiet. Now, I speak with confidence.",
            "Communication is a skill that improves with practice. Every session brings me closer to my goals.",
            "The best speakers aren't born, they're made through dedication and consistent practice.",
        ],
    },
    "advanced": {
        "complex": [
            "Interdisciplinary collaboration facilitates innovative solutions to multifaceted challenges in contemporary organizational environments.",
            "The implementation of comprehensive strategies requires meticulous planning and stakeholder engagement across all operational levels.",
            "Technological advancement has fundamentally transformed the methodologies through which we analyze and interpret complex data sets.",
            "Effective leadership necessitates the cultivation of emotional intelligence alongside strategic thinking capabilities.",
            "The intersection of artificial intelligence and healthcare presents unprecedented opportunities for improving patient outcomes.",
        ],
        "persuasive": [
            "I firmly believe that investing in continuous learning is the most valuable decision we can make for our future success.",
            "The evidence clearly demonstrates that our proposed approach will yield significant benefits for all stakeholders involved.",
            "Consider the long-term implications of this decision. The choices we make today will shape our tomorrow.",
            "I urge you to examine the data objectively. The facts speak for themselves and support this course of action.",
            "Together, we have the opportunity to create meaningful change that will impact generations to come.",
        ],
        "technical": [
            "The algorithm implements a recursive backtracking approach to solve the constraint satisfaction problem efficiently.",
            "Our neural network architecture utilizes convolutional layers with batch normalization and dropout regularization.",
            "The distributed system employs consistent hashing to ensure optimal load balancing across all server nodes.",
            "We've optimized the database schema using denormalization techniques to reduce query latency significantly.",
            "The microservices architecture facilitates independent deployment and scalability of individual components.",
        ],
    },
}

def get_random_script(difficulty="beginner", category=None):
    """
    Get a random practice script
    
    Args:
        difficulty: "beginner", "intermediate", or "advanced"
        category: Specific category within difficulty, or None for random
        
    Returns:
        dict with script text, difficulty, and category
    """
    import random
    
    if difficulty not in PRACTICE_SCRIPTS:
        difficulty = "beginner"
    
    difficulty_scripts = PRACTICE_SCRIPTS[difficulty]
    
    if category and category in difficulty_scripts:
        scripts = difficulty_scripts[category]
        selected_category = category
    else:
        # Random category
        selected_category = random.choice(list(difficulty_scripts.keys()))
        scripts = difficulty_scripts[selected_category]
    
    script_text = random.choice(scripts)
    
    return {
        "text": script_text,
        "difficulty": difficulty,
        "category": selected_category,
        "word_count": len(script_text.split())
    }

def get_all_scripts():
    """Get all available scripts organized by difficulty and category"""
    return PRACTICE_SCRIPTS

def get_categories(difficulty="beginner"):
    """Get available categories for a difficulty level"""
    if difficulty in PRACTICE_SCRIPTS:
        return list(PRACTICE_SCRIPTS[difficulty].keys())
    return []