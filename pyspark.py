from pyspark.sql import SparkSession

#1. Create a Spark session
print("1. Create a Spark session")
spark = SparkSession.builder \
    .appName("PySpark Example") \
    .getOrCreate()

print("Spark Session Created")

#2. Working with DataFrames
print("2. Working with DataFrames")

data = [("Alice", 25), ("Bob", 30), ("Cathy", 28)]
columns = ["Name", "Age"]

df = spark.createDataFrame(data, columns)
df.show()

#3. Common DataFrame Operations
print("3. Common DataFrame Operations")
df.filter(df.Age > 26).show() #Filter Rows
df.select("Name").show() #Select Specific Columns
df.withColumn("Age After 5 Years", df.Age + 5).show() #Add a New Column


### Group and Aggregate ####
newData = [("Alice", "Math", 85), ("Alice", "Science", 95), 
        ("Bob", "Math", 65), ("Bob", "Science", 78)]
columns = ["Name", "Subject", "Score"]

df = spark.createDataFrame(newData, columns)

# Group by Name and calculate average score 
df.groupBy("Name").avg("Score").show()

1. Create a Spark session
Spark Session Created
2. Working with DataFrames
+-----+---+
| Name|Age|
+-----+---+
|Alice| 25|
|  Bob| 30|
|Cathy| 28|
+-----+---+

3. Common DataFrame Operations
+-----+---+
| Name|Age|
+-----+---+
|  Bob| 30|
|Cathy| 28|
+-----+---+

+-----+
| Name|
+-----+
|Alice|
|  Bob|
|Cathy|
+-----+

+-----+---+-----------------+
| Name|Age|Age After 5 Years|
+-----+---+-----------------+
|Alice| 25|               30|
|  Bob| 30|               35|
|Cathy| 28|               33|
+-----+---+-----------------+

+-----+----------+
| Name|avg(Score)|
+-----+----------+
|Alice|      90.0|
|  Bob|      71.5|
+-----+----------+

