# In-memory knowledge graph and learning path generator
import json
import networkx as nx
from typing import List, Dict, Any, Set
import os
import sys
import io

# Optional cudf import for GPU acceleration
try:
    import cudf
    IS_CUDA_AVAILABLE = True
except ImportError:
    IS_CUDA_AVAILABLE = False
    
# Add parent directory to path for imports
sys.path.insert(0, str(os.path.dirname(__file__)))
from rag_retriever import CourseRAGRetriever

class LearningPathGenerator:
    """
    Generates a dynamic learning path based on a user's goal.
    """
    def __init__(self, courses_file_path: str):
        self.courses = self._load_courses(courses_file_path)
        self.course_graph = self._build_course_graph()
        # Initialize the RAG retriever to find candidate courses
        self.retriever = CourseRAGRetriever()

    def _load_courses(self, file_path: str) -> Dict[str, Any]:
        """Loads course data from a JSON file using the Hybrid (CPU/GPU) Approach."""
        print("Loading courses data...")

        # 1. CPU: Open the full file safely (Handles the nesting)
        with open(file_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)

        # 2. Extract ONLY the list of courses. Assumes "courses" is a list of dicts.
        courses_list = full_data.get("courses", [])
        if not courses_list:
            return {}

        # Attempt to use GPU (cudf) if available
        if IS_CUDA_AVAILABLE:
            try:
                print("Attempting to load with GPU (cudf)...")
                # 3. Convert that list to a JSON string for cudf
                courses_json_str = json.dumps(courses_list)
                
                # 4. GPU: Now cudf can read it because it's a perfectly flat list
                gdf = cudf.read_json(io.StringIO(courses_json_str))
                print(f"✅ GPU Loaded {len(gdf)} courses!")
                
                # Convert cuDF DataFrame back to the dictionary format the class expects
                courses_records = gdf.to_pandas().to_dict('records')

            except Exception as e:
                print(f"⚠️ GPU (cudf) loading failed: {e}. Falling back to CPU (json).")
                # Fallback to pure python if cudf fails for any reason
                courses_records = courses_list
        else:
            print("GPU (cudf) not available. Loading with CPU (json).")
            courses_records = courses_list

        # 5. Create a dictionary for quick lookup by course ID
        courses_dict = {course['id']: course for course in courses_records}
        return courses_dict

    def _build_course_graph(self) -> nx.DiGraph:
        """Builds a directed graph of courses and their prerequisites using cugraph backend."""
        graph = nx.DiGraph(backend='cugraph')
        for course_id, course_data in self.courses.items():
            # Add each course as a node
            graph.add_node(course_id, **course_data)
            
            # Add edges for prerequisites
            for prerequisite_id in course_data.get('prerequisites', []):
                if prerequisite_id in self.courses:
                    # Edge from prerequisite to the course that requires it
                    graph.add_edge(prerequisite_id, course_id)
        return graph

    def generate_path(self, user_goal: str) -> List[Dict[str, Any]]:
        """
        Generates a learning path for a given user goal.
        
        This implementation includes:
        1. Semantic search for candidate courses using RAG.
        2. Graph expansion to include all prerequisites.
        3. Topological sort to create a valid learning order.
        """
        # Step 1: Vector Search (Semantic) to get initial candidates
        candidate_courses = self.retriever.get_candidate_courses(user_goal)

        if not candidate_courses:
            return []

        # Step 2: Graph Expansion (Structural) to find all prerequisites
        all_courses_in_path = set(candidate_courses)
        for course_id in candidate_courses:
            try:
                # Use nx.ancestors to find all prerequisite courses in the graph
                ancestors = nx.ancestors(self.course_graph, course_id)
                all_courses_in_path.update(ancestors)
            except nx.NetworkXError:
                # This can happen if a course from the semantic search isn't in our graph
                # (e.g., if the JSON and DB are out of sync). We'll just ignore it.
                pass

        # Create a subgraph of the courses we care about
        subgraph = self.course_graph.subgraph(all_courses_in_path)
        
        # Step 3: Topological Sort to get the correct learning order
        try:
            sorted_course_ids = list(nx.topological_sort(subgraph))
        except nx.NetworkXUnfeasible:
            # This happens if there's a cycle in the prerequisites, which indicates a data issue.
            # For now, we'll return an empty list. A more robust solution would log this error.
            return []

        # Get the full course data for the sorted IDs
        learning_path = [self.courses[course_id] for course_id in sorted_course_ids if course_id in self.courses]
        
        return learning_path

    def get_popular_courses(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Calculates PageRank on the course graph to identify popular courses
        and returns the top N most popular courses.
        Leverages GPU acceleration via cugraph backend.
        """
        if not self.course_graph:
            return []

        print(f"Calculating PageRank for {len(self.course_graph.nodes)} courses...")
        # nx.pagerank will automatically use cugraph if backend is set
        pagerank_scores = nx.pagerank(self.course_graph, alpha=0.85)

        # Sort courses by PageRank score in descending order
        sorted_courses = sorted(pagerank_scores.items(), key=lambda item: item[1], reverse=True)

        popular_courses_info = []
        for course_id, score in sorted_courses[:top_n]:
            if course_id in self.courses:
                course_data = self.courses[course_id].copy()
                course_data['popularity_score'] = score
                popular_courses_info.append(course_data)
        
        return popular_courses_info

if __name__ == '__main__':
    # Example usage for testing
    # Note: This will initialize the RAG retriever, which can take a moment.
    generator = LearningPathGenerator(courses_file_path='../nvidia_courses_merged.json')
    
    # Test path generation with a real goal
    test_goal = "I want to learn about robotics and how to use Isaac Sim."
    print(f"--- Generating Learning Path for goal: '{test_goal}' ---")
    
    path = generator.generate_path(test_goal)
    
    print("\n--- Generated Learning Path ---")
    if path:
        for i, course in enumerate(path):
            print(f"{i+1}. {course['title']} (Level: {course['level']})")
    else:
        print("Could not generate a learning path for the given goal.")

    # Test popular courses feature
    print("\n" + "="*60)
    print("TOP POPULAR COURSES (GPU-accelerated PageRank)")
    print("="*60)
    popular_courses = generator.get_popular_courses(top_n=3)
    if popular_courses:
        for i, course in enumerate(popular_courses):
            print(f"{i+1}. {course['title']} (Score: {course['popularity_score']:.4f})")
    else:
        print("Could not retrieve popular courses.")

