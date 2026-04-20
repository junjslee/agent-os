"""Bridges: mappings between episteme memory contract and external systems.

Each bridge is symmetric where possible: external events become memory-contract-v1
envelopes on pull, and envelopes become substrate-native writes on push. The kernel
treats every external memory system as a cache, never as authoritative truth.
"""
