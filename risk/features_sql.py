from repos.features import rebuild_features


def rebuild(cutoff=None):
    rebuild_features(cutoff)


if __name__ == "__main__":
    rebuild()
    print("Rebuilt SQL-derived features for all wallets")
