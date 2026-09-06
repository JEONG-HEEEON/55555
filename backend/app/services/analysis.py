import statistics as stats
from typing import List, Dict


def compute_summary(items: List[Dict]) -> Dict:
    """items: [{"date": "YYYY-MM-DD", "value": float, ...}, ...]"""
    if not items:
        return {
            "period": "데이터 없음",
            "count": 0,
            "metrics": {"total": 0, "average": 0, "max": 0, "min": 0},
            "trend": "데이터 없음",
        }

    sorted_items = sorted(items, key=lambda x: x["date"])
    values = [item["value"] for item in sorted_items]
    period = f"{sorted_items[0]['date']} ~ {sorted_items[-1]['date']}"

    total = sum(values)
    average = total / len(values)
    trend = _compute_trend(values)

    return {
        "period": period,
        "count": len(values),
        "metrics": {
            "total": round(total, 2),
            "average": round(average, 2),
            "max": round(max(values), 2),
            "min": round(min(values), 2),
        },
        "trend": trend,
    }


def compute_statistics(items: List[Dict]) -> Dict:
    """보너스: 요약 + 표준편차 + 최근 7개 이동평균"""
    summary = compute_summary(items)
    if not items:
        summary["std_dev"] = 0
        summary["moving_average_7"] = None
        return summary

    sorted_items = sorted(items, key=lambda x: x["date"])
    values = [item["value"] for item in sorted_items]

    summary["std_dev"] = round(stats.pstdev(values), 2) if len(values) > 1 else 0
    recent = values[-7:]
    summary["moving_average_7"] = round(sum(recent) / len(recent), 2)
    return summary


def _compute_trend(values: List[float], window: int = 7) -> str:
    """최근 구간 평균 vs 그 이전 구간 평균을 비교해 증가/감소/유지 판단"""
    if len(values) < window * 2:
        # 데이터가 적으면 처음/끝 절반으로 비교
        half = max(1, len(values) // 2)
        first_half, second_half = values[:half], values[half:]
    else:
        first_half, second_half = values[-(window * 2):-window], values[-window:]

    if not first_half or not second_half:
        return "유지"

    prev_avg = sum(first_half) / len(first_half)
    recent_avg = sum(second_half) / len(second_half)

    if prev_avg == 0:
        change_pct = 0
    else:
        change_pct = ((recent_avg - prev_avg) / abs(prev_avg)) * 100

    if change_pct > 3:
        return f"상승 (직전 구간 대비 +{change_pct:.1f}%)"
    elif change_pct < -3:
        return f"하락 (직전 구간 대비 {change_pct:.1f}%)"
    else:
        return "유지 (큰 변화 없음)"
