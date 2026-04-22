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
        epochs_detail: list[dict] = []

        for epoch in range(epochs):
            total_error = 0
            for inputs, expected in samples:
                total_error += abs(self.train_step(inputs, expected))
            history.append(total_error)
            epochs_detail.append(
                {
                    "epoch": epoch + 1,
                    "error": total_error,
                    "weights": list(self.weights),
                    "bias": self.bias,
                }
            )
            if total_error == 0:
                break

        return {
            "epochs_ran": len(history),
            "history": history,
            "epochs": epochs_detail,
            "weights": list(self.weights),
            "bias": self.bias,
        }


@dataclass
class TopologicalMLP:
    """
    Red multicapa mínima con una sola capa oculta.

    Cada neurona sigue siendo un perceptrón topológico discreto.
    Esta clase permite expresar composiciones no linealmente separables
    como XOR usando varias neuronas binarias simples.
    """

    hidden_layer: list[TopologicalPerceptron]
    output_neuron: TopologicalPerceptron

    def hidden_state(self, inputs: list[int]) -> list[int]:
        return [neuron.predict(inputs) for neuron in self.hidden_layer]

    def predict(self, inputs: list[int]) -> int:
        return self.output_neuron.predict(self.hidden_state(inputs))


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


def build_xor_model() -> TopologicalMLP:
    """
    Construye un XOR mínimo usando una capa oculta de dos perceptrones.

    Estructura clásica:
    - neurona 1: OR
    - neurona 2: NAND
    - salida: AND(hidden_1, hidden_2)
    """
    hidden_or = TopologicalPerceptron(
        input_size=2,
        weights=[1, 1],
        bias=0,
    )
    hidden_nand = TopologicalPerceptron(
        input_size=2,
        weights=[-2, -2],
        bias=3,
    )
    output_and = TopologicalPerceptron(
        input_size=2,
        weights=[2, 2],
        bias=-3,
    )
    return TopologicalMLP(
        hidden_layer=[hidden_or, hidden_nand],
        output_neuron=output_and,
    )
