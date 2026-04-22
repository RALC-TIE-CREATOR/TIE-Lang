"""
neural/visualization.py
-----------------------
Visualización textual mínima para el aprendizaje en la capa neural.
"""


def _bar(value: int, scale: int = 1, char: str = "#") -> str:
    width = max(0, int(value) * scale)
    return char * width if width else "."


def render_error_history(training_result: dict) -> str:
    lines = ["Error history:"]
    for item in training_result.get("epochs", []):
        lines.append(
            f"  epoch {item['epoch']:>2}: error={item['error']:>2}  {_bar(item['error'])}"
        )
    return "\n".join(lines)


def render_parameter_history(training_result: dict) -> str:
    lines = ["Parameter history:"]
    for item in training_result.get("epochs", []):
        weights = ", ".join(str(w) for w in item["weights"])
        lines.append(
            f"  epoch {item['epoch']:>2}: w=[{weights}]  b={item['bias']}"
        )
    return "\n".join(lines)


def render_training_report(training_result: dict) -> str:
    return (
        f"{render_error_history(training_result)}\n"
        f"{render_parameter_history(training_result)}"
    )
