"""SCC Analysis module for Boolean Networks."""

import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class SCCAnalyzer:
    """Analyze Strongly Connected Components of Boolean network transition graphs."""
    
    def __init__(self, transitions: Dict[str, List[str]]):
        """
        Initialize analyzer with transition graph.
        
        Args:
            transitions: Dict mapping state -> list of successor states
        """
        self.transitions = transitions
        self._sccs: Optional[List[Set[str]]] = None
        self._state_to_scc: Optional[Dict[str, int]] = None
        self._scc_graph: Optional[Dict[int, Set[int]]] = None
        self._attractors: Optional[List[Set[str]]] = None
        self._transient_sccs: Optional[List[Set[str]]] = None
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'SCCAnalyzer':
        """Load network from Python file and create analyzer."""
        spec = importlib.util.spec_from_file_location("network", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'transitions'):
            raise ValueError(f"No transitions found in {filepath}")
        
        return cls(module.transitions)
    
    def find_sccs(self) -> List[Set[str]]:
        """Find strongly connected components using iterative Tarjan's algorithm."""
        if self._sccs is not None:
            return self._sccs
        
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        for start_node in self.transitions:
            if start_node in index:
                continue
            
            call_stack = [(start_node, None, 0)]
            
            while call_stack:
                node, successor_iter, phase = call_stack.pop()
                
                if phase == 0:
                    index[node] = index_counter[0]
                    lowlinks[node] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(node)
                    on_stack[node] = True
                    successor_iter = iter(self.transitions.get(node, []))
                    call_stack.append((node, successor_iter, 1))
                else:
                    try:
                        successor = next(successor_iter)
                        call_stack.append((node, successor_iter, 1))
                        if successor not in index:
                            call_stack.append((successor, None, 0))
                        elif on_stack.get(successor, False):
                            lowlinks[node] = min(lowlinks[node], index[successor])
                    except StopIteration:
                        if lowlinks[node] == index[node]:
                            scc = set()
                            while True:
                                successor = stack.pop()
                                on_stack[successor] = False
                                scc.add(successor)
                                if successor == node:
                                    break
                            sccs.append(scc)
                        if call_stack:
                            parent_node = call_stack[-1][0]
                            if parent_node in lowlinks:
                                lowlinks[parent_node] = min(lowlinks[parent_node], lowlinks[node])
        
        self._sccs = sccs
        return sccs
    
    def get_state_to_scc_mapping(self) -> Dict[str, int]:
        """Get mapping from state to SCC index."""
        if self._state_to_scc is not None:
            return self._state_to_scc
        
        sccs = self.find_sccs()
        self._state_to_scc = {}
        for i, scc in enumerate(sccs):
            for state in scc:
                self._state_to_scc[state] = i
        
        return self._state_to_scc
    
    def get_scc_graph(self) -> Dict[int, Set[int]]:
        """Build condensation graph (DAG of SCCs)."""
        if self._scc_graph is not None:
            return self._scc_graph
        
        state_to_scc = self.get_state_to_scc_mapping()
        sccs = self.find_sccs()
        
        # Build SCC adjacency
        scc_graph = {i: set() for i in range(len(sccs))}
        
        for state, targets in self.transitions.items():
            src_scc = state_to_scc[state]
            for target in targets:
                dst_scc = state_to_scc[target]
                if src_scc != dst_scc:
                    scc_graph[src_scc].add(dst_scc)
        
        self._scc_graph = scc_graph
        return scc_graph
    
    def identify_attractors(self) -> Tuple[List[Set[str]], List[Set[str]]]:
        """Identify attractors (terminal SCCs) and transient SCCs."""
        if self._attractors is not None and self._transient_sccs is not None:
            return self._attractors, self._transient_sccs
        
        sccs = self.find_sccs()
        scc_graph = self.get_scc_graph()
        
        attractors = []
        transient_sccs = []
        
        for i, scc in enumerate(sccs):
            if len(scc_graph[i]) == 0:  # No outgoing edges
                attractors.append(scc)
            else:
                transient_sccs.append(scc)
        
        self._attractors = attractors
        self._transient_sccs = transient_sccs
        return attractors, transient_sccs
    
    def get_scc_info(self) -> List[Dict]:
        """Get detailed info for each SCC."""
        sccs = self.find_sccs()
        scc_graph = self.get_scc_graph()
        attractors, _ = self.identify_attractors()
        attractor_indices = {id(a) for a in attractors}
        
        info = []
        for i, scc in enumerate(sccs):
            is_attractor = any(id(a) == id(scc) for a in attractors)
            # Check if it's actually a self-loop (fixed point)
            is_fixed_point = (len(scc) == 1 and 
                              list(scc)[0] in self.transitions.get(list(scc)[0], []))
            
            info.append({
                'index': i,
                'size': len(scc),
                'is_attractor': len(scc_graph[i]) == 0,
                'is_fixed_point': is_fixed_point and len(scc_graph[i]) == 0,
                'out_degree': len(scc_graph[i]),
                'states': scc if len(scc) <= 10 else f"{len(scc)} states"
            })
        
        return info
