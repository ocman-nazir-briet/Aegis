"""
Adaptive learning feedback service for improving predictions over time.
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.services.neo4j_service import Neo4jService
from app.models import PredictionFeedback

logger = logging.getLogger(__name__)


class FeedbackService:
    """Process user feedback to improve model accuracy."""

    def __init__(self, neo4j: Neo4jService):
        self.neo4j = neo4j

    def submit_feedback(self, feedback: PredictionFeedback) -> bool:
        """Submit prediction feedback for adaptive learning."""
        try:
            with self.neo4j.driver.session() as session:
                # Calculate accuracy score
                accuracy_score = 0.0
                if feedback.predicted_risk and feedback.actual_risk:
                    accuracy_score = 1.0 if feedback.predicted_risk == feedback.actual_risk else 0.0

                # Store feedback
                session.run("""
                    CREATE (:PredictionFeedback {
                        simulation_id: $sim_id,
                        predicted_risk: $pred_risk,
                        actual_risk: $actual_risk,
                        predicted_latency: $pred_latency,
                        actual_latency: $actual_latency,
                        predicted_error: $pred_error,
                        actual_error: $actual_error,
                        accuracy_score: $accuracy,
                        notes: $notes,
                        submitted_at: datetime()
                    })
                """,
                sim_id=feedback.simulation_id,
                pred_risk=feedback.predicted_risk,
                actual_risk=feedback.actual_risk,
                pred_latency=feedback.predicted_latency_delta,
                actual_latency=feedback.actual_latency_delta,
                pred_error=feedback.predicted_error_increase,
                actual_error=feedback.actual_error_increase,
                accuracy=accuracy_score,
                notes=feedback.notes)

                # Link to original ChangeEvent
                session.run("""
                    MATCH (ce:ChangeEvent {change_id: $sim_id})
                    SET ce.feedback_submitted = true,
                        ce.actual_risk = $actual_risk,
                        ce.feedback_timestamp = datetime()
                """, sim_id=feedback.simulation_id, actual_risk=feedback.actual_risk)

                logger.info(f"Feedback recorded for simulation {feedback.simulation_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def get_accuracy_insights(self, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Get model accuracy insights for optional repo filtering."""
        with self.neo4j.driver.session() as session:
            query = """
                MATCH (pf:PredictionFeedback)
                WHERE pf.accuracy_score IS NOT NULL
            """
            params = {}

            if repo_url:
                query += " AND EXISTS((pf)-[:FOR_CHANGE]->(:ChangeEvent {repo_url: $repo}))"
                params["repo"] = repo_url

            query += """
                WITH COUNT(pf) as total,
                     SUM(pf.accuracy_score) as correct,
                     PERCENTILE_CONT(pf.accuracy_score, 0.5) as median_acc,
                     AVG(pf.accuracy_score) as avg_acc
                RETURN total, correct, median_acc, avg_acc
            """

            result = session.run(query, **params)
            record = result.single()

            if record and record["total"] > 0:
                return {
                    "total_feedback": record["total"],
                    "accurate_predictions": int(record["correct"]),
                    "accuracy_rate": record["avg_acc"],
                    "median_accuracy": record["median_acc"]
                }
            return {"total_feedback": 0, "accurate_predictions": 0, "accuracy_rate": 0.0}

    def get_false_positives(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get predictions marked as False Positives (predicted High/Critical but actual was Low/Medium)."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (pf:PredictionFeedback)
                WHERE pf.submitted_at > datetime() - duration('P' + $days + 'D')
                AND pf.predicted_risk IN ['High', 'Critical']
                AND pf.actual_risk IN ['Low', 'Medium']
                RETURN pf.simulation_id as sim_id,
                       pf.predicted_risk as predicted,
                       pf.actual_risk as actual,
                       pf.notes as notes,
                       pf.submitted_at as timestamp
                ORDER BY pf.submitted_at DESC
                LIMIT 10
            """, days=days)

            fps = []
            for record in result:
                fps.append({
                    "simulation_id": record["sim_id"],
                    "predicted": record["predicted"],
                    "actual": record["actual"],
                    "notes": record["notes"],
                    "timestamp": record["timestamp"]
                })
            return fps

    def get_false_negatives(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get predictions marked as False Negatives (predicted Low/Medium but actual was High/Critical)."""
        with self.neo4j.driver.session() as session:
            result = session.run("""
                MATCH (pf:PredictionFeedback)
                WHERE pf.submitted_at > datetime() - duration('P' + $days + 'D')
                AND pf.predicted_risk IN ['Low', 'Medium']
                AND pf.actual_risk IN ['High', 'Critical']
                RETURN pf.simulation_id as sim_id,
                       pf.predicted_risk as predicted,
                       pf.actual_risk as actual,
                       pf.notes as notes,
                       pf.submitted_at as timestamp
                ORDER BY pf.submitted_at DESC
                LIMIT 10
            """, days=days)

            fns = []
            for record in result:
                fns.append({
                    "simulation_id": record["sim_id"],
                    "predicted": record["predicted"],
                    "actual": record["actual"],
                    "notes": record["notes"],
                    "timestamp": record["timestamp"]
                })
            return fns

    def get_prediction_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in prediction accuracy to guide model improvement."""
        with self.neo4j.driver.session() as session:
            # Group by repository
            repo_result = session.run("""
                MATCH (pf:PredictionFeedback)<-[:HAS_FEEDBACK]-(ce:ChangeEvent {repo_url: $repo})
                WITH ce.repo_url as repo,
                     COUNT(pf) as count,
                     AVG(pf.accuracy_score) as accuracy
                RETURN repo, count, accuracy
                ORDER BY count DESC
                LIMIT 5
            """)

            repos = {}
            for record in repo_result:
                repos[record["repo"]] = {
                    "feedback_count": record["count"],
                    "accuracy": record["accuracy"]
                }

            # Group by change type (feature, bugfix, refactor, etc.)
            change_type_result = session.run("""
                MATCH (pf:PredictionFeedback)<-[:HAS_FEEDBACK]-(ce:ChangeEvent {type: $type})
                WITH ce.type as change_type,
                     COUNT(pf) as count,
                     AVG(pf.accuracy_score) as accuracy
                RETURN change_type, count, accuracy
                ORDER BY accuracy DESC
            """)

            by_type = {}
            for record in change_type_result:
                by_type[record["change_type"]] = {
                    "feedback_count": record["count"],
                    "accuracy": record["accuracy"]
                }

            return {
                "by_repository": repos,
                "by_change_type": by_type,
                "total_patterns_analyzed": len(repos) + len(by_type)
            }

    def generate_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for improving prediction accuracy."""
        recommendations = []

        # Check false positives
        fps = self.get_false_positives(days=30)
        if len(fps) > 3:
            recommendations.append({
                "severity": "warning",
                "category": "false_positives",
                "message": f"High false positive rate ({len(fps)} in 30 days). Consider reducing risk thresholds.",
                "action": "Review blast_radius calculation and LLM prompt calibration."
            })

        # Check false negatives
        fns = self.get_false_negatives(days=30)
        if len(fns) > 2:
            recommendations.append({
                "severity": "error",
                "category": "false_negatives",
                "message": f"Missing risky changes ({len(fns)} in 30 days). Model underestimating risk.",
                "action": "Increase model sensitivity for High/Critical predictions."
            })

        # Check overall accuracy
        insights = self.get_accuracy_insights()
        if insights.get("accuracy_rate", 0) < 0.7:
            recommendations.append({
                "severity": "critical",
                "category": "low_accuracy",
                "message": f"Model accuracy at {insights.get('accuracy_rate', 0):.1%}. Below production threshold.",
                "action": "Fine-tune LLM prompt with recent feedback data."
            })

        return recommendations
