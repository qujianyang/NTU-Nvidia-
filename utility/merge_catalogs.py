"""
Merge NVIDIA LLM and Robotics course catalogs into a single unified catalog.
Adds 'domain' field to each course for filtering.
"""
import json
from pathlib import Path
from datetime import datetime


def merge_catalogs(llm_path, robotics_path, output_path):
    """Merge two course catalogs with domain identification."""

    print("=" * 60)
    print("NVIDIA Course Catalog Merger")
    print("=" * 60)

    # Load LLM catalog
    print(f"\nLoading LLM catalog: {llm_path}")
    with open(llm_path, 'r', encoding='utf-8') as f:
        llm_data = json.load(f)

    # Load Robotics catalog
    print(f"Loading Robotics catalog: {robotics_path}")
    with open(robotics_path, 'r', encoding='utf-8') as f:
        robotics_data = json.load(f)

    # Create merged catalog
    merged = {
        "metadata": {
            "source": "Merged LLM and Robotics Catalogs",
            "catalog_name": "NVIDIA Complete Learning Catalog - AI, LLM, and Robotics",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "total_courses": len(llm_data['courses']) + len(robotics_data['courses']),
            "llm_courses": len(llm_data['courses']),
            "robotics_courses": len(robotics_data['courses']),
            "notes": "Unified catalog combining Generative AI/LLM and Robotics learning paths"
        },
        "learning_paths": [],
        "courses": []
    }

    # Add domain identifier to LLM learning paths
    print("\nProcessing LLM learning paths...")
    for path in llm_data.get('learning_paths', []):
        path_copy = path.copy()
        path_copy['domain'] = 'LLM'
        merged['learning_paths'].append(path_copy)

    # Add domain identifier to Robotics learning paths
    print("Processing Robotics learning paths...")
    for path in robotics_data.get('learning_paths', []):
        path_copy = path.copy()
        path_copy['domain'] = 'Robotics'
        merged['learning_paths'].append(path_copy)

    # Add domain identifier to LLM courses
    print("\nProcessing LLM courses...")
    for course in llm_data.get('courses', []):
        course_copy = course.copy()
        course_copy['domain'] = 'LLM'
        merged['courses'].append(course_copy)

    # Add domain identifier to Robotics courses
    print("Processing Robotics courses...")
    for course in robotics_data.get('courses', []):
        course_copy = course.copy()
        course_copy['domain'] = 'Robotics'
        merged['courses'].append(course_copy)

    # Save merged catalog
    print(f"\nSaving merged catalog: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 60)
    print("MERGE COMPLETE!")
    print("=" * 60)
    print(f"\nTotal Learning Paths: {len(merged['learning_paths'])}")
    print(f"  - LLM Paths: {len([p for p in merged['learning_paths'] if p['domain'] == 'LLM'])}")
    print(f"  - Robotics Paths: {len([p for p in merged['learning_paths'] if p['domain'] == 'Robotics'])}")
    print(f"\nTotal Courses: {merged['metadata']['total_courses']}")
    print(f"  - LLM Courses: {merged['metadata']['llm_courses']}")
    print(f"  - Robotics Courses: {merged['metadata']['robotics_courses']}")
    print(f"\nOutput file: {output_path}")
    print("=" * 60)

    return merged


if __name__ == "__main__":
    # Define paths
    base_dir = Path(__file__).parent
    llm_path = base_dir / "nvidia_courses_template.json"
    robotics_path = base_dir / "nvidia_courses_robotics_BACKUP_2025-10-28.json"
    output_path = base_dir / "nvidia_courses_merged.json"

    # Check if files exist
    if not llm_path.exists():
        print(f"Error: LLM catalog not found: {llm_path}")
        exit(1)

    if not robotics_path.exists():
        print(f"Error: Robotics catalog not found: {robotics_path}")
        exit(1)

    # Merge catalogs
    merge_catalogs(str(llm_path), str(robotics_path), str(output_path))
