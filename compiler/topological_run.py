import argparse
from pathlib import Path
import sys

from topology.lowering import run_topological_source

VERSION = "0.3.0-preview"


def _summarize_phase_projection(projection: dict) -> dict:
    resumen = {}
    for name, item in projection.items():
        if "measured_value" in item:
            resumen[name] = {
                "value": item["value"],
                "measured_value": item["measured_value"],
                "bits": item["bits"],
                "measured_bits": item["measured_bits"],
            }
        else:
            resumen[name] = {
                "input": item["input_winding"],
                "measured": item["measured_winding"],
            }
    return resumen


def _summarize_stability(projection: dict) -> dict:
    return {
        name: {
            "stable": item["stability"]["stable"],
            "bit_errors": item["stability"]["bit_errors"],
            "energy_delta": round(item["stability"]["energy_delta"], 6),
            "value": item["value"],
            "measured_value": item["measured_value"],
            "layout": item.get("layout", "unknown"),
        }
        for name, item in projection.items()
        if "stability" in item
    }


def run_file(
    path: str,
    with_phase_projection: bool = False,
    with_stability: bool = False,
) -> dict:
    archivo = Path(path)
    if not archivo.exists():
        raise FileNotFoundError(f"No existe el archivo: {archivo}")
    fuente = archivo.read_text(encoding="utf-8")
    resultado = run_topological_source(
        fuente,
        with_phase_projection=with_phase_projection or with_stability,
    )
    print(f"Topological output: {resultado.output}")
    print(f"Topological snapshot: {resultado.snapshot}")
    if resultado.phase_projection is not None:
        print(f"Phase projection: {_summarize_phase_projection(resultado.phase_projection)}")
        if with_stability:
            print(f"Phase stability: {_summarize_stability(resultado.phase_projection)}")
    return {
        "output": resultado.output,
        "snapshot": resultado.snapshot,
        "phase_projection": resultado.phase_projection,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tie-topology",
        description="Runner topologico experimental para TIE-Lang v0.3.0.",
    )
    parser.add_argument("path", help="Archivo .tie compatible con el lowering topologico")
    parser.add_argument(
        "--phase",
        action="store_true",
        help="Proyecta el estado final al sustrato de fase en core/",
    )
    parser.add_argument(
        "--stability",
        action="store_true",
        help="Reporta estabilidad de fase por registro topologico",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Muestra la version actual del runner topologico",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    if args.version:
        print(f"TIE-Lang Topological Runner v{VERSION}")
        return 0

    try:
        run_file(
            args.path,
            with_phase_projection=args.phase,
            with_stability=args.stability,
        )
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
