import json

# Load merged catalog
with open('nvidia_courses_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("MERGED CATALOG VERIFICATION")
print("=" * 60)

# Check metadata
print(f"\nMetadata:")
print(f"  Total Courses: {data['metadata']['total_courses']}")
print(f"  LLM Courses: {data['metadata']['llm_courses']}")
print(f"  Robotics Courses: {data['metadata']['robotics_courses']}")

# Verify all courses have domain field
courses_without_domain = []
llm_count = 0
robotics_count = 0
course_ids = set()
duplicates = []

for course in data['courses']:
    course_id = course['id']

    # Check for duplicates
    if course_id in course_ids:
        duplicates.append(course_id)
    course_ids.add(course_id)

    # Check domain field
    if 'domain' not in course:
        courses_without_domain.append(course_id)
    else:
        if course['domain'] == 'LLM':
            llm_count += 1
        elif course['domain'] == 'Robotics':
            robotics_count += 1

print(f"\nActual Course Counts:")
print(f"  Total: {len(data['courses'])}")
print(f"  LLM: {llm_count}")
print(f"  Robotics: {robotics_count}")

# Check learning paths
paths_without_domain = []
for path in data['learning_paths']:
    if 'domain' not in path:
        paths_without_domain.append(path['id'])

print(f"\nLearning Paths:")
print(f"  Total: {len(data['learning_paths'])}")

# Report issues
print(f"\n{'-' * 60}")
print("VALIDATION RESULTS:")
print("-" * 60)

if duplicates:
    print(f"[FAIL] DUPLICATE IDs FOUND: {duplicates}")
else:
    print("[PASS] No duplicate course IDs")

if courses_without_domain:
    print(f"[FAIL] Courses missing domain field: {courses_without_domain}")
else:
    print("[PASS] All courses have domain field")

if paths_without_domain:
    print(f"[FAIL] Learning paths missing domain field: {paths_without_domain}")
else:
    print("[PASS] All learning paths have domain field")

# Sample courses from each domain
print(f"\nSample LLM Courses:")
llm_samples = [c for c in data['courses'] if c.get('domain') == 'LLM'][:3]
for course in llm_samples:
    print(f"  - {course['id']}: {course['title']}")

print(f"\nSample Robotics Courses:")
robotics_samples = [c for c in data['courses'] if c.get('domain') == 'Robotics'][:3]
for course in robotics_samples:
    print(f"  - {course['id']}: {course['title']}")

print("=" * 60)
