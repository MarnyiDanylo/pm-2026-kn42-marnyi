"""Імітаційне моделювання Monte Carlo для прогнозу строків (ЛР9).

Запозичено та адаптовано за результатами перехресної рецензії (ЛР10)
з метою забезпечення 100% відтворюваності розрахунків перед викладачем.

Використання:
    python simulate.py [remaining_points] [velocity_csv_list] [simulations] [seed]

Приклад запуску за замовчуванням (сценарій залишку 18 SP):
    python simulate.py 18 10,8 10000 42
"""

import math
import random
import sys
from datetime import date, timedelta


def one_run(remaining: float, history: list[float]) -> int:
    """Одна ітерація симуляції: рахує кількість спринтів до закриття всіх points."""
    sprints = 0
    while remaining > 0:
        remaining -= random.choice(history)
        sprints += 1
    return sprints


def run_monte_carlo(
    remaining_points: float,
    velocity_history: list[float],
    n_simulations: int = 10000,
    seed: int | None = 42,
) -> tuple[int, int, list[int]]:
    if not velocity_history or max(velocity_history) <= 0:
        raise ValueError("Історія velocity повинна містити хоча б одне додатне значення.")

    if seed is not None:
        random.seed(seed)

    results = sorted(one_run(remaining_points, velocity_history) for _ in range(n_simulations))
    p50 = results[math.ceil(0.50 * n_simulations) - 1]
    p85 = results[math.ceil(0.85 * n_simulations) - 1]
    return p50, p85, results


def main() -> None:
    remaining = float(sys.argv[1]) if len(sys.argv) > 1 else 18.0
    history = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [10.0, 8.0]
    sims = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    seed_val = int(sys.argv[4]) if len(sys.argv) > 4 else 42

    p50, p85, results = run_monte_carlo(remaining, history, sims, seed_val)

    # Календарні дати:
    # Якщо залишок 18 SP - відлік від кінця Спринта 2 (2026-10-30) + P * 14 днів
    # Якщо весь реліз 36 SP - відлік від кінця Спринта 1 (2026-10-16) + (P - 1) * 14 днів
    if remaining == 18.0:
        base_date = date(2026, 10, 30)
        p50_date = base_date + timedelta(days=int(14 * p50))
        p85_date = base_date + timedelta(days=int(14 * p85))
    else:
        base_date = date(2026, 10, 16)
        p50_date = base_date + timedelta(days=int(14 * (p50 - 1)))
        p85_date = base_date + timedelta(days=int(14 * (p85 - 1)))

    print(f"=== Результати симуляції Monte Carlo (seed={seed_val}) ===")
    print(f"Залишок points: {remaining:g}, Історія velocity: {history}, Прогонів: {sims}")
    print(f"P50: {p50} спринтів -> дата {p50_date.isoformat()}")
    print(f"P85: {p85} спринтів -> дата {p85_date.isoformat()}")
    print(f"Мінімум спринтів: {results[0]}, Максимум спринтів: {results[-1]}")


if __name__ == "__main__":
    main()
