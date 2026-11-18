"""Decision extraction and evidence ranking on source-linked RBI digests."""
import argparse
import collections
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CUTOFF = "2024-04-05"
RATE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|per cent)", re.I)


def read_data():
    return json.loads((ROOT / "decisions.json").read_text(encoding="utf-8"))


def tokens(sentence):
    return re.findall(r"[a-z]+", sentence.lower())


class Ranker:
    def __init__(self, rows):
        self.counts = [collections.Counter(), collections.Counter()]
        for row in rows:
            for i, sentence in enumerate(row["digest"]):
                self.counts[i == row["evidence"]].update(tokens(sentence))
        self.vocabulary = set().union(*self.counts)
        self.denominators = [sum(counter.values()) + len(self.vocabulary)
                             for counter in self.counts]

    def score(self, sentence):
        words = [word for word in tokens(sentence) if word in self.vocabulary]
        return sum(math.log((self.counts[1][word] + 1) / self.denominators[1])
                   - math.log((self.counts[0][word] + 1) / self.denominators[0])
                   for word in words)


def rule(sentence):
    words = tokens(sentence)
    return 2 * int("repo" in words) + int("policy" in words) + int(bool(RATE.search(sentence)))


def predict(row, scorer):
    index = max(range(len(row["digest"])), key=lambda i: scorer(row["digest"][i]))
    matches = RATE.findall(row["digest"][index])
    if len(matches) != 1:
        return dict(evidence=index, rate_bps=None, change_bps=None, action="unknown")
    from decimal import Decimal
    rate = int(Decimal(matches[0]) * 100)
    change = rate - row["previous_bps"]
    return dict(evidence=index, rate_bps=rate, change_bps=change,
                action="raise" if change > 0 else "cut" if change < 0 else "hold")


def evaluate(rows, pilot=False):
    if pilot:
        sample = [row for row in rows if row["date"] <= "2022-09-30" and row["date"] != "2021-10-08"]
        train, test = sample[:7], sample[7:10]
    else:
        train = [row for row in rows if row["date"] < CUTOFF]
        test = [row for row in rows if row["date"] >= CUTOFF]
    systems = {"rules": rule, "naive_bayes": Ranker(train).score}
    fields = ("action", "rate_bps", "change_bps", "evidence")
    results = []
    for row in test:
        results.append(dict(date=row["date"], gold={field: row[field] for field in fields},
                            predictions={name: predict(row, rank) for name, rank in systems.items()}))
    return dict(train=len(train), test=len(test), classes=dict(collections.Counter(r["action"] for r in test)),
                totals={name: {field: sum(r["predictions"][name][field] == r["gold"][field]
                                           for r in results) for field in fields}
                        for name in systems}, decisions=results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(evaluate(read_data(), args.pilot), indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
