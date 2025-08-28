"""
Manim API Documentation System for Animathic
Provides comprehensive access to Manim CE API docs, guides, and source code
"""

import os
import json
import logging
import requests
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import time
from urllib.parse import urljoin, urlparse
import html
from bs4 import BeautifulSoup

# Import embedding and vector search libraries
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    EMBEDDING_AVAILABLE = True
    FAISS_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    FAISS_AVAILABLE = False
    # logger not defined yet, so we'll handle this in the class initialization

# Try scikit-learn fallback
try:
    from sklearn.neighbors import NearestNeighbors
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ManimSymbol:
    """Represents a Manim symbol (class, function, constant)"""
    name: str
    symbol_type: str  # 'class', 'function', 'constant', 'method'
    canonical_path: str  # e.g., 'manim.mobject.geometry.line.Line'
    signature: str  # Constructor signature or function signature
    defaults: Dict[str, Any]  # Default parameter values
    doc_url: str  # URL to documentation
    description: str  # Brief description
    examples: List[str]  # Code examples
    source_code: str  # Relevant source code snippet
    version: str  # Manim version
    tags: List[str]  # Searchable tags
    dependencies: List[str]  # Required imports


@dataclass
class ManimDocResult:
    """Result from manim_doc lookup"""
    symbol: ManimSymbol
    relevance_score: float
    source: str  # 'api_docs', 'guides', 'source_code'


class ManimAPIDocumentationSystem:
    """Comprehensive system for managing and retrieving Manim API documentation"""
    
    def __init__(self, cache_dir: str = None):
        """Initialize the Manim API documentation system"""
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), 'manim_docs_cache')
        self.docs_dir = os.path.join(self.cache_dir, 'docs')
        self.index_dir = os.path.join(self.cache_dir, 'index')
        
        # Create directories
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
        
        # Initialize components
        self.symbol_registry: Dict[str, ManimSymbol] = {}
        self.embedding_model = None
        self.vector_index = None
        self.embedding_available = EMBEDDING_AVAILABLE
        
        # Manim documentation sources
        self.doc_sources = {
            'api_docs': 'https://docs.manim.community/en/stable/reference.html',
            'guides': 'https://docs.manim.community/en/stable/guides/',
            'examples': 'https://docs.manim.community/en/stable/examples/',
            'source_code': 'https://github.com/ManimCommunity/manim'
        }
        
        # Initialize embedding system if available
        if self.embedding_available:
            self._initialize_embedding_system()
        
        # Load existing registry or build new one
        self._load_or_build_registry()
    
    def _initialize_embedding_system(self):
        """Initialize the embedding model and vector index"""
        if not self.embedding_available:
            logger.warning("Sentence transformers or FAISS not available. Install with: pip install sentence-transformers faiss-cpu")
            return
            
        try:
            logger.info("Initializing embedding system with BAAI bge-small-en-384")
            self.embedding_model = SentenceTransformer('BAAI/bge-small-en-384')
            
            # Create FAISS index for vector search
            self.vector_index = faiss.IndexFlatIP(384)  # Inner product for cosine similarity
            
            logger.info("Embedding system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding system: {e}")
            self.embedding_available = False
    
    def _load_or_build_registry(self):
        """Load existing symbol registry or build a new one"""
        registry_file = os.path.join(self.index_dir, 'symbol_registry.json')
        
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.symbol_registry = {
                        name: ManimSymbol(**symbol_data) 
                        for name, symbol_data in data.items()
                    }
                logger.info(f"Loaded {len(self.symbol_registry)} symbols from cache")
                return
            except Exception as e:
                logger.warning(f"Failed to load cached registry: {e}")
        
        # Build new registry
        logger.info("Building new Manim symbol registry...")
        self._build_symbol_registry()
    
    def _build_symbol_registry(self):
        """Build the complete symbol registry from Manim documentation and source"""
        try:
            # Scrape API documentation
            self._scrape_api_documentation()
            
            # Scrape guides and examples
            self._scrape_guides_and_examples()
            
            # Extract source code information
            self._extract_source_code_info()
            
            # Build vector index
            if self.embedding_available:
                self._build_vector_index()
            
            # Save registry
            self._save_registry()
            
            logger.info(f"Built symbol registry with {len(self.symbol_registry)} symbols")
            
        except Exception as e:
            logger.error(f"Failed to build symbol registry: {e}")
            raise
    
    def _scrape_api_documentation(self):
        """Scrape Manim API documentation for symbols"""
        logger.info("Scraping Manim API documentation...")
        
        try:
            # Scrape main API reference
            response = requests.get(self.doc_sources['api_docs'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all API reference links
            api_links = soup.find_all('a', href=re.compile(r'reference/.*\.html'))
            
            for link in api_links[:50]:  # Limit to first 50 for initial build
                try:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.doc_sources['api_docs'], href)
                        self._scrape_api_page(full_url)
                        time.sleep(0.1)  # Be respectful
                except Exception as e:
                    logger.debug(f"Failed to scrape {href}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to scrape API documentation: {e}")
    
    def _scrape_api_page(self, url: str):
        """Scrape a single API documentation page"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page title
            title = soup.find('title')
            page_title = title.get_text() if title else "Unknown"
            
            # Find all class and function definitions
            for section in soup.find_all(['div', 'section'], class_=re.compile(r'(class|function|method)')):
                self._extract_symbol_from_section(section, url, page_title)
                
        except Exception as e:
            logger.debug(f"Failed to scrape API page {url}: {e}")
    
    def _extract_symbol_from_section(self, section, url: str, page_title: str):
        """Extract symbol information from a documentation section"""
        try:
            # Find symbol name
            name_elem = section.find(['h1', 'h2', 'h3', 'h4'])
            if not name_elem:
                return
            
            symbol_name = name_elem.get_text().strip()
            
            # Determine symbol type
            symbol_type = 'unknown'
            if 'class' in section.get('class', []):
                symbol_type = 'class'
            elif 'function' in section.get('class', []):
                symbol_type = 'function'
            elif 'method' in section.get('class', []):
                symbol_type = 'method'
            
            # Extract description
            desc_elem = section.find(['p', 'div'], class_='description')
            description = desc_elem.get_text().strip() if desc_elem else ""
            
            # Extract signature if available
            sig_elem = section.find(['code', 'pre'])
            signature = sig_elem.get_text().strip() if sig_elem else ""
            
            # Create symbol
            symbol = ManimSymbol(
                name=symbol_name,
                symbol_type=symbol_type,
                canonical_path=f"manim.{symbol_name.lower()}",
                signature=signature,
                defaults={},
                doc_url=url,
                description=description,
                examples=[],
                source_code="",
                version="0.19.0",  # Current Manim version
                tags=[symbol_type, page_title.lower()],
                dependencies=[]
            )
            
            # Add to registry
            self.symbol_registry[symbol_name] = symbol
            
        except Exception as e:
            logger.debug(f"Failed to extract symbol from section: {e}")
    
    def _scrape_guides_and_examples(self):
        """Scrape guides and examples for additional context"""
        logger.info("Scraping guides and examples...")
        
        # This would involve scraping the guides and examples pages
        # For now, we'll add some common Manim symbols manually
        self._add_common_manim_symbols()
    
    def _add_common_manim_symbols(self):
        """Add commonly used Manim symbols to the registry"""
        common_symbols = [
            # Basic shapes
            ManimSymbol(
                name="Circle",
                symbol_type="class",
                canonical_path="manim.mobject.geometry.line.Circle",
                signature="Circle(radius=1, color=WHITE, fill_opacity=0, stroke_width=4)",
                defaults={"radius": 1, "color": "WHITE", "fill_opacity": 0, "stroke_width": 4},
                doc_url="https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Circle.html",
                description="A circle geometric shape",
                examples=["Circle(radius=2, color=RED)", "Circle().scale(0.5)"],
                source_code="",
                version="0.19.0",
                tags=["shape", "geometry", "circle", "basic"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="Square",
                symbol_type="class",
                canonical_path="manim.mobject.geometry.line.Square",
                signature="Square(side_length=2, color=WHITE, fill_opacity=0, stroke_width=4)",
                defaults={"side_length": 2, "color": "WHITE", "fill_opacity": 0, "stroke_width": 4},
                doc_url="https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Square.html",
                description="A square geometric shape",
                examples=["Square(side_length=3, color=BLUE)", "Square().rotate(PI/4)"],
                source_code="",
                version="0.19.0",
                tags=["shape", "geometry", "square", "basic"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="Rectangle",
                symbol_type="class",
                canonical_path="manim.mobject.geometry.line.Rectangle",
                signature="Rectangle(width=4, height=2, color=WHITE, fill_opacity=0, stroke_width=4)",
                defaults={"width": 4, "height": 2, "color": "WHITE", "fill_opacity": 0, "stroke_width": 4},
                doc_url="https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Rectangle.html",
                description="A rectangle geometric shape",
                examples=["Rectangle(width=6, height=3, color=GREEN)", "Rectangle().scale(0.8)"],
                source_code="",
                version="0.19.0",
                tags=["shape", "geometry", "rectangle", "basic"],
                dependencies=["manim"]
            ),
            # Animations
            ManimSymbol(
                name="Create",
                symbol_type="class",
                canonical_path="manim.animation.creation.Create",
                signature="Create(mobject, lag_ratio=0, run_time=1.0)",
                defaults={"lag_ratio": 0, "run_time": 1.0},
                doc_url="https://docs.manim.community/en/stable/reference/manim.animation.creation.Create.html",
                description="Animation that creates a mobject by drawing it",
                examples=["Create(circle)", "Create(square, run_time=2.0)"],
                source_code="",
                version="0.19.0",
                tags=["animation", "creation", "drawing"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="FadeIn",
                symbol_type="class",
                canonical_path="manim.animation.fading.FadeIn",
                signature="FadeIn(mobject, lag_ratio=0, run_time=1.0, shift=ORIGIN, scale=1)",
                defaults={"lag_ratio": 0, "run_time": 1.0, "shift": "ORIGIN", "scale": 1},
                doc_url="https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeIn.html",
                description="Animation that fades in a mobject",
                examples=["FadeIn(circle)", "FadeIn(square, scale=1.5)"],
                source_code="",
                version="0.19.0",
                tags=["animation", "fading", "appear"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="FadeOut",
                symbol_type="class",
                canonical_path="manim.animation.fading.FadeOut",
                signature="FadeOut(mobject, lag_ratio=0, run_time=1.0, shift=ORIGIN, scale=1)",
                defaults={"lag_ratio": 0, "run_time": 1.0, "shift": "ORIGIN", "scale": 1},
                doc_url="https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeOut.html",
                description="Animation that fades out a mobject",
                examples=["FadeOut(circle)", "FadeOut(square, scale=0.5)"],
                source_code="",
                version="0.19.0",
                tags=["animation", "fading", "disappear"],
                dependencies=["manim"]
            ),
            # Colors
            ManimSymbol(
                name="RED",
                symbol_type="constant",
                canonical_path="manim.constants.RED",
                signature="RED",
                defaults={},
                doc_url="https://docs.manim.community/en/stable/reference/manim.constants.html",
                description="Red color constant",
                examples=["Circle(color=RED)", "Square().set_color(RED)"],
                source_code="",
                version="0.19.0",
                tags=["color", "constant", "red"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="BLUE",
                symbol_type="constant",
                canonical_path="manim.constants.BLUE",
                signature="BLUE",
                defaults={},
                doc_url="https://docs.manim.community/en/stable/reference/manim.constants.html",
                description="Blue color constant",
                examples=["Circle(color=BLUE)", "Square().set_color(BLUE)"],
                source_code="",
                version="0.19.0",
                tags=["color", "constant", "blue"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="GREEN",
                symbol_type="constant",
                canonical_path="manim.constants.GREEN",
                signature="GREEN",
                defaults={},
                doc_url="https://docs.manim.community/en/stable/reference/manim.constants.html",
                description="Green color constant",
                examples=["Circle(color=GREEN)", "Square().set_color(GREEN)"],
                source_code="",
                version="0.19.0",
                tags=["color", "constant", "green"],
                dependencies=["manim"]
            ),
            # Scenes
            ManimSymbol(
                name="Scene",
                symbol_type="class",
                canonical_path="manim.scene.scene.Scene",
                signature="Scene(camera=None, always_update_mobjects=False, random_seed=None)",
                defaults={"camera": None, "always_update_mobjects": False, "random_seed": None},
                doc_url="https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html",
                description="Base scene class for Manim animations",
                examples=["class MyScene(Scene):", "def construct(self):"],
                source_code="",
                version="0.19.0",
                tags=["scene", "base", "animation"],
                dependencies=["manim"]
            ),
            ManimSymbol(
                name="MovingCameraScene",
                symbol_type="class",
                canonical_path="manim.scene.moving_camera_scene.MovingCameraScene",
                signature="MovingCameraScene(camera=None, always_update_mobjects=False, random_seed=None)",
                defaults={"camera": None, "always_update_mobjects": False, "random_seed": None},
                doc_url="https://docs.manim.community/en/stable/reference/manim.scene.moving_camera_scene.MovingCameraScene.html",
                description="Scene with a moving camera for dynamic perspectives",
                examples=["class MyScene(MovingCameraScene):", "self.camera.frame.move_to(point)"],
                source_code="",
                version="0.19.0",
                tags=["scene", "camera", "moving", "dynamic"],
                dependencies=["manim"]
            )
        ]
        
        for symbol in common_symbols:
            self.symbol_registry[symbol.name] = symbol
    
    def _extract_source_code_info(self):
        """Extract source code information for symbols"""
        # This would involve analyzing Manim source code
        # For now, we'll use the basic information we have
        pass
    
    def _build_vector_index(self):
        """Build vector index for semantic search"""
        if not self.embedding_available:
            return
        
        try:
            if FAISS_AVAILABLE:
                # Use FAISS for vector search
                texts = []
                for symbol in self.symbol_registry.values():
                    # Combine name, description, tags, and examples for better semantic search
                    text = f"{symbol.name} {symbol.description} {' '.join(symbol.tags)} {' '.join(symbol.examples)}"
                    texts.append(text)
                
                embeddings = self.embedding_model.encode(texts, normalize_embeddings=True)
                dimension = embeddings.shape[1]
                self.vector_index = faiss.IndexFlatL2(dimension)
                self.vector_index.add(embeddings.astype('float32'))
                print(f"Built FAISS index with {len(embeddings)} vectors")
            elif SKLEARN_AVAILABLE:
                # Use scikit-learn TF-IDF + nearest neighbors as fallback
                descriptions = [symbol.description for symbol in self.symbol_registry.values()]
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
                tfidf_matrix = self.vectorizer.fit_transform(descriptions)
                self.nn_index = NearestNeighbors(n_neighbors=5, metric='cosine')
                self.nn_index.fit(tfidf_matrix)
                print(f"Built scikit-learn index with {len(descriptions)} documents")
            else:
                print("No vector indexing available - using basic search only")
        except Exception as e:
            print(f"Error building vector index: {e}")
            self.embedding_available = False
    
    def _save_registry(self):
        """Save the symbol registry to disk"""
        try:
            registry_file = os.path.join(self.index_dir, 'symbol_registry.json')
            
            # Convert symbols to dictionaries
            registry_data = {
                name: asdict(symbol) 
                for name, symbol in self.symbol_registry.items()
            }
            
            with open(registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            logger.info(f"Saved symbol registry to {registry_file}")
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def manim_doc(self, symbol_or_query: str) -> Optional[ManimDocResult]:
        """Main function to retrieve Manim documentation for a symbol or query"""
        try:
            # First, try exact symbol match
            if symbol_or_query in self.symbol_registry:
                symbol = self.symbol_registry[symbol_or_query]
                return ManimDocResult(
                    symbol=symbol,
                    relevance_score=1.0,
                    source='exact_match'
                )
            
            # Try partial matches
            partial_matches = []
            for name, symbol in self.symbol_registry.items():
                if symbol_or_query.lower() in name.lower():
                    partial_matches.append((symbol, 0.8))
                elif any(tag.lower() in symbol_or_query.lower() for tag in symbol.tags):
                    partial_matches.append((symbol, 0.6))
            
            if partial_matches:
                # Return best partial match
                best_match = max(partial_matches, key=lambda x: x[1])
                return ManimDocResult(
                    symbol=best_match[0],
                    relevance_score=best_match[1],
                    source='partial_match'
                )
            
            # Try semantic search if available
            if self.embedding_available and self.vector_index is not None:
                return self._semantic_search(symbol_or_query)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in manim_doc: {e}")
            return None
    
    def _semantic_search(self, query: str) -> Optional[ManimDocResult]:
        """Perform semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
            
            # Search in vector index
            scores, indices = self.vector_index.search(query_embedding.astype('float32'), k=1)
            
            if len(indices[0]) > 0 and scores[0][0] > 0.3:  # Relevance threshold
                symbol_names = list(self.symbol_registry.keys())
                symbol_name = symbol_names[indices[0][0]]
                symbol = self.symbol_registry[symbol_name]
                
                return ManimDocResult(
                    symbol=symbol,
                    relevance_score=float(scores[0][0]),
                    source='semantic_search'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return None
    
    def get_symbol_info(self, symbol_name: str) -> Optional[ManimSymbol]:
        """Get detailed information about a specific symbol"""
        return self.symbol_registry.get(symbol_name)
    
    def search_symbols(self, query: str, limit: int = 10) -> List[ManimDocResult]:
        """Search for symbols matching a query"""
        results = []
        
        # Exact and partial matches
        for name, symbol in self.symbol_registry.items():
            score = 0.0
            
            if query.lower() == name.lower():
                score = 1.0
            elif query.lower() in name.lower():
                score = 0.8
            elif any(tag.lower() in query.lower() for tag in symbol.tags):
                score = 0.6
            elif query.lower() in symbol.description.lower():
                score = 0.4
            
            if score > 0:
                results.append(ManimDocResult(
                    symbol=symbol,
                    relevance_score=score,
                    source='text_search'
                ))
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def get_all_symbols(self) -> List[ManimSymbol]:
        """Get all symbols in the registry"""
        return list(self.symbol_registry.values())
    
    def get_symbols_by_type(self, symbol_type: str) -> List[ManimSymbol]:
        """Get all symbols of a specific type"""
        return [symbol for symbol in self.symbol_registry.values() if symbol.symbol_type == symbol_type]
    
    def validate_symbol_usage(self, symbol_name: str, **kwargs) -> Tuple[bool, List[str]]:
        """Validate that a symbol is used with correct parameters"""
        if symbol_name not in self.symbol_registry:
            return False, [f"Unknown symbol: {symbol_name}"]
        
        symbol = self.symbol_registry[symbol_name]
        errors = []
        
        # Check if required parameters are provided
        # This is a simplified validation - could be enhanced with more sophisticated parsing
        if symbol.signature:
            # Extract parameter names from signature
            param_match = re.search(r'\((.*?)\)', symbol.signature)
            if param_match:
                params_str = param_match.group(1)
                # Simple parameter extraction - could be enhanced
                if '=' not in params_str and params_str.strip():
                    # No default values, all params required
                    required_params = [p.strip() for p in params_str.split(',') if p.strip()]
                    for param in required_params:
                        if param not in kwargs:
                            errors.append(f"Missing required parameter: {param}")
        
        return len(errors) == 0, errors
    
    def refresh_documentation(self):
        """Refresh the documentation by rebuilding the registry"""
        logger.info("Refreshing Manim documentation...")
        self.symbol_registry.clear()
        self._build_symbol_registry()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the documentation system"""
        return {
            'total_symbols': len(self.symbol_registry),
            'symbols_by_type': {
                symbol_type: len(self.get_symbols_by_type(symbol_type))
                for symbol_type in ['class', 'function', 'method', 'constant']
            },
            'embedding_available': self.embedding_available,
            'vector_index_size': self.vector_index.get_n_total() if self.vector_index else 0,
            'cache_directory': self.cache_dir
        }
    
    def _build_hardcoded_registry(self):
        """Build hardcoded registry of common Manim symbols"""
        symbols = {
            # Geometric Shapes
            'Circle': ManimSymbol(
                name='Circle',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Circle',
                signature='Circle(radius=1, color=WHITE, fill_opacity=0, stroke_width=4)',
                defaults={'radius': 1, 'color': 'WHITE', 'fill_opacity': 0, 'stroke_width': 4},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Circle.html',
                description='A circle geometric shape',
                examples=['Circle(radius=2, color=RED)', 'Circle().scale(0.5)'],
                source_code='class Circle(Arc):\n    def __init__(self, radius=1, **kwargs):\n        super().__init__(radius=radius, **kwargs)',
                version='0.18.0',
                tags=['geometry', 'shape', 'circle', '2d'],
                dependencies=['manim.mobject.geometry.line.Arc']
            ),
            'Square': ManimSymbol(
                name='Square',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Square',
                signature='Square(side_length=2, color=WHITE, fill_opacity=0, stroke_width=4)',
                defaults={'side_length': 2, 'color': 'WHITE', 'fill_opacity': 0, 'stroke_width': 4},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Square.html',
                description='A square geometric shape',
                examples=['Square(side_length=3, color=BLUE)', 'Square().rotate(PI/4)'],
                source_code='class Square(Rectangle):\n    def __init__(self, side_length=2, **kwargs):\n        super().__init__(width=side_length, height=side_length, **kwargs)',
                version='0.18.0',
                tags=['geometry', 'shape', 'square', '2d', 'rectangle'],
                dependencies=['manim.mobject.geometry.line.Rectangle']
            ),
            'Rectangle': ManimSymbol(
                name='Rectangle',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Rectangle',
                signature='Rectangle(width=4, height=2, color=WHITE, fill_opacity=0, stroke_width=4)',
                defaults={'width': 4, 'height': 2, 'color': 'WHITE', 'fill_opacity': 0, 'stroke_width': 4},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Rectangle.html',
                description='A rectangle geometric shape',
                examples=['Rectangle(width=6, height=3, color=GREEN)', 'Rectangle().scale(0.8)'],
                source_code='class Rectangle(Polygon):\n    def __init__(self, width=4, height=2, **kwargs):\n        super().__init__(**kwargs)',
                version='0.18.0',
                tags=['geometry', 'shape', 'rectangle', '2d', 'polygon'],
                dependencies=['manim.mobject.geometry.line.Polygon']
            ),
            'Triangle': ManimSymbol(
                name='Triangle',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Triangle',
                signature='Triangle(color=WHITE, fill_opacity=0, stroke_width=4)',
                defaults={'color': 'WHITE', 'fill_opacity': 0, 'stroke_width': 4},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Triangle.html',
                description='An equilateral triangle geometric shape',
                examples=['Triangle(color=YELLOW)', 'Triangle().scale(1.5)'],
                source_code='class Triangle(RegularPolygon):\n    def __init__(self, **kwargs):\n        super().__init__(n=3, **kwargs)',
                version='0.18.0',
                tags=['geometry', 'shape', 'triangle', '2d', 'polygon'],
                dependencies=['manim.mobject.geometry.line.RegularPolygon']
            ),
            'Line': ManimSymbol(
                name='Line',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Line',
                signature='Line(start=ORIGIN, end=RIGHT, color=WHITE, stroke_width=4)',
                defaults={'start': 'ORIGIN', 'end': 'RIGHT', 'color': 'WHITE', 'stroke_width': 4},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Line.html',
                description='A line segment between two points',
                examples=['Line(start=[-1,0,0], end=[1,0,0])', 'Line().set_color(RED)'],
                source_code='class Line(VMobject):\n    def __init__(self, start=ORIGIN, end=RIGHT, **kwargs):\n        super().__init__(**kwargs)',
                version='0.18.0',
                tags=['geometry', 'line', '2d', 'segment'],
                dependencies=['manim.mobject.types.vectorized_mobject.VMobject']
            ),
            'Arrow': ManimSymbol(
                name='Arrow',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Arrow',
                signature='Arrow(start=ORIGIN, end=RIGHT, color=WHITE, stroke_width=4, buff=0.25)',
                defaults={'start': 'ORIGIN', 'end': 'RIGHT', 'color': 'WHITE', 'stroke_width': 4, 'buff': 0.25},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Arrow.html',
                description='An arrow pointing from start to end',
                examples=['Arrow(start=[0,0,0], end=[2,1,0])', 'Arrow().set_color(BLUE)'],
                source_code='class Arrow(Line):\n    def __init__(self, start=ORIGIN, end=RIGHT, **kwargs):\n        super().__init__(start=start, end=end, **kwargs)',
                version='0.18.0',
                tags=['geometry', 'arrow', '2d', 'direction'],
                dependencies=['manim.mobject.geometry.line.Line']
            ),
            'Dot': ManimSymbol(
                name='Dot',
                symbol_type='class',
                canonical_path='manim.mobject.geometry.line.Dot',
                signature='Dot(point=ORIGIN, color=WHITE, radius=0.08, fill_opacity=1)',
                defaults={'point': 'ORIGIN', 'color': 'WHITE', 'radius': 0.08, 'fill_opacity': 1},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Dot.html',
                description='A circular dot at a specific point',
                examples=['Dot(point=[1,1,0])', 'Dot(radius=0.2, color=RED)'],
                source_code='class Dot(Circle):\n    def __init__(self, point=ORIGIN, **kwargs):\n        super().__init__(**kwargs)',
                version='0.18.0',
                tags=['geometry', 'dot', 'point', '2d'],
                dependencies=['manim.mobject.geometry.line.Circle']
            ),
            
            # Text and Math
            'Text': ManimSymbol(
                name='Text',
                symbol_type='class',
                canonical_path='manim.mobject.text.text_mobject.Text',
                signature='Text(text, color=WHITE, font_size=36, font="Arial")',
                defaults={'color': 'WHITE', 'font_size': 36, 'font': 'Arial'},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.text.text_mobject.Text.html',
                description='Text object with customizable font and styling',
                examples=['Text("Hello World")', 'Text("Math", font_size=48, color=BLUE)'],
                source_code='class Text(SVGMobject):\n    def __init__(self, text, **kwargs):\n        super().__init__(**kwargs)',
                version='0.18.0',
                tags=['text', 'font', 'string', '2d'],
                dependencies=['manim.mobject.types.vectorized_mobject.SVGMobject']
            ),
            'MathTex': ManimSymbol(
                name='MathTex',
                symbol_type='class',
                canonical_path='manim.mobject.text.tex_mobject.MathTex',
                signature='MathTex(tex_string, color=WHITE, font_size=36)',
                defaults={'color': 'WHITE', 'font_size': 36},
                doc_url='https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTex.html',
                description='Mathematical expressions using LaTeX syntax',
                examples=['MathTex(r"x^2 + y^2 = r^2")', 'MathTex(r"\\frac{a}{b}", color=RED)'],
                source_code='class MathTex(SingleStringMathTex):\n    def __init__(self, tex_string, **kwargs):\n        super().__init__(tex_string, **kwargs)',
                version='0.18.0',
                tags=['math', 'latex', 'tex', 'equation', '2d'],
                dependencies=['manim.mobject.text.tex_mobject.SingleStringMathTex']
            ),
            
            # Animations
            'Create': ManimSymbol(
                name='Create',
                symbol_type='class',
                canonical_path='manim.animation.creation.Create',
                signature='Create(mobject, run_time=1, lag_ratio=0)',
                defaults={'run_time': 1, 'lag_ratio': 0},
                doc_url='https://docs.manim.community/en/stable/reference/manim.animation.creation.Create.html',
                description='Animation that creates a mobject by drawing it',
                examples=['Create(circle)', 'Create(square, run_time=2)'],
                source_code='class Create(ShowPartial):\n    def __init__(self, mobject, **kwargs):\n        super().__init__(mobject, **kwargs)',
                version='0.18.0',
                tags=['animation', 'creation', 'drawing', 'show'],
                dependencies=['manim.animation.creation.ShowPartial']
            ),
            'FadeIn': ManimSymbol(
                name='FadeIn',
                symbol_type='class',
                canonical_path='manim.animation.fading.FadeIn',
                signature='FadeIn(mobject, run_time=1, lag_ratio=0, scale=1)',
                defaults={'run_time': 1, 'lag_ratio': 0, 'scale': 1},
                doc_url='https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeIn.html',
                description='Animation that fades in a mobject',
                examples=['FadeIn(text)', 'FadeIn(circle, scale=1.5)'],
                source_code='class FadeIn(FadeInOut):\n    def __init__(self, mobject, **kwargs):\n        super().__init__(mobject, **kwargs)',
                version='0.18.0',
                tags=['animation', 'fade', 'in', 'appear'],
                dependencies=['manim.animation.fading.FadeInOut']
            ),
            'FadeOut': ManimSymbol(
                name='FadeOut',
                symbol_type='class',
                canonical_path='manim.animation.fading.FadeOut',
                signature='FadeOut(mobject, run_time=1, lag_ratio=0, scale=1)',
                defaults={'run_time': 1, 'lag_ratio': 0, 'scale': 1},
                doc_url='https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeOut.html',
                description='Animation that fades out a mobject',
                examples=['FadeOut(text)', 'FadeOut(circle, scale=0.5)'],
                source_code='class FadeOut(FadeInOut):\n    def __init__(self, mobject, **kwargs):\n        super().__init__(mobject, **kwargs)',
                version='0.18.0',
                tags=['animation', 'fade', 'out', 'disappear'],
                dependencies=['manim.animation.fading.FadeInOut']
            ),
            'Transform': ManimSymbol(
                name='Transform',
                symbol_type='class',
                canonical_path='manim.animation.transform.Transform',
                signature='Transform(mobject, target_mobject, run_time=1, path_arc=0)',
                defaults={'run_time': 1, 'path_arc': 0},
                doc_url='https://docs.animation.transform.Transform.html',
                description='Animation that transforms one mobject into another',
                examples=['Transform(circle, square)', 'Transform(text, new_text)'],
                source_code='class Transform(Animation):\n    def __init__(self, mobject, target_mobject, **kwargs):\n        super().__init__(mobject, **kwargs)',
                version='0.18.0',
                tags=['animation', 'transform', 'morph', 'change'],
                dependencies=['manim.animation.animation.Animation']
            ),
            'MoveToTarget': ManimSymbol(
                name='MoveToTarget',
                symbol_type='class',
                canonical_path='manim.animation.movement.MoveToTarget',
                signature='MoveToTarget(mobject, run_time=1, path_arc=0)',
                defaults={'run_time': 1, 'path_arc': 0},
                doc_url='https://docs.manim.community/en/stable/reference/manim.animation.movement.MoveToTarget.html',
                description='Animation that moves a mobject to its target position',
                examples=['circle.generate_target(); circle.target.shift(UP)', 'MoveToTarget(circle)'],
                source_code='class MoveToTarget(Transform):\n    def __init__(self, mobject, **kwargs):\n        super().__init__(mobject, **kwargs)',
                version='0.18.0',
                tags=['animation', 'movement', 'target', 'position'],
                dependencies=['manim.animation.transform.Transform']
            ),
            
            # Colors
            'WHITE': ManimSymbol(
                name='WHITE',
                symbol_type='constant',
                canonical_path='manim.constants.WHITE',
                signature='WHITE = rgb_to_color([1, 1, 1])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='White color constant',
                examples=['Circle(color=WHITE)', 'Text("Hello", color=WHITE)'],
                source_code='WHITE = rgb_to_color([1, 1, 1])',
                version='0.18.0',
                tags=['color', 'white', 'constant'],
                dependencies=['manim.utils.color.rgb_to_color']
            ),
            'RED': ManimSymbol(
                name='RED',
                symbol_type='constant',
                canonical_path='manim.constants.RED',
                signature='RED = rgb_to_color([1, 0, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Red color constant',
                examples=['Circle(color=RED)', 'Square(color=RED)'],
                source_code='RED = rgb_to_color([1, 0, 0])',
                version='0.18.0',
                tags=['color', 'red', 'constant'],
                dependencies=['manim.utils.color.rgb_to_color']
            ),
            'BLUE': ManimSymbol(
                name='BLUE',
                symbol_type='constant',
                canonical_path='manim.constants.BLUE',
                signature='BLUE = rgb_to_color([0, 0, 1])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Blue color constant',
                examples=['Circle(color=BLUE)', 'Line(color=BLUE)'],
                source_code='BLUE = rgb_to_color([0, 0, 1])',
                version='0.18.0',
                tags=['color', 'blue', 'constant'],
                dependencies=['manim.utils.color.rgb_to_color']
            ),
            'GREEN': ManimSymbol(
                name='GREEN',
                symbol_type='constant',
                canonical_path='manim.constants.GREEN',
                signature='GREEN = rgb_to_color([0, 1, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Green color constant',
                examples=['Circle(color=GREEN)', 'Triangle(color=GREEN)'],
                source_code='GREEN = rgb_to_color([0, 1, 0])',
                version='0.18.0',
                tags=['color', 'green', 'constant'],
                dependencies=['manim.utils.color.rgb_to_color']
            ),
            'YELLOW': ManimSymbol(
                name='YELLOW',
                symbol_type='constant',
                canonical_path='manim.constants.YELLOW',
                signature='YELLOW = rgb_to_color([1, 1, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Yellow color constant',
                examples=['Circle(color=YELLOW)', 'Text("Warning", color=YELLOW)'],
                source_code='YELLOW = rgb_to_color([1, 1, 0])',
                version='0.18.0',
                tags=['color', 'yellow', 'constant'],
                dependencies=['manim.utils.color.rgb_to_color']
            ),
            
            # Mathematical Constants
            'PI': ManimSymbol(
                name='PI',
                symbol_type='constant',
                canonical_path='manim.constants.PI',
                signature='PI = 3.141592653589793',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Mathematical constant π (pi)',
                examples=['circle.rotate(PI/2)', 'angle = PI/4'],
                source_code='PI = 3.141592653589793',
                version='0.18.0',
                tags=['math', 'constant', 'pi', 'angle'],
                dependencies=[]
            ),
            'ORIGIN': ManimSymbol(
                name='ORIGIN',
                symbol_type='constant',
                canonical_path='manim.constants.ORIGIN',
                signature='ORIGIN = np.array([0, 0, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Origin point (0, 0, 0)',
                examples=['circle.move_to(ORIGIN)', 'Line(ORIGIN, RIGHT)'],
                source_code='ORIGIN = np.array([0, 0, 0])',
                version='0.18.0',
                tags=['math', 'constant', 'origin', 'point', 'coordinate'],
                dependencies=['numpy']
            ),
            'RIGHT': ManimSymbol(
                name='RIGHT',
                symbol_type='constant',
                canonical_path='manim.constants.RIGHT',
                signature='RIGHT = np.array([1, 0, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Right direction vector (1, 0, 0)',
                examples=['Line(ORIGIN, RIGHT)', 'arrow.shift(RIGHT)'],
                source_code='RIGHT = np.array([1, 0, 0])',
                version='0.18.0',
                tags=['math', 'constant', 'direction', 'vector', 'right'],
                dependencies=['numpy']
            ),
            'UP': ManimSymbol(
                name='UP',
                symbol_type='constant',
                canonical_path='manim.constants.UP',
                signature='UP = np.array([0, 1, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Up direction vector (0, 1, 0)',
                examples=['Line(ORIGIN, UP)', 'text.shift(UP)'],
                source_code='UP = np.array([0, 1, 0])',
                version='0.18.0',
                tags=['math', 'constant', 'direction', 'vector', 'up'],
                dependencies=['numpy']
            ),
            'DOWN': ManimSymbol(
                name='DOWN',
                symbol_type='constant',
                canonical_path='manim.constants.DOWN',
                signature='DOWN = np.array([0, -1, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Down direction vector (0, -1, 0)',
                examples=['Line(ORIGIN, DOWN)', 'circle.shift(DOWN)'],
                source_code='DOWN = np.array([0, -1, 0])',
                version='0.18.0',
                tags=['math', 'constant', 'direction', 'vector', 'down'],
                dependencies=['numpy']
            ),
            'LEFT': ManimSymbol(
                name='LEFT',
                symbol_type='constant',
                canonical_path='manim.constants.LEFT',
                signature='LEFT = np.array([-1, 0, 0])',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.constants.html',
                description='Left direction vector (-1, 0, 0)',
                examples=['Line(ORIGIN, LEFT)', 'square.shift(LEFT)'],
                source_code='LEFT = np.array([-1, 0, 0])',
                version='0.18.0',
                tags=['math', 'constant', 'direction', 'vector', 'left'],
                dependencies=['numpy']
            ),
            
            # Utility Functions
            'rgb_to_color': ManimSymbol(
                name='rgb_to_color',
                symbol_type='function',
                canonical_path='manim.utils.color.rgb_to_color',
                signature='rgb_to_color(rgb_values)',
                defaults={},
                doc_url='https://docs.manim.community/en/stable/reference/manim.utils.color.html',
                description='Convert RGB values to Manim color',
                examples=['rgb_to_color([1, 0, 0])', 'rgb_to_color([0.5, 0.5, 0.5])'],
                source_code='def rgb_to_color(rgb_values):\n    return Color(rgb=rgb_values)',
                version='0.18.0',
                tags=['utility', 'color', 'rgb', 'conversion'],
                dependencies=['manim.utils.color.Color']
            )
        }
        
        return symbols

    def ingest_online_docs(self, max_symbols: int = 25) -> int:
        """Scrape Manim CE reference docs to enrich the symbol registry.
        Fetches the reference index and visits symbol pages to extract signature, description, examples, and URLs.
        Returns the number of symbols added or updated.
        """
        try:
            base_ref = self.doc_sources.get('api_docs', 'https://docs.manim.community/en/stable/reference.html')
            # Compute base path for resolving relative links
            base_path = base_ref.rsplit('/', 1)[0] + '/'
            index_resp = requests.get(base_ref, timeout=15)
            if index_resp.status_code != 200:
                return 0
            soup = BeautifulSoup(index_resp.text, 'lxml')

            # Heuristic: pick reference links that look like symbol pages
            links: List[str] = []
            for a in soup.select('a.reference.internal'):
                href = a.get('href') or ''
                if not href:
                    continue
                if href.startswith('http'):
                    url = href
                else:
                    # resolve relative to reference.html directory
                    url = base_path + href.lstrip('/')
                # Only include detailed pages under reference that end with .html and have manim in path
                if '/reference/' in url and url.endswith('.html') and 'genindex' not in url and 'search' not in url:
                    links.append(url)

            # De-duplicate and cap
            seen = set()
            unique_links = []
            for url in links:
                if url not in seen:
                    seen.add(url)
                    unique_links.append(url)
            # If no links found, use a small seed list of known reference pages
            if not unique_links:
                unique_links = [
                    'https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Circle.html',
                    'https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Square.html',
                    'https://docs.manim.community/en/stable/reference/manim.mobject.geometry.line.Rectangle.html',
                    'https://docs.manim.community/en/stable/reference/manim.animation.creation.Create.html',
                    'https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeIn.html',
                    'https://docs.manim.community/en/stable/reference/manim.animation.fading.FadeOut.html',
                    'https://docs.manim.community/en/stable/reference/manim.mobject.text.text_mobject.Text.html',
                    'https://docs.manim.community/en/stable/reference/manim.mobject.text.tex_mobject.MathTex.html',
                ]
            unique_links = unique_links[:max_symbols]

            added_or_updated = 0
            for url in unique_links:
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code != 200:
                        continue
                    psoup = BeautifulSoup(r.text, 'lxml')

                    # Title as symbol name (fallback)
                    title_tag = psoup.select_one('h1')
                    raw_title = (title_tag.get_text(strip=True) if title_tag else '').split('—')[0].strip()
                    name_guess = raw_title.split('.')[-1] if raw_title else ''

                    # Try to find canonical path
                    canonical_path = ''
                    breadcrumb = psoup.select('div.breadcrumbs a')
                    if breadcrumb:
                        trail = [b.get_text(strip=True) for b in breadcrumb]
                        if raw_title and trail:
                            # Best effort only
                            canonical_path = raw_title

                    # Signature: first code block with signature or dl.sig
                    signature = ''
                    sig_tag = psoup.select_one('dl.function dd, dl.class dd, code.sig-prename, code.sig-name') or psoup.select_one('pre')
                    if sig_tag:
                        signature = sig_tag.get_text(" ", strip=True)

                    # Short description: first paragraph after title
                    description = ''
                    p = psoup.select_one('div.section p') or psoup.find('p')
                    if p:
                        description = p.get_text(" ", strip=True)[:300]

                    # Examples: collect up to 2 code blocks
                    examples: List[str] = []
                    for pre in psoup.select('div.highlight pre')[:2]:
                        code_text = pre.get_text()
                        if code_text:
                            examples.append(code_text[:400])

                    # Determine symbol type crudely
                    symbol_type = 'class' if 'class ' in signature.lower() or 'Class' in raw_title else 'function'

                    # Build symbol name
                    symbol_name = name_guess or raw_title or canonical_path
                    if not symbol_name:
                        continue

                    # Fill ManimSymbol
                    sym = ManimSymbol(
                        name=symbol_name,
                        symbol_type=symbol_type,
                        canonical_path=canonical_path or symbol_name,
                        signature=signature or symbol_name,
                        defaults={},
                        doc_url=url,
                        description=description or f"Manim symbol {symbol_name}",
                        examples=examples,
                        source_code='',
                        version='0.19.0',
                        tags=[t for t in [symbol_type, 'manim', 'reference'] if t],
                        dependencies=[],
                    )

                    # Insert/update registry (case-insensitive key normalization)
                    key = sym.name
                    self.symbol_registry[key] = sym
                    added_or_updated += 1
                except Exception:
                    continue

            # Persist cache and rebuild index
            try:
                self._save_registry_cache()
            except Exception:
                pass
            try:
                self._build_vector_index()
            except Exception:
                pass

            return added_or_updated
        except Exception:
            return 0

    def rebuild_index(self) -> None:
        """Force-rebuild vector index from the current registry and persist cache."""
        try:
            self._build_vector_index()
            self._save_registry_cache()
        except Exception:
            pass
