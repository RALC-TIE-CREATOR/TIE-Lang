"""
tests/test_neural.py
--------------------
Tests para la primera capa neural experimental de TIE-Lang.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from neural import (
    BOOLEAN_DATASETS,
    TopologicalMLP,
    TopologicalPerceptron,
    TrainableTopologicalMLP,
    build_xor_model,
    get_boolean_dataset,
    render_error_history,
    render_parameter_history,
    render_training_report,
    train_boolean_model,
    train_dataset_mlp,
    train_xor_mlp,
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


def test_dataset_registry():
    print("── NEURAL: Datasets ─────────────────────")
    nombres = sorted(BOOLEAN_DATASETS)
    ok = "MAJORITY3" in nombres and "PARITY3" in nombres
    print(f"  Disponibles: {', '.join(nombres)}")
    print(f"  Registro extendido: {'✅' if ok else '❌'}")
    assert ok
    assert len(get_boolean_dataset("MAJORITY3")) == 8
    assert len(get_boolean_dataset("PARITY3")) == 8
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
    assert len(resultado["epochs"]) == resultado["epochs_ran"]
    print()


def test_majority3_perceptron():
    print("── NEURAL: MAJORITY3 ────────────────────")
    model = train_boolean_model("MAJORITY3", epochs=30)

    casos = get_boolean_dataset("MAJORITY3")
    for inputs, esperado in casos:
        salida = model.predict(inputs)
        ok = salida == esperado
        print(
            f"  MAJ{tuple(inputs)} = {salida}  esp={esperado}  {'✅' if ok else '❌'}"
        )
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


def test_training_visualization():
    print("── NEURAL: Visualización ────────────────")
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

    error_view = render_error_history(resultado)
    param_view = render_parameter_history(resultado)
    report = render_training_report(resultado)

    ok = (
        "Error history:" in error_view
        and "Parameter history:" in param_view
        and "epoch" in report
    )
    print(error_view)
    print(param_view)
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


def test_trainable_xor_mlp():
    print("── NEURAL: XOR entrenable ───────────────")
    model = train_xor_mlp(epochs=4000, learning_rate=0.7, seed=7)
    assert isinstance(model, TrainableTopologicalMLP)

    casos = [
        ([0, 0], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 1], 0),
    ]
    resultados = []
    for inputs, esperado in casos:
        proba = model.predict_proba(inputs)
        salida = model.predict(inputs)
        resultados.append(salida)
        ok = salida == esperado
        print(
            f"  XOR{tuple(inputs)} = {salida}  p={proba:.4f}  esp={esperado}  {'✅' if ok else '❌'}"
        )
        assert ok
    assert resultados == [0, 1, 1, 0]
    print()


def test_parity3_trainable_mlp():
    print("── NEURAL: PARITY3 entrenable ───────────")
    model = train_dataset_mlp(
        "PARITY3",
        epochs=8000,
        learning_rate=0.7,
        seed=11,
        hidden_size=6,
        attempts=10,
    )
    assert isinstance(model, TrainableTopologicalMLP)

    casos = get_boolean_dataset("PARITY3")
    resultados = []
    for inputs, esperado in casos:
        proba = model.predict_proba(inputs)
        salida = model.predict(inputs)
        resultados.append(salida)
        ok = salida == esperado
        print(
            f"  PAR{tuple(inputs)} = {salida}  p={proba:.4f}  esp={esperado}  {'✅' if ok else '❌'}"
        )
        assert ok
    assert resultados == [esperado for _, esperado in casos]
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: Neural")
    print("=" * 45)
    print()
    test_and_perceptron()
    test_or_perceptron()
    test_dataset_registry()
    test_manual_training_converges()
    test_majority3_perceptron()
    test_xor_mlp()
    test_training_visualization()
    test_trainable_xor_mlp()
    test_parity3_trainable_mlp()
    print("✅ Capa neural experimental verificada")
