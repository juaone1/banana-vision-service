from typing import List
from app.core.supabase import supabase, supabase_admin
from app.core.logging import get_logger
from app.schemas.inference_result import InferenceResultOut
from uuid import UUID
import os
logger = get_logger('inference_result_service')


from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone

async def get_inference_results(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    try:
        # Use count='exact' for total count (for pagination)
        response = (
            supabase_admin
            .table("inference_results")
            .select(
                "id,created_at,regular_result,thermal_result,fused_confidence,fusion_decision,regular_output_url,thermal_output_url",
                count="exact"
            )
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        logger.info(f"Supabase raw response: {response}")
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error}")
            return {"data": [], "total": 0, "has_error": True, "error": str(response.error)}
        data = response.data if hasattr(response, 'data') else response["data"]
        total = response.count if hasattr(response, 'count') else response.get("count", 0)
        logger.info(f"Supabase data: {data} | total: {total}")
        return {"data": [InferenceResultOut(**row) for row in data], "total": total, "has_error": False, "error": None}
    except Exception as exc:
        logger.error(f"Exception in get_inference_results: {exc}")
        return {"data": [], "total": 0, "has_error": True, "error": str(exc)}


async def delete_inference_result(id: UUID) -> dict:
    """
    Delete an inference result row by its UUID.
    Returns a dict with operation result and error info.
    """
    try:
        response = (
            supabase_admin
            .table("inference_results")
            .delete()
            .eq("id", str(id))
            .execute()
        )
        logger.info(f"Delete response: {response}")
        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error}")
            return {"success": False, "has_error": True, "error": str(response.error)}
        if (hasattr(response, 'data') and response.data) or (isinstance(response, dict) and response.get("data")):
            return {"success": True, "has_error": False, "error": None}
        return {"success": False, "has_error": True, "error": "No row deleted"}
    except Exception as exc:
        logger.error(f"Exception in delete_inference_result: {exc}")
        return {"success": False, "has_error": True, "error": str(exc)}


async def get_tree_stats(tree_type: str = "Healthy") -> Dict[str, Any]:
    """
    Returns total number of trees and weekly timeseries for the past 12 weeks, grouped by fusion_decision.
    tree_type: 'Healthy' or 'Infected' (case-insensitive, matches fusion_decision)
    """
    try:
        now = datetime.now(timezone.utc)
        # Normalize tree_type
        fusion_decision = tree_type.lower()

        # Fetch all created_at for this fusion_decision (limit to last ~6 weeks for efficiency)
        # We'll determine the latest ISO week with data, then backtrack 5 more weeks
        data_resp = (
            supabase_admin
            .table("inference_results")
            .select("created_at")
            .eq("fusion_decision", fusion_decision)
            .order("created_at", desc=False)
            .execute()
        )
        if hasattr(data_resp, 'error') and data_resp.error:
            logger.error(f"Supabase error (fetch): {data_resp.error}")
            return {"series": [], "weeks": [], "totalTrees": 0, "has_error": True, "error": str(data_resp.error)}
        rows = data_resp.data if hasattr(data_resp, 'data') else data_resp["data"]
        # Aggregate by ISO week (year, week)
        from collections import defaultdict
        week_counts_map = defaultdict(int)
        for row in rows:
            created_at = row.get("created_at")
            if not created_at:
                continue
            try:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                continue
            iso_year, iso_week, _ = created_dt.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            week_counts_map[week_key] += 1
        # Always end at the current ISO week (even if no data)
        current_year, current_week, _ = now.isocalendar()
        week_labels = []
        week_counts = []
        year, week = current_year, current_week
        for _ in range(6):
            week_label = f"{year}-W{week:02d}"
            week_labels.insert(0, week_label)
            count = week_counts_map.get(week_label, 0)
            week_counts.insert(0, count)
            # Go to previous ISO week
            if week > 1:
                week -= 1
            else:
                year -= 1
                from datetime import date
                week = date(year, 12, 28).isocalendar()[1]  # Last ISO week of previous year
        # Total count for this type
        total = sum(week_counts_map.values())
        logger.info(f"Tree stats (ISO, ends now) for {tree_type}: total={total}, weeks={week_labels}, series={week_counts}")
        return {
            "series": [{"name": tree_type, "data": week_counts}],
            "weeks": week_labels,
            "totalTrees": total,
            "has_error": False,
            "error": None
        }
    except Exception as exc:
        logger.error(f"Exception in get_tree_stats: {exc}")
        return {"series": [], "weeks": [], "totalTrees": 0, "has_error": True, "error": str(exc)}
