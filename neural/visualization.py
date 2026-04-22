"""
neural/visualization.py
-----------------------
Visualización textual mínima para el aprendizaje en la capa neural.
"""


def _bar(value: float, scale: int = 1, char: str = "#") -> str:
    width = max(0, int(round(value * scale)))
    return char * width if width else "."


def render_error_history(training_result: dict) -> str:
    lines = ["Error history:"]
    errors = [item["error"] for item in training_result.get("epochs", [])]
    max_error = max(errors, default=0)
    scale = 1
    if max_error and max_error < 1:
        scale = 20
    elif max_error and max_error < 5:
        scale = 4
    for item in training_result.get("epochs", []):
        lines.append(
            f"  epoch {item['epoch']:>2}: error={item['error']:>7.4f}  {_bar(item['error'], scale=scale)}"
        )
    return "\n".join(lines)


def render_parameter_history(training_result: dict) -> str:
    if training_result.get("epochs") and "hidden_weights" in training_result["epochs"][0]:
        return render_mlp_parameter_history(training_result)

    lines = ["Parameter history:"]
    for item in training_result.get("epochs", []):
        weights = ", ".join(f"{w:.4f}" for w in item["weights"])
        lines.append(
            f"  epoch {item['epoch']:>2}: w=[{weights}]  b={item['bias']:.4f}"
        )
    return "\n".join(lines)


def render_mlp_parameter_history(training_result: dict) -> str:
    lines = ["MLP parameter history:"]
    for item in training_result.get("epochs", []):
        hidden_parts = []
        for index, row in enumerate(item["hidden_weights"], start=1):
            weights = ", ".join(f"{w:.4f}" for w in row)
            hidden_parts.append(
                f"h{index}=[{weights}] b={item['hidden_biases'][index - 1]:.4f}"
            )
        output_weights = ", ".join(f"{w:.4f}" for w in item["output_weights"])
        lines.append(
            f"  epoch {item['epoch']:>2}: "
            f"{' | '.join(hidden_parts)} || out=[{output_weights}] b={item['output_bias']:.4f}"
        )
    return "\n".join(lines)


def render_training_report(training_result: dict) -> str:
    return (
        f"{render_error_history(training_result)}\n"
        f"{render_parameter_history(training_result)}"
    )
