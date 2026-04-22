"""
tests/test_neural.py
--------------------
Tests para la primera capa neural experimental de TIE-Lang.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neural import (
    TopologicalMLP,
    TopologicalPerceptron,
    build_xor_model,
    train_boolean_model,
)


def test_and_perceptron():
    print("── NEURAL: AND ──────────────────────────")
    model = train_boolean_model("AND", epochs=20)

    casos = [
        ([0, 0], 0),
        ([0, 1], 0),
        ([1, 0], 0),
        ([1, 1], 1),
    ]
    for inputs, esperado in casos:
        salida = model.predict(inputs)
        ok = salida == esperado
        print(f"  AND{tuple(inputs)} = {salida}  esp={esperado}  {'✅' if ok else '❌'}")
        assert ok
    print()


def test_or_perceptron():
    print("── NEURAL: OR ───────────────────────────")
    model = train_boolean_model("OR", epochs=20)

    casos = [
        ([0, 0], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 1], 1),
    ]
    for inputs, esperado in casos:
        salida = model.predict(inputs)
        ok = salida == esperado
        print(f"  OR{tuple(inputs)} = {salida}  esp={esperado}  {'✅' if ok else '❌'}")
        assert ok
    print()


def test_manual_training_converges():
    print("── NEURAL: Convergencia ─────────────────")
    model = TopologicalPerceptron(input_size=2)
    resultado = model.train(
        [
            ([0, 0], 0),
            ([0, 1], 1),
            ([1, 0], 1),
            ([1, 1], 1),
        ],
        epochs=20,
    )

    ok = resultado["history"][-1] == 0
    print(f"  Historial: {resultado['history']}")
    print(f"  Convergió: {'✅' if ok else '❌'}")
    assert ok
    print()


def test_xor_mlp():
    print("── NEURAL: XOR MLP ──────────────────────")
    model = build_xor_model()
    assert isinstance(model, TopologicalMLP)

    casos = [
        ([0, 0], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 1], 0),
    ]
    for inputs, esperado in casos:
        hidden = model.hidden_state(inputs)
        salida = model.predict(inputs)
        ok = salida == esperado
        print(
            f"  XOR{tuple(inputs)} = {salida}  hidden={hidden}  esp={esperado}  {'✅' if ok else '❌'}"
        )
        assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Neural")
    print("=" * 45)
    print()
    test_and_perceptron()
    test_or_perceptron()
    test_manual_training_converges()
    test_xor_mlp()
    print("✅ Capa neural experimental verificada")
