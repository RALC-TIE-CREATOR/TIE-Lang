"""
neural/perceptron.py
--------------------
Primera base experimental para la capa neural de TIE-Lang.

La idea no es simular una red neuronal moderna completa, sino ofrecer
un bloque mínimo y verificable donde los pesos se tratan como estados
topológicos discretos y persistentes.
"""

from dataclasses import dataclass, field


def _dot(a: list[int], b: list[int]) -> int:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class TopologicalPerceptron:
    """
    Perceptrón binario mínimo.

    - Las entradas son binarias (0/1).
    - Los pesos y el sesgo se modelan como enteros persistentes.
    - La salida es binaria (0/1).
    """

    input_size: int
    learning_rate: int = 1
    weights: list[int] = field(default_factory=list)
    bias: int = 0

    def __post_init__(self):
        if not self.weights:
            self.weights = [0] * self.input_size
        if len(self.weights) != self.input_size:
            raise ValueError("weights debe tener el mismo tamaño que input_size")

    def raw_score(self, inputs: list[int]) -> int:
        if len(inputs) != self.input_size:
            raise ValueError("entrada con tamaño inválido")
        return _dot(self.weights, inputs) + self.bias

    def predict(self, inputs: list[int]) -> int:
        return 1 if self.raw_score(inputs) > 0 else 0

    def train_step(self, inputs: list[int], expected: int) -> int:
        predicted = self.predict(inputs)
        error = expected - predicted

        if error != 0:
            for i, value in enumerate(inputs):
                self.weights[i] += self.learning_rate * error * value
            self.bias += self.learning_rate * error

        return error

    def train(
        self,
        samples: list[tuple[list[int], int]],
        epochs: int = 20,
    ) -> dict:
        history: list[int] = []

        for _ in range(epochs):
            total_error = 0
            for inputs, expected in samples:
                total_error += abs(self.train_step(inputs, expected))
            history.append(total_error)
            if total_error == 0:
                break

        return {
            "epochs_ran": len(history),
            "history": history,
            "weights": list(self.weights),
            "bias": self.bias,
        }


def train_boolean_model(
    gate: str,
    epochs: int = 20,
) -> TopologicalPerceptron:
    gate = gate.upper()
    datasets = {
        "AND": [
            ([0, 0], 0),
            ([0, 1], 0),
            ([1, 0], 0),
            ([1, 1], 1),
        ],
        "OR": [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 1),
        ],
    }

    if gate not in datasets:
        raise ValueError("gate debe ser 'AND' o 'OR'")

    model = TopologicalPerceptron(input_size=2)
    model.train(datasets[gate], epochs=epochs)
    return model
