"""Handler for /scores command."""


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.
    
    Args:
        lab_id: Optional lab identifier to filter scores.
        
    Returns:
        Score information (placeholder for Task 2).
    """
    if lab_id:
        return f"Scores for {lab_id} will be shown here (placeholder)"
    return "Scores will be shown here (placeholder)"
