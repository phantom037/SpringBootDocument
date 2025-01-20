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


data = [("Messi", 10, "FC Barcelona", "Argentina"), ("Neymar", 11, "FC Barcelona", "Brazil"), ("Suarez", 9, "FC Barcelona", "Uruguay"), ("Iniesta", 8, "FC Barcelona", "Spain"),
        ("Ronaldo", 10, "Real Madrid", "Portugual"), ("Pepe", 3, "Real Madrid", "Portugual"), ("Kroos", 8, "Real Madrid", "Germany"), ("Ramos", 4, "Real Madrid", "Spain"),
        ("Reus", 11, "Dortmund", "Germany"), ("Neuer", 1, "Bayern Munich", "Germany"), ("De Paul", 4, "Athletico", "Argentina"), ("Xavi", 6, "FC Barcelona", "Spain")]

columns = ["Name", "Number", "Club", "Country"]

df = spark.createDataFrame(data, columns)
df.show()

df.filter((df.Number > 5) & (df.Country == "Germany")).show()


### Group and Aggregate ####
newData = [("Alice", "Math", 85), ("Alice", "Science", 95), 
        ("Bob", "Math", 65), ("Bob", "Science", 78)]
columns = ["Name", "Subject", "Score"]

df = spark.createDataFrame(newData, columns)

# Group by Name and calculate average score 
df.groupBy("Name").avg("Score").show()


#4. Read and Write Data
df = spark.read.csv("path/to/your/file.csv", header=True, inferSchema=True)
df.show()

df.write.csv("path/to/save/output.csv", header=True)



#5. Register the DataFrame as a SQL temporary view
df.createOrReplaceTempView("people")

# Run SQL queries
result = spark.sql("SELECT * FROM people WHERE Age > 26")
result.show()


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

