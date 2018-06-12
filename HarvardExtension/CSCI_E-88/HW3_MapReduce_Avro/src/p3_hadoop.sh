input_dir=/e88/A3/p2_input
output_dir=/e88/A3/p3_output
hdfs dfs -rmr $output_dir

jars="avro-1.8.2.jar,avro-mapred-1.8.2-hadoop1.jar"

STREAM_JAR=hadoop-streaming

$STREAM_JAR \
    -D mapred.reduce.tasks=1  \
    -files  $jars \
    -libjars $jars \
    -mapper "$PWD/p3_mapper.py" \
    -reducer "$PWD/p3_reducer.py" \
    -input "$input_dir/1_input.log" \
    -output "$output_dir"  \
    -file "$PWD/p3_mapper.py" \
    -file "$PWD/p3_reducer.py" \
    -outputformat org.apache.avro.mapred.AvroTextOutputFormat
