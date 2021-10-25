import pandas as pd
import click
import os


@click.command()
@click.option("--csv_path", help="path to the csv with species classification results")
@click.option(
    "--common_to_filter", help="common name to filter (can use more than once)", multiple=True
)
@click.option("--threshold", help="threshold to filter common", type=float)
def main(csv_path, common_to_filter, threshold):
    df = pd.read_csv(csv_path, names=["path", "folder", "query", "sciname", "common", "likelihood"])
    paths_to_remove = filter_by_likelihood(df, "common_likelihood", common_to_filter, threshold)
    p_len = len(paths_to_remove)
    commons = " ".join(common_to_filter)
    if p_len > 0:
        print(f"Removing {p_len} paths with {commons}")
        for path in paths_to_remove:
            path = os.path.join(os.getcwd(), paths_to_remove[0][1:])
            os.remove(path)


def sum_common_likelihood(df_group, common_names):
    """gets the likelihood count of a list of detected common names in an image.

    Args:
        df_group ([type]): detection rows for a single image. a dataframe subset
        common_names ([type]): list of common names ["hare", "rabbit", "jackrabbit"] for example. or ["sheep"]

    Returns:
        [type]: [description]
    """
    is_common = [False] * len(df_group)
    for name in common_names:
        is_common_r = df_group.loc[:, "common"].str.contains(name)
        is_common = [a or b for a, b in zip(is_common, is_common_r)]
    return df_group.likelihood[is_common].sum()


def filter_by_likelihood(df, cname, common_names, threshold):
    """Filters imgs by likelihood of common_names appearing.

    Args:
        cname ([type]): Name of the likelihood column
        common_names ([type]): common names
        threshold ([type]): likelihood threshold

    Returns:
        [type]: df with images without classes in common names.
    """

    likelihood = df.groupby("path").apply(lambda x: sum_common_likelihood(x, common_names))

    df = df.set_index("path")

    return likelihood[likelihood > threshold].index.tolist()


if __name__ == "__main__":
    main()

