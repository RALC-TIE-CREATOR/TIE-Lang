from .perceptron import (
    BOOLEAN_DATASETS,
    TopologicalMLP,
    TopologicalPerceptron,
    TrainableTopologicalMLP,
    build_xor_model,
    get_boolean_dataset,
    train_boolean_model,
    train_dataset_mlp,
    train_xor_mlp,
)
from .visualization import (
    render_error_history,
    render_parameter_history,
    render_training_report,
)
