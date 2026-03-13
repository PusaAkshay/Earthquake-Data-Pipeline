from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.types import *


bronze_read_path  = "abfss://bronze@adlsearthquake.dfs.core.windows.net/earthquake_data/"


properties_schema = StructType([
    StructField("mag",     DoubleType(),  True),
    StructField("place",   StringType(),  True),
    StructField("time",    LongType(),    True),
    StructField("updated", LongType(),    True),
    StructField("tsunami", IntegerType(), True),
    StructField("sig",     IntegerType(), True),
    StructField("status",  StringType(),  True),
    StructField("alert",   StringType(),  True),
    StructField("magType", StringType(),  True),
    StructField("title",   StringType(),  True),
    StructField("type",    StringType(),  True)
])

geometry_schema = StructType([
    StructField("coordinates", ArrayType(DoubleType()))
])

@dp.table(name="bronze_earthquakes")
@dp.expect_all_or_drop({"rule_1": "earthquake_id IS NOT NULL"})
def bronze_earthquakes():
    df = spark.readStream \
        .format("delta") \
        .load(bronze_read_path) \
        .withColumn("_load_timestamp", current_timestamp())

    df = df.withColumn("props", from_json(col("properties"), properties_schema)) \
           .withColumn("geo",   from_json(col("geometry"),   geometry_schema))

    df = df.select(
        col("id").alias("earthquake_id"),
        col("props.mag").alias("magnitude"),
        col("props.place").alias("place"),
        col("props.title").alias("title"),
        col("props.status").alias("status"),
        col("props.alert").alias("alert"),
        col("props.magType").alias("magnitude_type"),
        col("props.tsunami").cast("integer").alias("tsunami_flag"),
        col("props.sig").cast("integer").alias("significance"),
        col("props.type").alias("event_type"),
        (col("props.time") / 1000).cast(TimestampType()).alias("event_time"),
        (col("props.updated") / 1000).cast(TimestampType()).alias("updated_time"),
        col("geo.coordinates")[0].alias("longitude"),
        col("geo.coordinates")[1].alias("latitude"),
        col("geo.coordinates")[2].alias("depth_km"),
        col("_load_timestamp")
    )

    df = df.filter(col("earthquake_id").isNotNull())
    return df


silver_rules = {
    "rule_1": "earthquake_id IS NOT NULL",
    "rule_2": "magnitude IS NOT NULL",
    "rule_3": "latitude IS NOT NULL"
}

@dp.table(
    name="silver_earthquakes",

)
@dp.expect_all_or_drop(silver_rules)
def silver_earthquakes():
    df = dp.read_stream("bronze_earthquakes")
    return df


gold_rules = {
    "rule_1": "earthquake_id IS NOT NULL"
}

@dp.table(
    name="gold_earthquakes",

)
@dp.expect_all_or_drop(gold_rules)
def gold_earthquakes():
    df = dp.read("silver_earthquakes")

    df = df.dropDuplicates(["earthquake_id"])

    df = df.withColumn("magnitude_category",
        when(col("magnitude") >= 7.0, lit("Major"))
        .when(col("magnitude") >= 5.0, lit("Moderate"))
        .when(col("magnitude") >= 3.0, lit("Minor"))
        .otherwise(lit("Micro"))
    ) \
    .withColumn("tsunami_risk",
        when(col("tsunami_flag") == 1, lit("Yes"))
        .otherwise(lit("No"))
    ) \
    .withColumn("depth_category",
        when(col("depth_km") <= 70,   lit("Shallow"))
        .when(col("depth_km") <= 300, lit("Intermediate"))
        .otherwise(lit("Deep"))
    ) \
    .withColumn("alert_level",
        when(col("alert").isNull(), lit("Green"))
        .otherwise(upper(col("alert")))
    )

    return df
