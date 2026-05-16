# Simulation Design Notes

> ⚠️ Synthetic demo simulator only. This is not a high-fidelity LEO network simulator and should not be interpreted as industrial validation.

The repository builds a public, reproducible decision table for LEO handover research-style experimentation.

## Constellation

A deterministic Walker-like toy constellation is generated from circular orbits. The model captures frequent visibility changes and fast handover windows while keeping the code lightweight and dependency-free. It does not use TLE/SGP4 propagation.

## Ground users

Ground users are sampled across global latitudes and longitudes. Each user has a service class and demand value so the feature table can represent heterogeneous traffic. These users are fake and do not represent real customers.

## Candidate generation

At each decision epoch, the simulator computes line-of-sight elevation and distance between each user and satellite. Visible satellites above the elevation mask become candidates, and only the strongest geometric candidates are retained.

## Features

The AI model uses geometry, link quality, load, continuity, and current-connection information:

- elevation angle
- distance
- RSRP-like signal estimate
- link margin
- satellite load
- remaining visibility time
- relative velocity
- current satellite indicator
- handover penalty
- signal rank
- demand and time encoding

## Labeling

A transparent oracle utility marks one selected satellite per user and timestep. The utility rewards signal quality and longer remaining visibility, while penalizing load and unnecessary handovers. This is an engineered label, not a real operations label.

## Evaluation

Policy comparison is based on temporal holdout decision epochs. Baselines include max-signal, sticky-signal, visibility-guard, load-aware, and stability-aware heuristics. The AI ranker is compared by top-1 agreement with the oracle, handover rate, signal quality, load, remaining visibility, outage-risk proxy, low-margin rate, and oracle-regret proxy.
