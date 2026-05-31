import great_expectations as gx
from google.cloud import bigquery
import os

PROJECT = "nyc-taxi-platform-2026"
DATASET = "raw"
TABLE = "tlc_yellow_trips_2022"
SAMPLE_SIZE = 500000

def fetch_sample(client):
    query = f"""
        SELECT
            pickup_datetime,
            dropoff_datetime,
            fare_amount,
            trip_distance,
            total_amount,
            passenger_count,
            payment_type
        FROM `{PROJECT}.{DATASET}.{TABLE}`
        LIMIT {SAMPLE_SIZE}
    """
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    return df

def run_validation(df):
    context = gx.get_context()

    datasource = context.sources.add_pandas("nyc_taxi_raw")
    asset = datasource.add_dataframe_asset("raw_sample")
    batch_request = asset.build_batch_request(dataframe=df)

    suite_name = "raw_taxi_suite"
    context.add_or_update_expectation_suite(suite_name)

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    validator.expect_table_row_count_to_be_between(min_value=400000, max_value=600000)

    validator.expect_column_values_to_not_be_null("pickup_datetime")
    validator.expect_column_values_to_not_be_null("dropoff_datetime")
    validator.expect_column_values_to_not_be_null("fare_amount")
    validator.expect_column_values_to_not_be_null("trip_distance")
    validator.expect_column_values_to_not_be_null("total_amount")
    validator.expect_column_values_to_not_be_null("passenger_count")

    validator.expect_column_values_to_be_between("fare_amount", min_value=0, max_value=500)
    validator.expect_column_values_to_be_between("trip_distance", min_value=0, max_value=100)
    validator.expect_column_values_to_be_between("total_amount", min_value=0, max_value=500)
    validator.expect_column_values_to_be_between("passenger_count", min_value=1, max_value=9)

    validator.expect_column_values_to_be_in_set(
        "payment_type", [1, 2, 3, 4, 5, 6]
    )

    validator.save_expectation_suite()

    checkpoint = context.add_or_update_checkpoint(
        name="raw_checkpoint",
        validator=validator,
    )

    result = checkpoint.run()

    context.open_data_docs()

    if result.success:
        print("Validation passed")
    else:
        print("Validation failed -- check Data Docs for details")

if __name__ == "__main__":
    client = bigquery.Client(project=PROJECT)
    df = fetch_sample(client)
    print(f"Fetched {len(df)} rows")
    run_validation(df)