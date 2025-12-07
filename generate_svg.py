import base64
import urllib.request
import sys

graph = """
graph TD
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef data fill:#fff3e0,stroke:#ff6f00,stroke-width:2px;
    classDef ai fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    subgraph Frontend
        UI[Dashboard UI]:::frontend
        JS[Logic JS]:::frontend
        Chat[Chat Widget]:::frontend
        UI --> JS
        JS --> API
        Chat --> ChatAPI
    end

    subgraph Backend
        API[API Gateway]:::backend
        ChatAPI[Chat API]:::backend
        Auth[Auth Module]:::backend
        Engine[Competency Engine]:::backend
        Logic[Business Logic]:::backend
        API --> Engine
        ChatAPI --> RAG
        Engine --> Logic
    end

    subgraph AI_Logic
        RAG[RAG System]:::ai
        Paths[Career Paths]:::ai
        Logic --> Paths
        RAG --> VectorDB
    end

    subgraph Data
        DB[(SQLite)]:::data
        JSON[Catalog]:::data
        VectorDB[(FAISS)]:::data
        Auth --> DB
        Engine --> DB
        RAG --> JSON
    end

    JS --> API
    ChatAPI --> Chat
"""

graphbytes = graph.encode("utf-8")
base64_bytes = base64.urlsafe_b64encode(graphbytes)
base64_string = base64_bytes.decode("utf-8")

url = "https://mermaid.ink/svg/" + base64_string

try:
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            with open("architecture_diagram.svg", "wb") as f:
                f.write(response.read())
            print("SVG saved to architecture_diagram.svg")
        else:
            print(f"Failed to fetch SVG. Status code: {response.status}")
except Exception as e:
    print(f"Error: {e}")