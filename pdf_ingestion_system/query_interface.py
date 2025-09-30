"""
Query Interface - Simple CLI for NVIDIA Course Assistant
Interactive command-line interface for asking questions about courses
"""

import sys
from rag_retriever import CourseRAGRetriever


class QueryInterface:
    """Simple command-line interface for course queries."""

    def __init__(self, db_path: str = "nvidia_courses.db"):
        print("="*60)
        print("NVIDIA Course Assistant")
        print("="*60)
        print("Loading course database and AI model...")
        print()

        try:
            self.retriever = CourseRAGRetriever(db_path)
            print()
            print("Ready to answer your questions!")
            print()
        except Exception as e:
            print(f"Error initializing: {e}")
            sys.exit(1)

    def run(self):
        """Run the interactive query loop."""
        self._print_help()

        while True:
            try:
                # Get user input
                print()
                question = input("Your question: ").strip()

                if not question:
                    continue

                # Handle commands
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                elif question.lower() in ['help', 'h', '?']:
                    self._print_help()
                    continue
                elif question.lower() == 'examples':
                    self._print_examples()
                    continue

                # Answer the question
                print("\nThinking...\n")
                answer = self.retriever.answer_question(question)

                print("-"*60)
                print(answer)
                print("-"*60)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

        # Cleanup
        self.retriever.close()

    def _print_help(self):
        """Print help message."""
        print("="*60)
        print("How to use:")
        print("  - Ask any question about NVIDIA courses")
        print("  - Type 'examples' to see sample questions")
        print("  - Type 'help' for this message")
        print("  - Type 'quit' to exit")
        print("="*60)

    def _print_examples(self):
        """Print example questions."""
        print("\nExample questions you can ask:")
        print()
        print("  1. What prerequisites do I need for Isaac Sim?")
        print("  2. Which courses teach reinforcement learning?")
        print("  3. Show me free beginner courses")
        print("  4. What's the learning path for robotics development?")
        print("  5. Which courses use ROS 2?")
        print("  6. What do I need to learn before MobilityGen?")
        print("  7. Tell me about Isaac Lab training courses")
        print("  8. Which courses are hands-on?")
        print()


def main():
    """Main entry point."""
    # Check for database path argument
    db_path = "nvidia_courses.db"
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    # Run interface
    interface = QueryInterface(db_path)
    interface.run()


if __name__ == "__main__":
    main()