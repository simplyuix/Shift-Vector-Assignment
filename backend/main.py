from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List, Dict, Any, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeData(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class PipelineRequest(BaseModel):
    nodes: List[NodeData]
    edges: List[EdgeData]

class PipelineResponse(BaseModel):
    num_nodes: int
    num_edges: int
    is_dag: bool

def is_directed_acyclic_graph(nodes: List[NodeData], edges: List[EdgeData]) -> bool:
    """
    Check if the nodes and edges form a directed acyclic graph (DAG).
    Uses DFS to detect cycles.
    """
    if not nodes:
        return True
    
    
    graph = {}
    node_ids = set()
    
    
    for node in nodes:
        graph[node.id] = []
        node_ids.add(node.id)
    
    
    for edge in edges:
        if edge.source in graph and edge.target in node_ids:  
            graph[edge.source].append(edge.target)
    
    
    color = {node_id: 0 for node_id in node_ids}
    
    def has_cycle_dfs(node):
        if color[node] == 1:  
            return True
        if color[node] == 2:  
            return False
        
        color[node] = 1  
        
        for neighbor in graph[node]:
            if has_cycle_dfs(neighbor):  
                return True
        
        color[node] = 2  
        return False
    
   
    for node_id in node_ids:
        if color[node_id] == 0:
            if has_cycle_dfs(node_id):
                return False
    
    return True

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse', response_model=PipelineResponse)
def parse_pipeline(pipeline: PipelineRequest):
    """
    Parse a pipeline and return node count, edge count, and DAG validation.
    """
    try:
        num_nodes = len(pipeline.nodes)
        num_edges = len(pipeline.edges)
        is_dag = is_directed_acyclic_graph(pipeline.nodes, pipeline.edges)
        
        return PipelineResponse(
            num_nodes=num_nodes,
            num_edges=num_edges,
            is_dag=is_dag
        )
        
    except Exception as e:
        print(f"Error processing pipeline: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"Error processing pipeline: {str(e)}")