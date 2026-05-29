with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),

enriched as (
    select
        pickup_datetime,
        dropoff_datetime,
        date(pickup_datetime) as trip_date,
        extract(hour from pickup_datetime) as pickup_hour,
        pickup_location_id,
        dropoff_location_id,
        passenger_count,
        trip_distance,
        fare_amount,
        tip_amount,
        tolls_amount,
        total_amount,
        payment_type,
        timestamp_diff(dropoff_datetime, pickup_datetime, minute) as trip_duration_minutes
    from trips
    where dropoff_datetime > pickup_datetime
      and timestamp_diff(dropoff_datetime, pickup_datetime, minute) between 1 and 180
      and trip_distance <= 100
      and total_amount <= 500
)

select * from enriched