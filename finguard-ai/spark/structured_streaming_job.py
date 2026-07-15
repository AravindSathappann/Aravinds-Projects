from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, count
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    MapType
)


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CALL_RISK_TOPIC = "call_risk_events"


event_schema = StructType([
    StructField("event_id", StringType()),
    StructField("event_time", StringType()),
    StructField("transcript", StringType()),
    StructField("ml_prediction", StringType()),
    StructField("final_prediction", StringType()),
    StructField("decision_reason", StringType()),
    StructField("retrieved_policy", StringType()),
    StructField("policy_file", StringType()),
    StructField("policy_similarity_score", DoubleType()),
    StructField("recommended_action", StringType()),
    StructField("manual_features", MapType(StringType(), DoubleType()))
])


def main():
    spark = (
        SparkSession.builder
        .appName("FinGuardAIStreaming")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    raw_events = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", CALL_RISK_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_events = (
        raw_events
        .selectExpr("CAST(value AS STRING) as json_value")
        .select(from_json(col("json_value"), event_schema).alias("event"))
        .select("event.*")
    )

    risk_counts = (
        parsed_events
        .groupBy("final_prediction")
        .agg(count("*").alias("call_count"))
    )

    query = (
        risk_counts
        .writeStream
        .outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
