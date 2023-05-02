import math
import pandas as pd
from collections import Counter
from tqdm import tqdm

def entropy(data, target_attr):
    frequencies = Counter([record[target_attr] for record in data])
    entropy = 0
    for freq in frequencies.values():
        probability = freq / len(data)
        entropy += -probability * math.log2(probability)
    return entropy


def gain_ratio_nominal(data, attribute, target_attr, subset, positives, negatives):
    attribute_entropy = entropy(subset, target_attr)
    values = [record[attribute] for record in data]
    unique_values = set(values)

    iv = 0
    gain = 0
    for value in unique_values:
        value_subset = [
            record for record in subset if record[attribute] == value]
        value_positives = [
            record for record in value_subset if record[target_attr] == "yes"]
        value_negatives = [
            record for record in value_subset if record[target_attr] == "no"]

        if len(value_subset) == 0:
            value_gain_ratio = 0
            value_iv = 0
        else:
            value_gain_ratio = entropy(value_subset, target_attr)
            value_iv = 0
            if len(value_positives) > 0:
                value_iv -= (len(value_positives) / len(value_subset)) * \
                    math.log2(len(value_positives) / len(value_subset))
                if len(value_negatives) > 0:
                    value_iv -= (len(value_negatives) / len(value_subset)) * \
                        math.log2(len(value_negatives) / len(value_subset))

        iv += (len(value_subset) / len(data)) * value_iv
        gain += (len(value_subset) / len(data)) * value_gain_ratio

    if iv == 0:
        gain_ratio = float('inf')
    else:
        gain_ratio = (entropy(data, target_attr) - gain) / iv

    return gain_ratio


def attribute_values(data, attribute):
    values = [record[attribute] for record in data]
    return list(set(values))


def majority_value(data, target_attr):
    value_counts = Counter(record[target_attr] for record in data)
    majority_value = max(value_counts, key=value_counts.get)
    return majority_value


def cn2(data, attributes, target_attr):
    """
    CN2 algorithm for inducing a decision rule-based classifier.
    """
    # Initialize the list of induced rules
    rules = []

    # Initialize a list of positive and negative examples
    positives = [record for record in data if record[target_attr] == "yes"]
    negatives = [record for record in data if record[target_attr] == "no"]

    # Start the algorithm
    pbar = None
    with tqdm(total=len(attributes), desc="CN2 Algorithm") as pbar:
        while positives:
            # Select the best attribute and its corresponding subset
            best_subset, best_attr = None, None
            max_gain_ratio = 0
            for attr in attributes:
                for value in attribute_values(data, attr):
                    subset = [
                        record for record in positives if record[attr] == value]
                    gain_ratio = gain_ratio_nominal(
                        data, attr, target_attr, subset, positives, negatives)
                    if gain_ratio > max_gain_ratio:
                        best_subset, best_attr, max_gain_ratio = subset, attr, gain_ratio
            if max_gain_ratio == 0:
                break
            rule = {"attribute": best_attr, "subset": best_subset}
            attributes.remove(best_attr)
            pbar.update(1)

            # Remove the covered examples from the positive examples
            positives = [
                record for record in positives if record not in best_subset]

            # Find the majority value for the covered examples and add it to the rule
            rule["conclusion"] = majority_value(best_subset, target_attr)

            # Add the rule to the list of induced rules
            rules.append(rule)

            # Add a default rule for negative examples
        rules.append(
            {"attribute": "default", "subset": negatives, "conclusion": "no"})

    return rules


def return_rules(rules):
    rows = []
    default_rule = None
    default_conclusion = None
    for rule in rules:
        if rule["attribute"] == "default":
            default_rule = rule["subset"]
            default_conclusion = rule["conclusion"]
        else:
            attribute_value = [record[rule["attribute"]]
                               for record in rule["subset"]][0]
            rows.append("If {} = {} then class is {}".format(
                rule["attribute"], attribute_value, rule["conclusion"]))
    return rows, default_rule, default_conclusion
