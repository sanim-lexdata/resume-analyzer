"""
Text embedding and semantic similarity using Sentence Transformers.
"""
import numpy as np
from typing import List, Union, Dict
from sentence_transformers import SentenceTransformer, util


class Embedder:
    """Handle text embeddings and semantic similarity calculations."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder with sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            print(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Model loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            print("Using fallback model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Encode text into embeddings.
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Numpy array of embeddings
        """
        if not text:
            # Return empty array for empty input
            return np.array([])
        
        # Convert to list if single string
        if isinstance(text, str):
            text = [text]
        
        # Filter out empty strings and None values
        text = [str(t).strip() for t in text if t and str(t).strip()]
        
        if not text:
            # Return empty array if all texts were empty
            return np.array([])
        
        try:
            # Encode text
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            print(f"⚠️ Error encoding text: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(text), 384))  # 384 is the embedding dimension
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Encode both texts
            emb1 = self.encode(text1)
            emb2 = self.encode(text2)
            
            if emb1.size == 0 or emb2.size == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = util.cos_sim(emb1, emb2)
            
            # Convert to float
            if isinstance(similarity, np.ndarray):
                return float(similarity[0][0])
            else:
                return float(similarity)
            
        except Exception as e:
            print(f"⚠️ Error calculating similarity: {e}")
            return 0.0
    
    def semantic_skill_match(
        self,
        resume_skills: List[str],
        jd_skills: List[str],
        threshold: float = 0.7
    ) -> Dict[str, any]:
        """
        Match skills semantically using embeddings.
        
        Args:
            resume_skills: Skills from resume
            jd_skills: Skills from job description
            threshold: Similarity threshold (0-1)
            
        Returns:
            Dictionary with semantic matching results
        """
        # Validate and clean inputs
        if not resume_skills or not jd_skills:
            return {
                'matched': [],
                'semantic_pairs': [],
                'unmatched_jd': list(jd_skills) if jd_skills else [],
                'unmatched_resume': list(resume_skills) if resume_skills else []
            }
        
        # Convert to list and filter
        resume_skills = [str(s).strip() for s in resume_skills if s and str(s).strip()]
        jd_skills = [str(s).strip() for s in jd_skills if s and str(s).strip()]
        
        if not resume_skills or not jd_skills:
            return {
                'matched': [],
                'semantic_pairs': [],
                'unmatched_jd': jd_skills,
                'unmatched_resume': resume_skills
            }
        
        try:
            # Encode all skills
            print(f"  Encoding {len(resume_skills)} resume skills...")
            resume_embs = self.encode(resume_skills)
            
            print(f"  Encoding {len(jd_skills)} JD skills...")
            jd_embs = self.encode(jd_skills)
            
            if resume_embs.size == 0 or jd_embs.size == 0:
                return {
                    'matched': [],
                    'semantic_pairs': [],
                    'unmatched_jd': jd_skills,
                    'unmatched_resume': resume_skills
                }
            
            # Calculate similarity matrix
            similarity_matrix = util.cos_sim(resume_embs, jd_embs)
            
            matched = []
            semantic_pairs = []
            matched_resume_idx = set()
            matched_jd_idx = set()
            
            # Find best matches for each JD skill
            for jd_idx, jd_skill in enumerate(jd_skills):
                best_score = 0
                best_resume_idx = -1
                
                for resume_idx, resume_skill in enumerate(resume_skills):
                    if resume_idx in matched_resume_idx:
                        continue
                    
                    score = float(similarity_matrix[resume_idx][jd_idx])
                    
                    if score >= threshold and score > best_score:
                        best_score = score
                        best_resume_idx = resume_idx
                
                if best_resume_idx >= 0:
                    matched.append(jd_skill)
                    semantic_pairs.append({
                        'jd_skill': jd_skill,
                        'resume_skill': resume_skills[best_resume_idx],
                        'similarity': best_score
                    })
                    matched_resume_idx.add(best_resume_idx)
                    matched_jd_idx.add(jd_idx)
            
            # Unmatched skills
            unmatched_jd = [skill for idx, skill in enumerate(jd_skills) if idx not in matched_jd_idx]
            unmatched_resume = [skill for idx, skill in enumerate(resume_skills) if idx not in matched_resume_idx]
            
            return {
                'matched': matched,
                'semantic_pairs': semantic_pairs,
                'unmatched_jd': unmatched_jd,
                'unmatched_resume': unmatched_resume
            }
            
        except Exception as e:
            print(f"⚠️ Error in semantic matching: {e}")
            import traceback
            traceback.print_exc()
            return {
                'matched': [],
                'semantic_pairs': [],
                'unmatched_jd': jd_skills,
                'unmatched_resume': resume_skills
            }
    
    def find_similar_texts(
        self,
        query: str,
        corpus: List[str],
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """
        Find most similar texts from corpus.
        
        Args:
            query: Query text
            corpus: List of texts to search
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with text and similarity score
        """
        if not query or not corpus:
            return []
        
        # Filter corpus
        corpus = [str(t).strip() for t in corpus if t and str(t).strip()]
        
        if not corpus:
            return []
        
        try:
            # Encode query and corpus
            query_emb = self.encode(query)
            corpus_embs = self.encode(corpus)
            
            if query_emb.size == 0 or corpus_embs.size == 0:
                return []
            
            # Calculate similarities
            similarities = util.cos_sim(query_emb, corpus_embs)[0]
            
            # Get top k
            top_results = []
            for idx, score in enumerate(similarities):
                top_results.append({
                    'text': corpus[idx],
                    'score': float(score)
                })
            
            # Sort by score
            top_results.sort(key=lambda x: x['score'], reverse=True)
            
            return top_results[:top_k]
            
        except Exception as e:
            print(f"⚠️ Error finding similar texts: {e}")
            return []
    
    def batch_similarity(
        self,
        texts1: List[str],
        texts2: List[str]
    ) -> np.ndarray:
        """
        Calculate pairwise similarities between two lists of texts.
        
        Args:
            texts1: First list of texts
            texts2: Second list of texts
            
        Returns:
            Similarity matrix (texts1 x texts2)
        """
        if not texts1 or not texts2:
            return np.array([])
        
        # Filter inputs
        texts1 = [str(t).strip() for t in texts1 if t and str(t).strip()]
        texts2 = [str(t).strip() for t in texts2 if t and str(t).strip()]
        
        if not texts1 or not texts2:
            return np.array([])
        
        try:
            # Encode both lists
            embs1 = self.encode(texts1)
            embs2 = self.encode(texts2)
            
            if embs1.size == 0 or embs2.size == 0:
                return np.zeros((len(texts1), len(texts2)))
            
            # Calculate similarity matrix
            similarity_matrix = util.cos_sim(embs1, embs2)
            
            return similarity_matrix.numpy()
            
        except Exception as e:
            print(f"⚠️ Error in batch similarity: {e}")
            return np.zeros((len(texts1), len(texts2)))
    
    def cluster_texts(
        self,
        texts: List[str],
        n_clusters: int = 5
    ) -> Dict[str, any]:
        """
        Cluster texts based on semantic similarity.
        
        Args:
            texts: List of texts to cluster
            n_clusters: Number of clusters
            
        Returns:
            Dictionary with cluster assignments and centroids
        """
        if not texts or len(texts) < n_clusters:
            return {'clusters': {}, 'labels': []}
        
        # Filter texts
        texts = [str(t).strip() for t in texts if t and str(t).strip()]
        
        if len(texts) < n_clusters:
            return {'clusters': {}, 'labels': []}
        
        try:
            from sklearn.cluster import KMeans
            
            # Encode texts
            embeddings = self.encode(texts)
            
            if embeddings.size == 0:
                return {'clusters': {}, 'labels': []}
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            
            # Organize into clusters
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(texts[idx])
            
            return {
                'clusters': clusters,
                'labels': labels.tolist(),
                'centroids': kmeans.cluster_centers_
            }
            
        except Exception as e:
            print(f"⚠️ Error clustering texts: {e}")
            return {'clusters': {}, 'labels': []}