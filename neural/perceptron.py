"""
neural/perceptron.py
--------------------
Primera base experimental para la capa neural de TIE-Lang.

La idea no es simular una red neuronal moderna completa, sino ofrecer
un bloque mínimo y verificable donde los pesos se tratan como estados
topológicos discretos y persistentes.
"""

from dataclasses import dataclass, field
import math
import random


def _dot(a: list[int], b: list[int]) -> int:
    return sum(x * y for x, y in zip(a, b))


def _sigmoid(x: float) -> float:
    if x < -60:
        return 0.0
    if x > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


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


@dataclass
class TrainableTopologicalMLP:
    """
    Red multicapa mínima entrenable con una capa oculta.

    Esta versión usa propagación hacia adelante y backpropagation básicos
    para aprender funciones no linealmente separables como XOR.
    """

    input_size: int
    hidden_size: int
    learning_rate: float = 0.5
    seed: int = 7
    hidden_weights: list[list[float]] = field(default_factory=list)
    hidden_biases: list[float] = field(default_factory=list)
    output_weights: list[float] = field(default_factory=list)
    output_bias: float = 0.0

    def __post_init__(self):
        rng = random.Random(self.seed)
        hidden_limit = math.sqrt(6.0 / (self.input_size + self.hidden_size))
        output_limit = math.sqrt(6.0 / (self.hidden_size + 1))

        if not self.hidden_weights:
            self.hidden_weights = [
                [rng.uniform(-hidden_limit, hidden_limit) for _ in range(self.input_size)]
                for _ in range(self.hidden_size)
            ]
        if not self.hidden_biases:
            self.hidden_biases = [rng.uniform(-0.25, 0.25) for _ in range(self.hidden_size)]
        if not self.output_weights:
            self.output_weights = [
                rng.uniform(-output_limit, output_limit) for _ in range(self.hidden_size)
            ]
        if len(self.hidden_weights) != self.hidden_size:
            raise ValueError("hidden_weights debe coincidir con hidden_size")
        if len(self.hidden_biases) != self.hidden_size:
            raise ValueError("hidden_biases debe coincidir con hidden_size")
        if len(self.output_weights) != self.hidden_size:
            raise ValueError("output_weights debe coincidir con hidden_size")

    def forward(self, inputs: list[int]) -> dict:
        if len(inputs) != self.input_size:
            raise ValueError("entrada con tamaño inválido")

        hidden_raw = [
            sum(w * x for w, x in zip(weights, inputs)) + bias
            for weights, bias in zip(self.hidden_weights, self.hidden_biases)
        ]
        hidden = [_sigmoid(v) for v in hidden_raw]
        output_raw = sum(w * h for w, h in zip(self.output_weights, hidden)) + self.output_bias
        output = _sigmoid(output_raw)

        return {
            "inputs": list(inputs),
            "hidden_raw": hidden_raw,
            "hidden": hidden,
            "output_raw": output_raw,
            "output": output,
        }

    def predict_proba(self, inputs: list[int]) -> float:
        return self.forward(inputs)["output"]

    def predict(self, inputs: list[int]) -> int:
        return 1 if self.predict_proba(inputs) >= 0.5 else 0

    def train_step(self, inputs: list[int], expected: int) -> float:
        state = self.forward(inputs)
        output = state["output"]
        hidden = state["hidden"]

        error = expected - output
        delta_out = error * output * (1.0 - output)

        delta_hidden = [
            hidden[i] * (1.0 - hidden[i]) * self.output_weights[i] * delta_out
            for i in range(self.hidden_size)
        ]

        for i in range(self.hidden_size):
            self.output_weights[i] += self.learning_rate * delta_out * hidden[i]
        self.output_bias += self.learning_rate * delta_out

        for i in range(self.hidden_size):
            for j in range(self.input_size):
                self.hidden_weights[i][j] += self.learning_rate * delta_hidden[i] * inputs[j]
            self.hidden_biases[i] += self.learning_rate * delta_hidden[i]

        return error * error

    def train(
        self,
        samples: list[tuple[list[int], int]],
        epochs: int = 2000,
    ) -> dict:
        history: list[float] = []
        epochs_detail: list[dict] = []
        expected_outputs = [expected for _, expected in samples]
        rng = random.Random(self.seed)

        for epoch in range(epochs):
            shuffled_samples = list(samples)
            rng.shuffle(shuffled_samples)
            total_loss = 0.0
            for inputs, expected in shuffled_samples:
                total_loss += self.train_step(inputs, expected)

            history.append(total_loss)
            epochs_detail.append(
                {
                    "epoch": epoch + 1,
                    "error": round(total_loss, 6),
                    "hidden_weights": [list(row) for row in self.hidden_weights],
                    "hidden_biases": list(self.hidden_biases),
                    "output_weights": list(self.output_weights),
                    "output_bias": self.output_bias,
                }
            )

            preds = [self.predict(inputs) for inputs, _ in samples]
            if preds == expected_outputs:
                break

        return {
            "epochs_ran": len(history),
            "history": history,
            "epochs": epochs_detail,
            "hidden_weights": [list(row) for row in self.hidden_weights],
            "hidden_biases": list(self.hidden_biases),
            "output_weights": list(self.output_weights),
            "output_bias": self.output_bias,
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


def train_xor_mlp(
    epochs: int = 2000,
    learning_rate: float = 0.5,
    seed: int = 7,
    hidden_size: int = 2,
    attempts: int = 8,
) -> TrainableTopologicalMLP:
    samples = [
        ([0, 0], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 1], 0),
    ]
    best_model = None
    best_score = -1

    for offset in range(attempts):
        model = TrainableTopologicalMLP(
            input_size=2,
            hidden_size=hidden_size,
            learning_rate=learning_rate,
            seed=seed + offset,
        )
        model.train(samples, epochs=epochs)
        preds = [model.predict(inputs) for inputs, _ in samples]
        score = sum(int(pred == expected) for pred, (_, expected) in zip(preds, samples))
        if score > best_score:
            best_model = model
            best_score = score
        if preds == [expected for _, expected in samples]:
            return model

    raise RuntimeError(
        f"no se logró convergencia XOR tras {attempts} intentos; mejor score={best_score}/4"
    )
