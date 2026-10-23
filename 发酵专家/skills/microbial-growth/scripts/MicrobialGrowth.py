import math

MODELS = ("gompertz", "logistic")


def _concentration(model, rate, lag, asymptote, C0, time):
    if model == "gompertz":
        exponent = -math.exp((lag - time) * rate / asymptote + 1)
        return C0 * asymptote * math.exp(exponent)
    return asymptote / (1 + (asymptote / C0 - 1) * math.exp(rate * (lag - time)))


def microbial_growth(model, rate, lag, asymptote, C0, time, Temperature):
    if model is None or str(model).strip() == "":
        return (
            "Error: model is required. Please choose one of: gompertz, logistic"
        )

    key = str(model).strip().lower()
    if key not in MODELS:
        return (
            f"Error: unknown model '{model}'. Please choose one of: gompertz, logistic"
        )

    params = [("rate", rate), ("lag", lag), ("asymptote", asymptote), ("C0", C0), ("time", time), ("Temperature", Temperature)]
    for name, val in params:
        try:
            float(val)
        except (ValueError, TypeError):
            return f"Error: {name} must be a number, got '{val}'"

    rate = float(rate)
    lag = float(lag)
    asymptote = float(asymptote)
    C0 = float(C0)
    time = float(time)
    Temperature = float(Temperature)

    Ct = _concentration(key, rate, lag, asymptote, C0, time)
    label = "Gompertz Growth Model Result" if key == "gompertz" else "Logistic Growth Model Result"

    return (
        f"{label}:\n"
        f"  Model model = {key}\n"
        f"  Initial concentration C0 = {C0}\n"
        f"  Max concentration asymptote = {asymptote}\n"
        f"  Max growth rate rate = {rate}\n"
        f"  Lag phase lag = {lag}\n"
        f"  Time time = {time}\n"
        f"  Temperature Temperature = {Temperature}C\n"
        f"  => C({time}) = {Ct:.4f}"
    )


def plot_growth(model, rate, lag, asymptote, C0, hours=24, Temperature=30, output=None):
    if model is None or str(model).strip() == "":
        return None, "Error: model is required. Please choose one of: gompertz, logistic"
    key = str(model).strip().lower()
    if key not in MODELS:
        return None, f"Error: unknown model '{model}'. Please choose one of: gompertz, logistic"

    params = [("rate", rate), ("lag", lag), ("asymptote", asymptote), ("C0", C0), ("hours", hours), ("Temperature", Temperature)]
    for name, val in params:
        try:
            float(val)
        except (ValueError, TypeError):
            return None, f"Error: {name} must be a number, got '{val}'"

    rate = float(rate)
    lag = float(lag)
    asymptote = float(asymptote)
    C0 = float(C0)
    hours = float(hours)
    Temperature = float(Temperature)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    steps = max(2, int(hours * 6) + 1)
    times = [hours * i / (steps - 1) for i in range(steps)]
    concentrations = [_concentration(key, rate, lag, asymptote, C0, t) for t in times]

    plt.figure(figsize=(10, 6))
    plt.plot(times, concentrations, "b-", linewidth=2, label=f"{key.capitalize()} Curve")
    plt.axvline(x=lag, color="gray", linestyle="--", alpha=0.5, label=f"Lag phase = {lag}")
    plt.scatter(times, concentrations, color="red", s=12, zorder=5)
    plt.xlabel("Time")
    plt.ylabel("Concentration (CFU)")
    plt.title(f"Microbial Growth Curve - {key.capitalize()} ({Temperature}C)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if output is None:
        output = f"microbial_growth_curve_{key}.png"
    plt.savefig(output, dpi=150)
    plt.close()
    return output, None


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    is_plot = "--plot" in args
    if is_plot:
        args.remove("--plot")

    if is_plot:
        if len(args) not in (6, 7, 8):
            print("Usage: python MicrobialGrowth.py <model> <rate> <lag> <asymptote> <C0> <hours> [Temperature] [output] --plot")
            sys.exit(1)
        model, rate, lag, asymptote, C0, hours = args[:6]
        temperature = args[6] if len(args) > 6 else 30
        output = args[7] if len(args) > 7 else None
        path, err = plot_growth(model, rate, lag, asymptote, C0, hours, temperature, output)
        if err:
            print(err)
            sys.exit(1)
        print(f"Growth curve saved to {path}")
    else:
        if len(args) != 7:
            print("Usage: python MicrobialGrowth.py <model> <rate> <lag> <asymptote> <C0> <time> <Temperature>")
            print("  model: gompertz | logistic")
            print("  add --plot to draw the growth curve")
            sys.exit(1)
        print(microbial_growth(*args))
