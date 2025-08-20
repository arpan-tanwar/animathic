import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sqlite3
import uuid

from schemas.feedback_schema import (
    GenerationRecord, UserFeedback, TrainingDataset, 
    ModelPerformance, FeedbackAnalytics, ModelType
)

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Collects and manages feedback for improving both Gemini and local models"""
    
    def __init__(self, db_path: str = "feedback_data.db"):
        self.db_path = db_path
        self.ensure_database()
        logger.info(f"✅ Feedback collector initialized with database: {db_path}")
    
    def ensure_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generation records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_records (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                user_id TEXT,
                prompt TEXT,
                primary_model TEXT,
                fallback_used BOOLEAN,
                fallback_model TEXT,
                generated_json TEXT,
                compiled_manim TEXT,
                render_success BOOLEAN,
                generation_time REAL,
                compilation_time REAL,
                render_time REAL,
                total_time REAL,
                video_path TEXT,
                error_message TEXT,
                suitable_for_training BOOLEAN,
                training_notes TEXT
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                generation_id TEXT PRIMARY KEY,
                rating INTEGER,
                quality TEXT,
                comments TEXT,
                animation_worked BOOLEAN,
                matched_intent BOOLEAN,
                feedback_timestamp TEXT,
                FOREIGN KEY (generation_id) REFERENCES generation_records (id)
            )
        """)
        
        # Training datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_datasets (
                id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                source TEXT,
                version TEXT,
                examples TEXT,
                total_examples INTEGER,
                avg_rating REAL,
                success_rate REAL,
                description TEXT,
                tags TEXT
            )
        """)
        
        # Model performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT,
                timestamp TEXT,
                total_generations INTEGER,
                successful_generations INTEGER,
                success_rate REAL,
                avg_user_rating REAL,
                avg_generation_time REAL,
                avg_total_time REAL,
                common_errors TEXT,
                error_counts TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def record_generation(self, record: GenerationRecord) -> str:
        """Record a generation attempt in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO generation_records (
                    id, timestamp, user_id, prompt, primary_model, fallback_used,
                    fallback_model, generated_json, compiled_manim, render_success,
                    generation_time, compilation_time, render_time, total_time,
                    video_path, error_message, suitable_for_training, training_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id, record.timestamp.isoformat(), record.user_id, record.prompt,
                record.primary_model.value, record.fallback_used,
                record.fallback_model.value if record.fallback_model else None,
                json.dumps(record.generated_json), record.compiled_manim, record.render_success,
                record.generation_time, record.compilation_time, record.render_time, record.total_time,
                record.video_path, record.error_message, record.suitable_for_training, record.training_notes
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Recorded generation {record.id} for user {record.user_id}")
            return record.id
            
        except Exception as e:
            logger.error(f"❌ Failed to record generation: {e}")
            raise e
    
    async def update_generation(self, generation_id: str, updates: Dict[str, Any]) -> bool:
        """Update a generation record with additional information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['compiled_manim', 'render_success', 'compilation_time', 
                          'render_time', 'total_time', 'video_path', 'error_message']:
                    set_clauses.append(f"{key} = ?")
                    if key in ['compiled_manim', 'video_path', 'error_message']:
                        values.append(str(value))
                    else:
                        values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(generation_id)
            query = f"UPDATE generation_records SET {', '.join(set_clauses)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated generation {generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update generation {generation_id}: {e}")
            return False
    
    async def record_user_feedback(self, generation_id: str, feedback: UserFeedback) -> bool:
        """Record user feedback for a generation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_feedback (
                    generation_id, rating, quality, comments, animation_worked,
                    matched_intent, feedback_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                generation_id, feedback.rating, feedback.quality.value,
                feedback.comments, feedback.animation_worked, feedback.matched_intent,
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Recorded feedback for generation {generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record feedback: {e}")
            return False
    
    async def get_generation_record(self, generation_id: str) -> Optional[GenerationRecord]:
        """Retrieve a generation record by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM generation_records WHERE id = ?
            """, (generation_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_generation_record(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve generation {generation_id}: {e}")
            return None
    
    async def get_training_data(self, 
                               model_type: Optional[ModelType] = None,
                               min_rating: int = 3,
                               limit: int = 1000) -> List[Dict[str, Any]]:
        """Get training data suitable for model improvement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT gr.*, uf.rating, uf.quality, uf.comments, uf.animation_worked, uf.matched_intent
                FROM generation_records gr
                LEFT JOIN user_feedback uf ON gr.id = uf.generation_id
                WHERE gr.suitable_for_training = 1
            """
            params = []
            
            if model_type:
                query += " AND gr.primary_model = ?"
                params.append(model_type.value)
            
            query += " AND (uf.rating IS NULL OR uf.rating >= ?)"
            params.append(min_rating)
            
            query += " ORDER BY gr.timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            training_data = []
            for row in rows:
                # Convert to training format
                training_example = {
                    "prompt": row[3],  # prompt
                    "json_output": json.loads(row[8]),  # generated_json
                    "rating": row[19] if row[19] else 3,  # rating or default
                    "success": row[10],  # render_success
                    "timestamp": row[1],  # timestamp
                    "model": row[4]  # primary_model
                }
                training_data.append(training_example)
            
            logger.info(f"✅ Retrieved {len(training_data)} training examples")
            return training_data
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve training data: {e}")
            return []
    
    async def create_training_dataset(self, 
                                    source: str,
                                    examples: List[Dict[str, Any]],
                                    description: str = "",
                                    tags: List[str] = None) -> str:
        """Create a new training dataset from collected data"""
        try:
            dataset_id = str(uuid.uuid4())
            
            # Calculate metrics
            ratings = [ex.get('rating', 3) for ex in examples]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            success_rate = sum(1 for ex in examples if ex.get('success', False)) / len(examples) if examples else 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO training_datasets (
                    id, created_at, updated_at, source, version, examples,
                    total_examples, avg_rating, success_rate, description, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                source, "1.0.0", json.dumps(examples), len(examples),
                avg_rating, success_rate, description, json.dumps(tags or [])
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created training dataset {dataset_id} with {len(examples)} examples")
            return dataset_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create training dataset: {e}")
            raise e
    
    async def export_training_dataset(self, dataset_id: str, format: str = "jsonl") -> str:
        """Export training dataset in specified format"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT examples FROM training_datasets WHERE id = ?
            """, (dataset_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            examples = json.loads(row[0])
            
            if format == "jsonl":
                output_path = f"training_data_{dataset_id}.jsonl"
                with open(output_path, 'w') as f:
                    for example in examples:
                        f.write(json.dumps(example) + '\n')
                
                logger.info(f"✅ Exported dataset {dataset_id} to {output_path}")
                return output_path
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"❌ Failed to export dataset {dataset_id}: {e}")
            raise e
    
    async def get_model_performance(self, 
                                  model_type: ModelType,
                                  days: int = 30) -> Optional[ModelPerformance]:
        """Get performance metrics for a specific model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_generations,
                    SUM(CASE WHEN render_success = 1 THEN 1 ELSE 0 END) as successful_generations,
                    AVG(generation_time) as avg_generation_time,
                    AVG(total_time) as avg_total_time
                FROM generation_records 
                WHERE primary_model = ? AND timestamp >= ?
            """, (model_type.value, cutoff_date))
            
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                total, successful, avg_gen_time, avg_total_time = row
                success_rate = (successful / total) * 100
                
                # Get user ratings
                cursor.execute("""
                    SELECT AVG(uf.rating) as avg_rating
                    FROM generation_records gr
                    JOIN user_feedback uf ON gr.id = uf.generation_id
                    WHERE gr.primary_model = ? AND gr.timestamp >= ?
                """, (model_type.value, cutoff_date))
                
                rating_row = cursor.fetchone()
                avg_rating = rating_row[0] if rating_row and rating_row[0] else 0
                
                conn.close()
                
                return ModelPerformance(
                    model_type=model_type,
                    total_generations=total,
                    successful_generations=successful,
                    success_rate=success_rate,
                    avg_user_rating=avg_rating,
                    avg_generation_time=avg_gen_time or 0,
                    avg_total_time=avg_total_time or 0
                )
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance for {model_type.value}: {e}")
            return None
    
    async def generate_analytics_report(self, days: int = 30) -> FeedbackAnalytics:
        """Generate comprehensive analytics report"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_generations,
                    SUM(CASE WHEN render_success = 1 THEN 1 ELSE 0 END) as successful_generations
                FROM generation_records 
                WHERE timestamp >= ?
            """, (start_date.isoformat(),))
            
            overall_row = cursor.fetchone()
            total_generations = overall_row[0] if overall_row else 0
            successful_generations = overall_row[1] if overall_row else 0
            overall_success_rate = (successful_generations / total_generations * 100) if total_generations > 0 else 0
            
            # Average user satisfaction
            cursor.execute("""
                SELECT AVG(rating) as avg_rating
                FROM user_feedback uf
                JOIN generation_records gr ON uf.generation_id = gr.id
                WHERE gr.timestamp >= ?
            """, (start_date.isoformat(),))
            
            rating_row = cursor.fetchone()
            avg_user_satisfaction = rating_row[0] if rating_row and rating_row[0] else 0
            
            # Model performance
            model_performance = []
            for model_type in ModelType:
                perf = await self.get_model_performance(model_type, days)
                if perf:
                    model_performance.append(perf)
            
            # Popular prompts
            cursor.execute("""
                SELECT prompt, COUNT(*) as count
                FROM generation_records 
                WHERE timestamp >= ?
                GROUP BY prompt
                ORDER BY count DESC
                LIMIT 10
            """, (start_date.isoformat(),))
            
            popular_prompts = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Generate improvement insights
            top_improvement_areas = self._analyze_improvement_areas(model_performance)
            training_priorities = self._generate_training_priorities(model_performance)
            
            return FeedbackAnalytics(
                period_start=start_date,
                period_end=end_date,
                total_generations=total_generations,
                overall_success_rate=overall_success_rate,
                avg_user_satisfaction=avg_user_satisfaction,
                model_performance=model_performance,
                top_improvement_areas=top_improvement_areas,
                training_priorities=training_priorities,
                popular_prompts=popular_prompts,
                prompt_complexity_distribution={}  # TODO: Implement complexity analysis
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate analytics report: {e}")
            raise e
    
    def _row_to_generation_record(self, row) -> GenerationRecord:
        """Convert database row to GenerationRecord object"""
        from schemas.feedback_schema import ModelType
        
        return GenerationRecord(
            id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            user_id=row[2],
            prompt=row[3],
            primary_model=ModelType(row[4]),
            fallback_used=bool(row[5]),
            fallback_model=ModelType(row[6]) if row[6] else None,
            generated_json=json.loads(row[7]) if row[7] else {},
            compiled_manim=row[8] or "",
            render_success=bool(row[9]),
            generation_time=row[10] or 0.0,
            compilation_time=row[11] or 0.0,
            render_time=row[12] or 0.0,
            total_time=row[13] or 0.0,
            video_path=row[14],
            error_message=row[15],
            suitable_for_training=bool(row[16]),
            training_notes=row[17]
        )
    
    def _analyze_improvement_areas(self, model_performance: List[ModelPerformance]) -> List[str]:
        """Analyze model performance to identify improvement areas"""
        areas = []
        
        for perf in model_performance:
            if perf.success_rate < 80:
                areas.append(f"Improve {perf.model_type.value} success rate (currently {perf.success_rate:.1f}%)")
            
            if perf.avg_user_rating < 3.5:
                areas.append(f"Improve {perf.model_type.value} user satisfaction (currently {perf.avg_user_rating:.1f}/5)")
            
            if perf.avg_generation_time > 60:
                areas.append(f"Optimize {perf.model_type.value} generation speed (currently {perf.avg_generation_time:.1f}s)")
        
        return areas[:5]  # Top 5 areas
    
    def _generate_training_priorities(self, model_performance: List[ModelPerformance]) -> List[str]:
        """Generate training priorities based on performance data"""
        priorities = []
        
        # Find worst performing model
        worst_model = min(model_performance, key=lambda x: x.success_rate, default=None)
        if worst_model and worst_model.success_rate < 70:
            priorities.append(f"Priority training for {worst_model.model_type.value}")
        
        # Identify models needing speed optimization
        slow_models = [p for p in model_performance if p.avg_generation_time > 60]
        for model in slow_models:
            priorities.append(f"Optimize {model.model_type.value} for speed")
        
        return priorities[:3]  # Top 3 priorities

    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] == 1
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    async def create_generation_record(self, generation_record: GenerationRecord) -> str:
        """Create a new generation record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO generation_records (
                    id, timestamp, user_id, prompt, primary_model, fallback_used,
                    fallback_model, generated_json, compiled_manim, render_success,
                    generation_time, compilation_time, render_time, total_time,
                    video_path, error_message, suitable_for_training, training_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                generation_record.id,
                datetime.utcnow().isoformat(),
                generation_record.user_id,
                generation_record.prompt,
                generation_record.primary_model.value,
                generation_record.fallback_used,
                generation_record.fallback_model.value if generation_record.fallback_model else None,
                json.dumps(generation_record.generated_json),
                generation_record.compiled_manim,
                generation_record.render_success,
                generation_record.generation_time,
                generation_record.compilation_time,
                generation_record.render_time,
                generation_record.total_time,
                generation_record.video_path,
                getattr(generation_record, 'error_message', None),
                generation_record.suitable_for_training,
                generation_record.training_notes
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Generation record created: {generation_record.id}")
            return generation_record.id
            
        except Exception as e:
            logger.error(f"❌ Failed to create generation record: {e}")
            raise RuntimeError(f"Failed to create generation record: {str(e)}")
    
    async def get_training_data_for_generation(self, generation_id: str) -> List[Dict[str, Any]]:
        """Get training data for a specific generation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT gr.*, uf.rating, uf.quality, uf.comments, uf.animation_worked, uf.matched_intent
                FROM generation_records gr
                LEFT JOIN user_feedback uf ON gr.id = uf.generation_id
                WHERE gr.id = ? AND gr.suitable_for_training = 1
            """, (generation_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return []
            
            # Convert to training data format
            training_data = []
            for row in rows:
                training_data.append({
                    "generation_id": row[0],
                    "prompt": row[2],
                    "generated_json": json.loads(row[7]) if row[7] else {},
                    "compiled_manim": row[8],
                    "rating": row[19] if row[19] else 3,
                    "quality": row[20] if row[20] else "medium",
                    "comments": row[21] if row[21] else "",
                    "animation_worked": bool(row[22]) if row[22] is not None else True,
                    "matched_intent": bool(row[23]) if row[23] is not None else True
                })
            
            return training_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get training data: {e}")
            return []
    
    async def close(self):
        """Close database connections"""
        # SQLite connections are automatically closed, but we can add cleanup here if needed
        pass
