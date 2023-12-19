"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")  
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    augmented_dep = pd.merge(departments,
                             regions,
                             how='left',
                             left_on='region_code',
                             right_on='code').drop(['id_x', 'id_y', 'code_y', 'slug_x', 'slug_y'], axis=1)
    augmented_dep = augmented_dep.rename(columns={"region_code": "code_reg",\
        "code_x": "code_dep", "name_x": "name_dep", "name_y": "name_reg"})
    return augmented_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    augmented_ref = pd.merge(referendum[referendum['Department code'].str.isnumeric()],
                            regions_and_departments, how='left', left_on='Department code',
                            right_on='code_dep').drop(['code_dep', 'name_dep'], axis=1)
    return augmented_ref


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    aggregated_data = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',  # Assuming 'name_reg' is the same for each 'code_reg'
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })

    # Reorder columns as specified
    columns_order = ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    aggregated_data = aggregated_data[columns_order]

    return aggregated_data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load geographic data
    geo_data = gpd.read_file('data/regions.geojson')
    # Merge the referendum results with the geographic data
    merged_data = geo_data.merge(referendum_result_by_regions, left_on='code', right_on='code_reg')

    # Calculate the ratio of 'Choice A' over all expressed ballots (excluding abstentions and null votes)
    expressed_ballots = merged_data['Registered'] - merged_data['Abstentions'] - merged_data['Null']
    merged_data['ratio'] = merged_data['Choice A'] / expressed_ballots

    # Plotting the map
    merged_data.plot(column='ratio', legend=True, figsize=(10, 6))

    return merged_data



if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
