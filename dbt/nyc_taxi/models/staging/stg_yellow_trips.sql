with source as (
    select * from {{ source('raw', 'tlc_yellow_trips_2022') }}
),

renamed as (
    select
        vendor_id,
        pickup_datetime,
        dropoff_datetime,
        passenger_count,
        trip_distance,
        rate_code,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        imp_surcharge,
        airport_fee,
        total_amount,
        cast(pickup_location_id as integer) as pickup_location_id,
        cast(dropoff_location_id as integer) as dropoff_location_id,
        data_file_year,
        data_file_month
    from source
    where fare_amount > 0
      and trip_distance > 0
      and passenger_count > 0
      and pickup_datetime is not null
      and dropoff_datetime is not null
)

select * from renamed